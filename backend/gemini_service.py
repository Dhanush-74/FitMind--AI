import base64
import io
from typing import Optional, List, Dict, Any
from PIL import Image
from google import genai
from google.genai import types
import config

SYSTEM_INSTRUCTION = (
    "You are FitMind AI, an intelligent personal health and fitness coach. "
    "You provide helpful, accurate, and well-structured responses about health, fitness, "
    "nutrition, workouts, wellness, yoga, meditation, sleep, hydration, and healthy lifestyle habits. "
    "Use markdown formatting with headings (##, ###), bullet points, numbered lists, bold text, "
    "and tables when appropriate to make responses clear and readable. "
    "Always prioritize user safety. For serious medical symptoms, recommend consulting a healthcare professional. "
    "For emergencies, advise seeking immediate medical help. "
    "Never diagnose medical conditions, prescribe medications, or recommend dangerous practices. "
    "Clearly state when nutritional estimates are approximate. "
    "Keep responses conversational, encouraging, and supportive."
)

class GeminiService:
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.client = None
        self.model = config.GEMINI_MODEL
        self._initialize()

    def _initialize(self):
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY not set. AI features will be unavailable.")
            return
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            print(f"Failed to initialize Gemini client: {e}")
            self.client = None

    def is_available(self) -> bool:
        return self.client is not None

    async def generate_response(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        image_data: Optional[bytes] = None,
        image_mime_type: Optional[str] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        if not self.is_available():
            return "⚠️ AI service is not configured. Please set your GEMINI_API_KEY in the .env file."

        try:
            sys_instruction = system_instruction or SYSTEM_INSTRUCTION
            contents = []

            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-20:]:  # Last 20 messages for context
                    role = "user" if msg.get("role") == "user" else "model"
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=msg["content"])]
                        )
                    )

            # Build current message parts
            parts = []

            if image_data:
                mime = image_mime_type or "image/jpeg"
                parts.append(types.Part.from_bytes(data=image_data, mime_type=mime))

            parts.append(types.Part.from_text(text=prompt))
            contents.append(types.Content(role="user", parts=parts))

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruction,
                    temperature=temperature,
                    max_output_tokens=8192,
                ),
            )

            if response and response.text:
                return response.text.strip()
            return "I couldn't generate a response. Please try again."

        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "rate" in error_str or "429" in error_str:
                return "⚠️ API rate limit reached. Please wait a moment and try again."
            elif "invalid" in error_str or "api key" in error_str or "401" in error_str or "403" in error_str:
                return "⚠️ Invalid API key. Please check your GEMINI_API_KEY in the .env file."
            elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
                return "⚠️ Network error. Please check your internet connection and try again."
            else:
                print(f"Gemini API error: {e}")
                return f"⚠️ An error occurred while generating a response. Please try again."

    def health_check(self) -> Dict[str, Any]:
        if not self.is_available():
            return {"status": "unavailable", "message": "API key not configured"}
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents="Say OK",
                config=types.GenerateContentConfig(max_output_tokens=10),
            )
            return {"status": "healthy", "message": "Gemini API is working"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Singleton instance
gemini_service = GeminiService()
