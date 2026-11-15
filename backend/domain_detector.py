import re
from typing import List, Dict, Optional

# Health & fitness related keyword categories
HEALTH_FITNESS_KEYWORDS = {
    "exercise": ["workout", "exercise", "training", "cardio", "strength", "squat", "deadlift",
        "bench press", "push up", "pushup", "pull up", "pullup", "plank", "burpee", "lunge",
        "crunch", "sit up", "jumping jack", "running", "jogging", "swimming", "cycling",
        "hiit", "crossfit", "bodyweight", "dumbbell", "barbell", "kettlebell", "resistance",
        "reps", "sets", "repetition", "gym", "treadmill", "elliptical", "rowing"],
    "nutrition": ["nutrition", "calorie", "calories", "protein", "carb", "carbohydrate",
        "fat", "fiber", "vitamin", "mineral", "macro", "micronutrient", "diet", "meal",
        "food", "eat", "eating", "breakfast", "lunch", "dinner", "snack", "recipe",
        "ingredient", "serving", "portion", "nutrient", "supplement", "whey",
        "creatine", "bcaa", "omega", "antioxidant", "superfood", "organic"],
    "health": ["health", "healthy", "wellness", "wellbeing", "medical", "doctor",
        "symptom", "blood pressure", "cholesterol", "diabetes", "bmi", "body mass",
        "heart rate", "metabolism", "immune", "inflammation", "disease", "condition",
        "therapy", "treatment", "prevention", "diagnosis", "checkup", "screening"],
    "fitness_goals": ["weight loss", "lose weight", "gain weight", "bulk", "cut", "lean",
        "muscle", "toning", "tone", "slim", "shred", "body fat", "six pack", "abs",
        "bicep", "tricep", "chest", "back", "shoulder", "leg", "core", "glute",
        "flexibility", "endurance", "stamina", "agility", "balance", "posture"],
    "yoga_meditation": ["yoga", "meditation", "mindfulness", "breathing", "pranayama",
        "asana", "stretching", "flexibility", "relaxation", "stress relief",
        "mental health", "anxiety", "calm", "peace", "zen", "chakra", "pilates"],
    "sleep_recovery": ["sleep", "rest", "recovery", "insomnia", "fatigue", "tired",
        "energy", "nap", "circadian", "melatonin", "rem", "deep sleep", "sleep quality",
        "overtraining", "muscle recovery", "soreness", "foam roll", "massage"],
    "hydration": ["water", "hydration", "hydrate", "dehydration", "fluid", "electrolyte",
        "drink", "beverage", "juice", "smoothie", "tea", "coffee"],
    "body_parts": ["arm", "leg", "chest", "back", "shoulder", "core", "abs", "glute",
        "hamstring", "quadricep", "calf", "forearm", "neck", "hip", "knee", "ankle",
        "wrist", "elbow", "spine", "lower back", "upper body", "lower body"],
    "equipment": ["dumbbell", "barbell", "kettlebell", "resistance band", "pull up bar",
        "bench", "rack", "cable", "machine", "mat", "foam roller", "jump rope",
        "treadmill", "bike", "elliptical", "rowing machine", "smith machine"],
}

GREETING_PATTERNS = [
    r"^(hi|hello|hey|howdy|greetings|good morning|good afternoon|good evening|sup|yo|hola)[\s!.,?]*$",
    r"^(what'?s up|how are you|how'?s it going|nice to meet you)[\s!.,?]*$",
    r"^(thanks|thank you|thx|ty|appreciate it|grateful)[\s!.,?]*$",
    r"^(bye|goodbye|see you|take care|later|cheers)[\s!.,?]*$",
    r"^(ok|okay|sure|got it|understood|alright|great|nice|cool|awesome|perfect)[\s!.,?]*$",
    r"^(help|help me|can you help me)[\s!.,?]*$",
]

OFF_TOPIC_INDICATORS = [
    "programming", "python", "javascript", "java", "code", "coding", "software",
    "algorithm", "database", "sql", "html", "css", "api", "framework", "git",
    "math", "calculus", "algebra", "geometry", "equation", "theorem", "integral",
    "politics", "election", "government", "president", "minister", "party",
    "movie", "film", "actor", "actress", "music", "song", "singer", "game",
    "travel", "tourism", "flight", "hotel", "vacation", "country", "city",
    "history", "war", "battle", "empire", "dynasty", "civilization",
    "physics", "chemistry", "astronomy", "planet", "star", "quantum",
    "stock", "trading", "crypto", "bitcoin", "investment", "forex",
    "netflix", "cinema", "series", "tv show", "video game",
]

class DomainDetector:
    def __init__(self):
        self._all_keywords = set()
        for category_words in HEALTH_FITNESS_KEYWORDS.values():
            for w in category_words:
                self._all_keywords.add(w.lower())

    def is_health_fitness_related(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> bool:
        if not message or not message.strip():
            return False

        msg_lower = message.lower().strip()

        # 1. Check for pure greetings and polite social phrases
        for pattern in GREETING_PATTERNS:
            if re.match(pattern, msg_lower, re.IGNORECASE):
                return True

        # 2. Score health and off-topic terms
        keyword_score = sum(1 for keyword in self._all_keywords if keyword in msg_lower)
        offtopic_score = sum(1 for indicator in OFF_TOPIC_INDICATORS if indicator in msg_lower)

        # 3. If distinct off-topic indicators are present with no health keywords, reject
        if offtopic_score > 0 and keyword_score == 0:
            return False

        # 4. If health/fitness keywords found, accept
        if keyword_score > 0 and keyword_score >= offtopic_score:
            return True

        # 5. Check if it's a valid contextual follow-up to an existing health conversation
        if conversation_history and len(conversation_history) >= 2:
            recent = conversation_history[-4:]
            recent_text = " ".join([m.get("content", "") for m in recent]).lower()
            has_health_context = any(keyword in recent_text for keyword in self._all_keywords)
            
            if has_health_context:
                # Common follow-up patterns
                followup_cues = [
                    "more", "also", "another", "else", "what about", "how about",
                    "instead", "alternative", "similar", "different", "better",
                    "modify", "change", "update", "add", "remove", "increase", "decrease",
                    "continue", "next", "then", "it", "this", "that", "those", "these",
                    "them", "they", "the same", "again", "repeat", "suitable", "home",
                    "gym", "easier", "harder", "why", "how", "what", "can you",
                ]
                if any(cue in msg_lower for cue in followup_cues) and offtopic_score == 0:
                    return True

        # 6. Default to rejection for unrecognized topics
        return False

    def get_rejection_message(self) -> str:
        return (
            "I'm FitMind AI, your personal Health & Fitness Coach. "
            "I can help you with workouts, nutrition, healthy eating, fitness goals, "
            "weight management education, yoga, sleep and wellness. "
            "Please ask me something related to health and fitness!"
        )

# Singleton
domain_detector = DomainDetector()
