import sys
import io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from app import app
from PIL import Image

client = TestClient(app)

def test_document_upload_and_rag():
    # 1. Create a sample health & fitness document in memory
    doc_content = """FITNESS AND NUTRITION MASTER GUIDE (Page 1)

1. Hypertrophy Guidelines:
To maximize muscle growth, aim for 10 to 20 hard working sets per muscle group per week.
Train in the 6 to 12 repetition range with 2-3 minutes of rest between compound sets.

2. Protein Intake:
Target 1.6 to 2.2 grams of protein per kilogram of bodyweight each day.
Distribute protein intake evenly across 3 to 5 meals.

3. Hydration Guidelines:
Drink 2.5 to 3.5 liters of water daily, increasing fluid intake by 500ml for every hour of intense exercise.
"""
    files = {
        'file': ('nutrition_guide.txt', io.BytesIO(doc_content.encode('utf-8')), 'text/plain')
    }
    
    # 2. Upload document
    res_upload = client.post("/api/analyze-document", files=files)
    assert res_upload.status_code == 200
    data = res_upload.json()
    assert data["success"] is True
    conv_id = data["conversation_id"]
    doc_id = data["doc_id"]
    print(f"✅ Document uploaded & indexed! Conv ID: {conv_id}, Doc ID: {doc_id}")

    # 3. Test RAG question
    res_q = client.post("/api/rag/question", json={
        "question": "How much protein should I eat per kilogram?",
        "conversation_id": conv_id,
        "document_id": doc_id
    })
    assert res_q.status_code == 200
    print(f"✅ RAG question answered! Response length: {len(res_q.json()['response'])}")

def test_image_upload_validation():
    # 1. Test image generation
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)

    files = {
        'file': ('test_meal.jpg', buf, 'image/jpeg')
    }
    data = {
        'message': 'Analyze this breakfast meal'
    }

    res = client.post("/api/analyze-image", files=files, data=data)
    assert res.status_code == 200
    print(f"✅ Image upload accepted & processed! Response length: {len(res.json()['response'])}")

if __name__ == "__main__":
    print("--- Running RAG & Image API Integration Tests ---")
    test_document_upload_and_rag()
    test_image_upload_validation()
    print("--- ALL RAG & IMAGE TESTS PASSED! ---")
