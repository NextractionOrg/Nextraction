"""
Evaluation script for NexTraction Web RAG Pipeline

This script demonstrates example questions and evaluates citation quality.
Run after ingesting content with a job_id.
"""

import requests
import json
from typing import List, Dict
from datetime import datetime

BASE_URL = "http://localhost:8000"


def evaluate_question(job_id: str, question: str) -> Dict:
    """Ask a question and evaluate the response"""
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}")
    
    response = requests.post(
        f"{BASE_URL}/ask",
        json={"job_id": job_id, "question": question}
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    result = response.json()
    
    print(f"\nAnswer:")
    print(f"{result['answer']}\n")
    
    print(f"Confidence: {result['confidence']}")
    print(f"Grounding Notes: {result['groundingnotes']}\n")
    
    print(f"Citations ({len(result['citations'])}):")
    for i, citation in enumerate(result['citations'], 1):
        print(f"\n  [{i}] {citation['title']}")
        print(f"      URL: {citation['url']}")
        print(f"      Score: {citation['score']:.3f}")
        print(f"      Quote: {citation['quote'][:100]}...")
    
    # Evaluation metrics
    metrics = {
        "has_answer": bool(result['answer']),
        "has_citations": len(result['citations']) > 0,
        "citation_count": len(result['citations']),
        "confidence": result['confidence'],
        "avg_citation_score": (
            sum(c['score'] for c in result['citations']) / len(result['citations'])
            if result['citations'] else 0
        ),
        "answer_length": len(result['answer']),
    }
    
    print(f"\nMetrics:")
    print(f"  Has Answer: {metrics['has_answer']}")
    print(f"  Has Citations: {metrics['has_citations']}")
    print(f"  Citation Count: {metrics['citation_count']}")
    print(f"  Average Citation Score: {metrics['avg_citation_score']:.3f}")
    print(f"  Answer Length: {metrics['answer_length']} chars")
    
    return {
        "question": question,
        "result": result,
        "metrics": metrics
    }


def main():
    """Run evaluation on example questions"""
    print("NexTraction Web RAG Pipeline - Evaluation Script")
    print("=" * 60)
    
    # Get job_id from user or use default
    job_id = input("\nEnter job_id (or press Enter to use 'test'): ").strip()
    if not job_id:
        job_id = "test"
    
    # Check if job exists and is done
    status_response = requests.get(f"{BASE_URL}/status/{job_id}")
    if status_response.status_code != 200:
        print(f"Error: Job {job_id} not found")
        return
    
    status = status_response.json()
    print(f"\nJob Status: {status['state']}")
    print(f"Pages Fetched: {status['pages_fetched']}")
    print(f"Pages Indexed: {status['pages_indexed']}")
    
    if status['state'] != 'done':
        print(f"\nWarning: Job is not done (state: {status['state']})")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            return
    
    # Example questions
    questions = [
        "What is the main topic of this website?",
        "What are the key features mentioned?",
        "Who is the target audience?",
        "What are the main benefits?",
        "Are there any limitations or drawbacks mentioned?",
        "What is the pricing model?",
        "Who are the competitors?",
        "What technology stack is used?",
        "What is the company's mission?",
        "What are the contact details?",
    ]
    
    print(f"\n{'='*60}")
    print(f"Running evaluation on {len(questions)} questions")
    print(f"{'='*60}")
    
    results = []
    for question in questions:
        try:
            result = evaluate_question(job_id, question)
            if result:
                results.append(result)
        except Exception as e:
            print(f"\nError evaluating question: {str(e)}")
            continue
    
    # Summary statistics
    print(f"\n{'='*60}")
    print("Summary Statistics")
    print(f"{'='*60}")
    
    if results:
        total_questions = len(results)
        questions_with_answers = sum(1 for r in results if r['metrics']['has_answer'])
        questions_with_citations = sum(1 for r in results if r['metrics']['has_citations'])
        avg_citations = sum(r['metrics']['citation_count'] for r in results) / total_questions
        avg_score = sum(r['metrics']['avg_citation_score'] for r in results) / total_questions
        
        confidence_dist = {}
        for r in results:
            conf = r['metrics']['confidence']
            confidence_dist[conf] = confidence_dist.get(conf, 0) + 1
        
        print(f"\nTotal Questions: {total_questions}")
        print(f"Questions with Answers: {questions_with_answers} ({100*questions_with_answers/total_questions:.1f}%)")
        print(f"Questions with Citations: {questions_with_citations} ({100*questions_with_citations/total_questions:.1f}%)")
        print(f"Average Citations per Answer: {avg_citations:.2f}")
        print(f"Average Citation Score: {avg_score:.3f}")
        print(f"\nConfidence Distribution:")
        for conf, count in confidence_dist.items():
            print(f"  {conf}: {count} ({100*count/total_questions:.1f}%)")
        
        # Save results
        output_file = f"evaluation_results_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_file}")
    else:
        print("\nNo results to summarize")


if __name__ == "__main__":
    main()

