import uuid
from typing import List, Dict, Optional
import config
from backend.vector_store import vector_store
from backend.document_processor import document_processor
from backend.gemini_service import gemini_service

class RAGPipeline:
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
        self.top_k = config.TOP_K_RESULTS

    def chunk_text(self, text: str, page_data: Optional[List[Dict]] = None) -> List[Dict[str, str]]:
        chunks = []
        if page_data:
            for page_info in page_data:
                page_text = page_info["text"]
                page_num = page_info["page"]
                page_chunks = self._split_text(page_text)
                for chunk in page_chunks:
                    chunks.append({
                        "text": chunk,
                        "page": str(page_num),
                        "source": f"Page {page_num}"
                    })
        else:
            text_chunks = self._split_text(text)
            for i, chunk in enumerate(text_chunks):
                chunks.append({
                    "text": chunk,
                    "page": str(i + 1),
                    "source": f"Section {i + 1}"
                })
        return chunks

    def _split_text(self, text: str) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            if end < len(text):
                # Try to break at a paragraph or sentence boundary
                for sep in ['\n\n', '\n', '. ', '! ', '? ']:
                    last_sep = text[start:end].rfind(sep)
                    if last_sep > self.chunk_size // 2:
                        end = start + last_sep + len(sep)
                        break
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        return chunks

    async def process_document(
        self, file_bytes: bytes, filename: str, conversation_id: str
    ) -> Dict:
        # Extract text
        extraction = document_processor.extract_text(file_bytes, filename)
        if extraction.get("error"):
            return {"success": False, "error": extraction["error"]}
        
        text = extraction["text"]
        if not text.strip():
            return {"success": False, "error": "No text content found in document"}
        
        # Create chunks
        page_data = extraction.get("page_data")
        chunks = self.chunk_text(text, page_data)
        if not chunks:
            return {"success": False, "error": "Could not create text chunks from document"}
        
        # Create vector index
        doc_id = str(uuid.uuid4())
        index_id = f"{conversation_id}_{doc_id}"
        success = vector_store.create_index(index_id, chunks)
        
        if not success:
            return {"success": False, "error": "Failed to create document index"}
        
        # Generate summary using Gemini
        preview = text[:3000]
        summary_prompt = (
            f"Provide a brief summary of this document in 3-5 sentences. "
            f"Focus on the main topics and key points:\n\n{preview}"
        )
        summary = await gemini_service.generate_response(summary_prompt)
        
        return {
            "success": True,
            "doc_id": doc_id,
            "index_id": index_id,
            "filename": filename,
            "pages": extraction.get("pages", 0),
            "chunks": len(chunks),
            "preview": document_processor.get_preview(text),
            "summary": summary,
        }

    async def answer_question(
        self, question: str, conversation_id: str,
        doc_id: Optional[str] = None
    ) -> str:
        # Find relevant index
        index_id = None
        if doc_id:
            index_id = f"{conversation_id}_{doc_id}"
        else:
            # Search all indexes for this conversation
            for key in list(vector_store._stores.keys()):
                if key.startswith(f"{conversation_id}_"):
                    index_id = key
                    break
        
        if not index_id or not vector_store.has_index(index_id):
            return (
                "No documents found for this conversation. "
                "Please upload a PDF, DOCX, or TXT file first, then ask your question."
            )
        
        # Retrieve relevant chunks
        results = vector_store.search(index_id, question, self.top_k)
        if not results:
            return "I couldn't find relevant information in the document to answer your question."
        
        # Build context
        context_parts = []
        for r in results:
            source = r.get("source", "Unknown")
            context_parts.append(f"[{source}]: {r['text']}")
        context = "\n\n".join(context_parts)
        
        # Generate answer with Gemini
        prompt = (
            f"Based on the following document excerpts, answer the user's question. "
            f"Only use information from the provided context. "
            f"If the answer is not in the context, say so clearly. "
            f"Include page/section references when available.\n\n"
            f"DOCUMENT CONTEXT:\n{context}\n\n"
            f"USER QUESTION: {question}\n\n"
            f"Provide a clear, well-structured answer based on the document content."
        )
        return await gemini_service.generate_response(prompt)

# Singleton
rag_pipeline = RAGPipeline()
