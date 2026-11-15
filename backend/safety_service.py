from typing import Optional

SAFETY_DISCLAIMER = (
    "\n\n> **⚕️ Disclaimer:** This information is for general educational purposes only "
    "and should not replace professional medical advice. Please consult a qualified "
    "healthcare professional for personalized medical guidance."
)

EMERGENCY_KEYWORDS = [
    "heart attack", "stroke", "chest pain", "can't breathe", "cannot breathe",
    "severe bleeding", "unconscious", "seizure", "anaphylaxis", "allergic shock",
    "suicidal", "suicide", "overdose", "poisoning", "choking",
]

MEDICAL_DIAGNOSIS_PATTERNS = [
    "diagnose me", "what disease", "what illness", "am i sick",
    "prescribe me", "what medicine", "what drug should",
    "is this cancer", "do i have", "what condition",
]

class SafetyService:
    def check_emergency(self, message: str) -> Optional[str]:
        msg_lower = message.lower()
        for keyword in EMERGENCY_KEYWORDS:
            if keyword in msg_lower:
                return (
                    "🚨 **This sounds like it could be a medical emergency.**\n\n"
                    "Please **call your local emergency number immediately** "
                    "(e.g., 911 in the US, 999 in the UK, 112 in EU, 108 in India).\n\n"
                    "If someone is with you, ask them to help while you call.\n\n"
                    "I'm an AI fitness coach and cannot provide emergency medical assistance."
                )
        return None

    def check_medical_diagnosis(self, message: str) -> bool:
        msg_lower = message.lower()
        for pattern in MEDICAL_DIAGNOSIS_PATTERNS:
            if pattern in msg_lower:
                return True
        return False

    def get_medical_disclaimer(self) -> str:
        return SAFETY_DISCLAIMER

    def add_safety_context(self, prompt: str, message: str) -> str:
        msg_lower = message.lower()
        safety_notes = []

        if self.check_medical_diagnosis(message):
            safety_notes.append(
                "The user is asking about medical diagnosis. Remind them that you cannot "
                "diagnose conditions or prescribe medications. Provide general educational "
                "information and strongly recommend consulting a healthcare professional."
            )

        if any(w in msg_lower for w in ["supplement", "creatine", "steroid", "hormone"]):
            safety_notes.append(
                "The user is asking about supplements. Provide general information but "
                "recommend consulting a healthcare provider before starting any supplement regimen."
            )

        if any(w in msg_lower for w in ["injury", "pain", "hurt", "sprain", "strain", "fracture"]):
            safety_notes.append(
                "The user mentions pain or injury. Provide general first-aid guidance "
                "and recommend seeing a healthcare professional for proper evaluation."
            )

        if any(w in msg_lower for w in ["fast", "fasting", "extreme diet", "crash diet", "starvation"]):
            safety_notes.append(
                "The user is asking about extreme dieting. Do not recommend dangerous "
                "or extreme weight loss methods. Emphasize sustainable, healthy approaches."
            )

        if safety_notes:
            notes = " ".join(safety_notes)
            return f"{prompt}\n\nSAFETY NOTES: {notes}"
        return prompt

# Singleton
safety_service = SafetyService()
