# FitMind AI – Intelligent Health & Fitness Coach

FitMind AI is a full-stack, AI-powered Health and Fitness Coach Chatbot built with **Python**, **FastAPI**, **Google Gemini Multimodal API**, **FAISS vector embeddings**, and an interactive **glassmorphic dashboard**.

Developed as an MSc Data Science academic project.

---

## 🌟 Key Features

1. **Intelligent Health & Fitness Chat**
   - Natural, conversational responses grounded in exercise science, nutrition, recovery, and wellness habits.
   - Strict domain restriction with contextual classification (allows greetings, follow-ups, but gently rejects unrelated topics like coding, politics, math).
   - Evidence-based safety guardrails (emergency detection, medical disclaimer, no drug prescribing or extreme diets).

2. **Multimodal Food & Workout Image Analysis**
   - Visual analysis of food photos: identifies meal components, estimates portion sizes, calories, and macronutrients (protein, carbs, fats).
   - Nutrition label scanning: extracts serving sizes, calories, sodium, and ingredients.
   - Workout form & exercise chart analysis.

3. **RAG-Powered Document Analysis**
   - Upload health documents, fitness guides, or blood test reports in **PDF**, **DOCX**, or **TXT** format.
   - Text chunking, sentence embeddings with PyMuPDF and python-docx.
   - In-memory FAISS vector indexing with conversational context isolation.

4. **Unique Interactive Fitness Dashboard**
   - **Adult BMI Calculator** with real-time category categorization and educational feedback.
   - **Daily Hydration Tracker** with interactive circular meter, quick +250ml / +500ml logging, and goal tracking.
   - **Macronutrient Breakdown & Calorie Charts** using Chart.js.
   - **Weekly Workout Planner** (Mon–Sun) with exercise checklists.
   - **Healthy Habits Checklist** for sleep, movement, hydration, nutrition, and mindfulness.
   - **Weight & Measurement Progress Tracker** with historical trend visualization.

5. **Conversational Memory & Persistence**
   - SQLite relational database (`database/fitmind.db`).
   - Multi-session chat history, auto-naming, renaming, message persistence, and session deletion.

---

## 🏗️ Architecture & Project Structure

```
FitMind-AI/
├── app.py                     # FastAPI application entrypoint & routing
├── config.py                  # Central configuration & environment variables
├── requirements.txt           # Python dependencies
├── .env                       # API keys and environment settings
├── .env.example               # Template for environment variables
├── .gitignore                 # Excluded directories and credentials
├── README.md                  # Complete project documentation
│
├── backend/
│   ├── __init__.py
│   ├── gemini_service.py      # Google Gen AI SDK client & safety integration
│   ├── domain_detector.py     # Context-aware domain classifier
│   ├── chat_service.py        # Central chat orchestration
│   ├── safety_service.py      # Emergency & medical advisory safety rules
│   ├── image_analyzer.py      # Multimodal food & label vision analyzer
│   ├── document_processor.py  # PDF (PyMuPDF), DOCX, TXT parser
│   ├── rag_pipeline.py        # Chunking, embeddings & context grounding
│   ├── vector_store.py        # FAISS vector similarity search
│   └── conversation_manager.py# SQLite conversation management
│
├── database/
│   ├── __init__.py
│   ├── db.py                  # SQLite database connection & schema creation
│   └── models.py              # Pydantic data schemas
│
├── frontend/
│   ├── templates/
│   │   └── index.html         # Responsive, glassmorphic Single Page App
│   └── static/
│       ├── css/
│       │   └── style.css      # Dark navy & purple glassmorphic theme
│       ├── js/
│       │   └── app.js         # Frontend controllers, Chart.js, API clients
│       └── images/
│
├── uploads/                   # Temporary file upload staging
└── vector_db/                 # Persistent document indices
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.9 to 3.12 installed on your system.
- A valid Google Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

### 2. Installation
Open a terminal in the project directory:

```bash
cd FitMind-AI
pip install -r requirements.txt
```

### 3. Configure API Key
Open `.env` and set your key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run the Application
```bash
python app.py
```

The application will initialize the SQLite database and start the FastAPI server at:
👉 **`http://127.0.0.1:8000`** (will automatically open in your default web browser).

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the main web dashboard |
| `GET` | `/api/health` | Health status and Gemini API connectivity |
| `POST` | `/api/chat` | Send a text query to the health coach |
| `POST` | `/api/analyze-image` | Multimodal analysis of food, workout, or label images |
| `POST` | `/api/analyze-document` | Upload and index PDF, DOCX, or TXT documents |
| `POST` | `/api/rag/question` | Ask grounded questions against indexed documents |
| `GET` | `/api/conversations` | Retrieve conversation list |
| `POST` | `/api/conversations` | Create a new conversation |
| `GET` | `/api/conversations/{id}` | Retrieve messages and documents for a conversation |
| `DELETE` | `/api/conversations/{id}` | Delete a specific conversation |
| `DELETE` | `/api/conversations` | Clear all conversation history |

---

## ⚠️ Medical & Safety Disclaimer

*FitMind AI is developed strictly for educational and informational purposes as part of an MSc Data Science curriculum. It does not provide medical diagnoses, treatment plans, or prescriptions. Users experiencing severe or acute medical symptoms should contact emergency medical services or consult a licensed physician immediately.*
