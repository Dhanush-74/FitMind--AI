import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitMind" in response.text
    print("✅ GET /: 200 OK (HTML Template served)")

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print(f"✅ GET /api/health: 200 OK -> {data}")

def test_domain_rejection():
    response = client.post("/api/chat", json={"message": "Write a python script to sort numbers"})
    assert response.status_code == 200
    data = response.json()
    assert "FitMind AI" in data["response"]
    assert "Health & Fitness Coach" in data["response"]
    print("✅ POST /api/chat [Unrelated Domain Rejection]: 200 OK")

def test_emergency_detection():
    response = client.post("/api/chat", json={"message": "I have severe chest pain and can't breathe"})
    assert response.status_code == 200
    data = response.json()
    assert "medical emergency" in data["response"].lower()
    print("✅ POST /api/chat [Emergency Detection]: 200 OK")

def test_conversation_crud():
    # 1. Create conversation
    res_create = client.post("/api/conversations")
    assert res_create.status_code == 200
    conv_id = res_create.json()["id"]
    print(f"✅ POST /api/conversations: 200 OK -> ID: {conv_id}")

    # 2. List conversations
    res_list = client.get("/api/conversations")
    assert res_list.status_code == 200
    assert any(c["id"] == conv_id for c in res_list.json()["conversations"])
    print("✅ GET /api/conversations: 200 OK")

    # 3. Get single conversation
    res_get = client.get(f"/api/conversations/{conv_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == conv_id
    print(f"✅ GET /api/conversations/{conv_id}: 200 OK")

    # 4. Delete conversation
    res_del = client.delete(f"/api/conversations/{conv_id}")
    assert res_del.status_code == 200
    print(f"✅ DELETE /api/conversations/{conv_id}: 200 OK")

def test_fitness_data_storage():
    payload = {
        "type": "hydration",
        "data": {"amount": 250, "goal": 2500}
    }
    res_save = client.post("/api/fitness-data", json=payload)
    assert res_save.status_code == 200
    print("✅ POST /api/fitness-data: 200 OK")

    res_get = client.get("/api/fitness-data/hydration")
    assert res_get.status_code == 200
    data = res_get.json()["data"]
    assert len(data) > 0
    print("✅ GET /api/fitness-data/hydration: 200 OK")

if __name__ == "__main__":
    print("--- Running FitMind AI API Integration Tests ---")
    test_root()
    test_health()
    test_domain_rejection()
    test_emergency_detection()
    test_conversation_crud()
    test_fitness_data_storage()
    print("--- ALL API TESTS PASSED SUCCESSFULLY! ---")
