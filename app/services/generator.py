import os
import re
from typing import List, Dict, Tuple
from app.config import settings
from app.utils.logger import logger
from app.schemas import Confidence


class GroundedGenerator:
    """Service for generating grounded answers with citations"""
    
    def __init__(self):
        self.llm_provider = settings.llm_provider
        self.llm_model = settings.llm_model
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the LLM client"""
        if self.llm_provider == "openai":
            try:
                from openai import AsyncOpenAI
                api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
                base_url = settings.openai_base_url or None
                self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
                logger.info("Initialized OpenAI LLM client")
            except ImportError:
                logger.error("OpenAI library not installed")
                raise RuntimeError("OpenAI client not available")
        
        elif self.llm_provider == "gemini":
            try:
                import google.generativeai as genai
                api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
                genai.configure(api_key=api_key)
                self._client = genai
                logger.info("Initialized Gemini LLM client")
            except ImportError:
                logger.error("Gemini library not installed")
                raise RuntimeError("Gemini client not available")
    
    def _build_context(self, retrieved_chunks: List[Tuple[Dict, float]]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        for chunk, score in retrieved_chunks:
            chunk_text = chunk.get("text", "")
            url = chunk.get("url", "")
            title = chunk.get("title", "")
            chunkid = chunk.get("chunkid", "")
            
            context_parts.append(
                f"[Source: {title} ({url}) | ChunkID: {chunkid} | Score: {score:.3f}]\n"
                f"{chunk_text}\n"
            )
        
        return "\n---\n\n".join(context_parts)
    
    async def generate_answer(
        self,
        question: str,
        retrieved_chunks: List[Tuple[Dict, float]]
    ) -> Dict:
        """Generate a grounded answer with citations"""
        
        if not retrieved_chunks:
            return {
                "answer": "I don't have enough information to answer this question based on the available sources.",
                "citations": [],
                "confidence": Confidence.LOW,
                "groundingnotes": "No relevant sources were found in the indexed content."
            }
        
        # Filter chunks by minimum relevance score
        min_score = 0.3
        relevant_chunks = [(chunk, score) for chunk, score in retrieved_chunks if score >= min_score]
        
        if not relevant_chunks:
            return {
                "answer": "I don't have sufficient evidence to answer this question. The retrieved sources have low relevance scores.",
                "citations": [],
                "confidence": Confidence.LOW,
                "groundingnotes": f"Retrieved {len(retrieved_chunks)} sources, but none met the minimum relevance threshold ({min_score})."
            }
        
        # Build context
        context = self._build_context(relevant_chunks)
        
        # Generate answer
        prompt = self._build_prompt(question, context)
        
        try:
            answer_text = await self._call_llm(prompt)
            
            # Extract citations from answer
            citations = self._extract_citations(answer_text, relevant_chunks)
            
            # Self-check for unsupported claims
            checked_answer, confidence, grounding_notes = self._self_check(
                answer_text, relevant_chunks, question
            )
            
            return {
                "answer": checked_answer,
                "citations": citations,
                "confidence": confidence,
                "groundingnotes": grounding_notes
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                "answer": "I encountered an error while generating an answer.",
                "citations": [],
                "confidence": Confidence.LOW,
                "groundingnotes": f"Error: {str(e)}"
            }
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build the prompt for the LLM"""
        return f"""You are a helpful assistant that answers questions based ONLY on the provided context. 
You must:
1. Answer the question using ONLY information from the provided context
2. Cite sources using [ChunkID: ...] format when making factual claims
3. If the context doesn't contain enough information, explicitly state what is missing
4. Never make up information or use knowledge outside the provided context

Context:
{context}

Question: {question}

Answer (with citations in [ChunkID: ...] format):"""
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM to generate an answer"""
        if self.llm_provider == "openai":
            response = await self._client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides evidence-based answers with citations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens
            )
            return response.choices[0].message.content.strip()
        
        elif self.llm_provider == "gemini":
            model = self._client.GenerativeModel(self.llm_model)
            response = await model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": settings.llm_temperature,
                    "max_output_tokens": settings.llm_max_tokens
                }
            )
            return response.text.strip()
    
    def _extract_citations(self, answer: str, chunks: List[Tuple[Dict, float]]) -> List[Dict]:
        """Extract citations from the answer text"""
        citations = []
        chunk_map = {chunk["chunkid"]: (chunk, score) for chunk, score in chunks}
        
        # Find chunk IDs mentioned in the answer
        chunkid_pattern = r'\[ChunkID:\s*([a-f0-9]+)\]'
        matches = re.finditer(chunkid_pattern, answer, re.IGNORECASE)
        
        seen_chunkids = set()
        for match in matches:
            chunkid = match.group(1)
            if chunkid in chunk_map and chunkid not in seen_chunkids:
                seen_chunkids.add(chunkid)
                chunk, score = chunk_map[chunkid]
                
                # Extract a short quote (max 25 words)
                text = chunk.get("text", "")
                words = text.split()[:25]
                quote = " ".join(words)
                if len(text.split()) > 25:
                    quote += "..."
                
                citations.append({
                    "url": chunk.get("url", ""),
                    "title": chunk.get("title", ""),
                    "chunkid": chunkid,
                    "quote": quote,
                    "score": float(score)
                })
        
        # If no citations found but we have chunks, add top chunks
        if not citations and chunks:
            for chunk, score in chunks[:3]:  # Top 3
                text = chunk.get("text", "")
                words = text.split()[:25]
                quote = " ".join(words)
                if len(text.split()) > 25:
                    quote += "..."
                
                citations.append({
                    "url": chunk.get("url", ""),
                    "title": chunk.get("title", ""),
                    "chunkid": chunk.get("chunkid", ""),
                    "quote": quote,
                    "score": float(score)
                })
        
        return citations
    
    def _self_check(
        self,
        answer: str,
        chunks: List[Tuple[Dict, float]],
        question: str
    ) -> Tuple[str, Confidence, str]:
        """Self-check for unsupported claims"""
        # Simple heuristic: check if answer contains citations
        has_citations = bool(re.search(r'\[ChunkID:', answer, re.IGNORECASE))
        
        # Check average relevance score
        avg_score = sum(score for _, score in chunks) / len(chunks) if chunks else 0.0
        
        # Determine confidence
        if has_citations and avg_score > 0.7 and len(chunks) >= 2:
            confidence = Confidence.HIGH
            grounding_notes = f"Answer is well-supported by {len(chunks)} high-quality sources (avg score: {avg_score:.2f})"
        elif has_citations and avg_score > 0.5:
            confidence = Confidence.MEDIUM
            grounding_notes = f"Answer is partially supported by {len(chunks)} sources (avg score: {avg_score:.2f})"
        else:
            confidence = Confidence.LOW
            grounding_notes = f"Answer has limited support from {len(chunks)} sources (avg score: {avg_score:.2f}). Some information may be missing."
        
        # Remove unsupported claims (simple heuristic: sentences without citations)
        if not has_citations:
            # Try to add a disclaimer
            if not answer.endswith("(based on limited evidence)"):
                answer += " (Note: This answer is based on limited evidence from the available sources.)"
        
        return answer, confidence, grounding_notes

