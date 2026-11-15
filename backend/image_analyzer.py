import io
import base64
from typing import Optional, Tuple
from PIL import Image
import config
from backend.gemini_service import gemini_service

MAX_IMAGE_DIMENSION = 1024

def validate_image(file_bytes: bytes, content_type: str) -> Tuple[bool, str]:
    if content_type not in config.ALLOWED_IMAGE_TYPES:
        return False, f"Unsupported image format. Allowed: JPG, JPEG, PNG, WEBP"
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > config.MAX_IMAGE_SIZE_MB:
        return False, f"Image too large ({size_mb:.1f}MB). Maximum: {config.MAX_IMAGE_SIZE_MB}MB"
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
        return True, "Valid image"
    except Exception:
        return False, "Invalid or corrupted image file"

def resize_image(file_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(file_bytes))
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    w, h = img.size
    if max(w, h) > MAX_IMAGE_DIMENSION:
        ratio = MAX_IMAGE_DIMENSION / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return buf.getvalue()

class ImageAnalyzer:
    async def analyze_food_image(self, image_bytes: bytes, mime_type: str, user_message: str = "") -> str:
        prompt = (
            "Analyze this food image in detail. Provide:\n"
            "1. **Food Name**: Identify the food items visible\n"
            "2. **Visible Ingredients**: List recognizable ingredients\n"
            "3. **Approximate Portion**: Describe the portion size\n"
            "4. **Estimated Nutritional Information**:\n"
            "   - Calories (approximate range)\n"
            "   - Protein (grams)\n"
            "   - Carbohydrates (grams)\n"
            "   - Fat (grams)\n"
            "5. **Health Assessment**: Is this meal healthy? Why or why not?\n"
            "6. **Suggestions**: How to make it healthier\n\n"
            "⚠️ Note: These are visual estimates and may not be accurate. "
            "For precise nutrition information, use verified food databases or consult a nutritionist."
        )
        if user_message:
            prompt += f"\n\nUser's question: {user_message}"
        
        resized = resize_image(image_bytes)
        return await gemini_service.generate_response(
            prompt=prompt,
            image_data=resized,
            image_mime_type="image/jpeg"
        )

    async def analyze_nutrition_label(self, image_bytes: bytes, mime_type: str, user_message: str = "") -> str:
        prompt = (
            "Analyze this nutrition label image. Extract and present:\n"
            "1. **Product Name** (if visible)\n"
            "2. **Serving Size**\n"
            "3. **Calories**\n"
            "4. **Macronutrients**: Protein, Carbs, Fat\n"
            "5. **Other Nutrients**: Sugar, Sodium, Fiber, etc.\n"
            "6. **Ingredients** (if visible)\n"
            "7. **Health Assessment**: Comment on the nutritional profile\n"
            "8. **Recommendations**: Suggestions for healthier alternatives if applicable\n\n"
            "If any information is unreadable, mention it clearly."
        )
        if user_message:
            prompt += f"\n\nUser's question: {user_message}"
        
        resized = resize_image(image_bytes)
        return await gemini_service.generate_response(
            prompt=prompt,
            image_data=resized,
            image_mime_type="image/jpeg"
        )

    async def analyze_workout_image(self, image_bytes: bytes, mime_type: str, user_message: str = "") -> str:
        prompt = (
            "Analyze this workout/exercise image. Explain:\n"
            "1. **Exercise(s) Shown**: Name and type\n"
            "2. **Muscle Groups Targeted**\n"
            "3. **Sets & Reps** (if visible)\n"
            "4. **Schedule/Duration** (if visible)\n"
            "5. **Proper Form Tips**\n"
            "6. **Safety Considerations**\n"
            "7. **Modifications**: Easier and harder variations\n\n"
            "If information is missing or unclear, mention it."
        )
        if user_message:
            prompt += f"\n\nUser's question: {user_message}"
        
        resized = resize_image(image_bytes)
        return await gemini_service.generate_response(
            prompt=prompt,
            image_data=resized,
            image_mime_type="image/jpeg"
        )

    async def analyze_general_image(self, image_bytes: bytes, mime_type: str, user_message: str = "") -> str:
        prompt = (
            "Analyze this health or fitness related image. "
            "Describe what you see and provide relevant health and fitness information, "
            "explanations, and practical advice. "
            "If this appears to be a medical document or report, explain the readable "
            "information and terminology without diagnosing the user. "
            "Recommend consulting a healthcare professional for medical interpretation."
        )
        if user_message:
            prompt += f"\n\nUser's question: {user_message}"
        
        resized = resize_image(image_bytes)
        return await gemini_service.generate_response(
            prompt=prompt,
            image_data=resized,
            image_mime_type="image/jpeg"
        )

# Singleton
image_analyzer = ImageAnalyzer()
