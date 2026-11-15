from typing import Optional, Dict, List, Any
from backend.gemini_service import gemini_service
from backend.domain_detector import domain_detector
from backend.safety_service import safety_service
from backend.conversation_manager import conversation_manager
from backend.image_analyzer import image_analyzer
from backend.document_processor import document_processor
from backend.rag_pipeline import rag_pipeline

class ChatService:
    async def process_message(
        self, message: str, conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # Create conversation if needed
        if not conversation_id:
            conv = conversation_manager.create_conversation()
            conversation_id = conv["id"]
            is_new = True
        else:
            is_new = False
        
        # Get conversation history
        history = conversation_manager.get_conversation_history(conversation_id)
        
        # Check for emergency
        emergency = safety_service.check_emergency(message)
        if emergency:
            conversation_manager.add_message(conversation_id, "user", message)
            conversation_manager.add_message(conversation_id, "assistant", emergency)
            if is_new:
                conversation_manager.auto_title(conversation_id, message)
            return {
                "response": emergency,
                "conversation_id": conversation_id,
                "is_new": is_new,
            }
        
        # Domain check
        if not domain_detector.is_health_fitness_related(message, history):
            rejection = domain_detector.get_rejection_message()
            conversation_manager.add_message(conversation_id, "user", message)
            conversation_manager.add_message(conversation_id, "assistant", rejection)
            if is_new:
                conversation_manager.auto_title(conversation_id, message)
            return {
                "response": rejection,
                "conversation_id": conversation_id,
                "is_new": is_new,
            }
        
        # Add safety context to prompt
        enhanced_prompt = safety_service.add_safety_context(message, message)
        
        # Save user message
        conversation_manager.add_message(conversation_id, "user", message)
        
        # Generate AI response
        response = await gemini_service.generate_response(
            prompt=enhanced_prompt,
            conversation_history=history,
        )
        
        # Add safety disclaimer if medical
        if safety_service.check_medical_diagnosis(message):
            response += safety_service.get_medical_disclaimer()
        
        # Save AI response
        conversation_manager.add_message(conversation_id, "assistant", response)
        
        # Auto-title new conversations
        if is_new:
            conversation_manager.auto_title(conversation_id, message)
        
        return {
            "response": response,
            "conversation_id": conversation_id,
            "is_new": is_new,
        }

    async def process_image(
        self, image_bytes: bytes, mime_type: str,
        user_message: str = "", conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if not conversation_id:
            conv = conversation_manager.create_conversation()
            conversation_id = conv["id"]
            is_new = True
        else:
            is_new = False
        
        # Save user message
        msg = user_message or "Uploaded an image for analysis"
        conversation_manager.add_message(conversation_id, "user", msg, "image")
        
        # Try to detect image type and analyze
        prompt = user_message or "Analyze this image"
        prompt_lower = prompt.lower()
        
        if any(w in prompt_lower for w in ["nutrition label", "label", "packaging", "ingredients list"]):
            response = await image_analyzer.analyze_nutrition_label(image_bytes, mime_type, user_message)
        elif any(w in prompt_lower for w in ["workout", "exercise", "routine", "training plan", "schedule"]):
            response = await image_analyzer.analyze_workout_image(image_bytes, mime_type, user_message)
        elif any(w in prompt_lower for w in ["food", "meal", "dish", "breakfast", "lunch", "dinner", "snack", "eat", "calorie"]):
            response = await image_analyzer.analyze_food_image(image_bytes, mime_type, user_message)
        else:
            # Let Gemini analyze general health/fitness image
            response = await image_analyzer.analyze_general_image(image_bytes, mime_type, user_message)
        
        conversation_manager.add_message(conversation_id, "assistant", response)
        
        if is_new:
            title = user_message[:50] if user_message else "Image Analysis"
            conversation_manager.update_conversation(conversation_id, title)
        
        return {
            "response": response,
            "conversation_id": conversation_id,
            "is_new": is_new,
        }

    async def process_document(
        self, file_bytes: bytes, filename: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if not conversation_id:
            conv = conversation_manager.create_conversation()
            conversation_id = conv["id"]
            is_new = True
        else:
            is_new = False
        
        conversation_manager.add_message(
            conversation_id, "user", f"Uploaded document: {filename}", "document", filename
        )
        
        # Process through RAG pipeline
        result = await rag_pipeline.process_document(file_bytes, filename, conversation_id)
        
        if result.get("success"):
            # Save document reference
            conversation_manager.add_document(
                conversation_id, result["doc_id"], filename,
                filename.split('.')[-1], len(file_bytes),
                result.get("preview", ""), result.get("pages", 0)
            )
            
            response = (
                f"📄 **Document Uploaded Successfully**\n\n"
                f"**File:** {filename}\n"
                f"**Pages:** {result.get('pages', 'N/A')}\n"
                f"**Chunks Created:** {result.get('chunks', 0)}\n\n"
                f"**Summary:**\n{result.get('summary', 'Processing...')}\n\n"
                f"You can now ask me questions about this document!"
            )
            
            conversation_manager.add_message(conversation_id, "assistant", response)
            
            if is_new:
                conversation_manager.update_conversation(conversation_id, f"📄 {filename}")
            
            return {
                "response": response,
                "conversation_id": conversation_id,
                "doc_id": result["doc_id"],
                "is_new": is_new,
                "success": True,
            }
        else:
            error_msg = f"❌ Failed to process document: {result.get('error', 'Unknown error')}"
            conversation_manager.add_message(conversation_id, "assistant", error_msg)
            return {
                "response": error_msg,
                "conversation_id": conversation_id,
                "is_new": is_new,
                "success": False,
            }

    async def answer_document_question(
        self, question: str, conversation_id: str,
        doc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        conversation_manager.add_message(conversation_id, "user", question)
        
        response = await rag_pipeline.answer_question(question, conversation_id, doc_id)
        conversation_manager.add_message(conversation_id, "assistant", response)
        
        return {
            "response": response,
            "conversation_id": conversation_id,
        }

# Singleton
chat_service = ChatService()
