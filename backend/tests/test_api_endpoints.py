import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()

def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_portal_invoices_endpoint(client):
    response = client.get("/api/portal/invoices?company=Acme")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

def test_finance_records_endpoint(client):
    response = client.get("/api/finance/records?company=Acme")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_agent_tools_endpoint(client):
    response = client.get("/api/agent/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) >= 6

def test_agent_run_endpoint(client):
    payload = {
        "goal": "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."
    }
    response = client.post("/api/agent/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["verification_passed"] is True

def test_demo_scenario_1(client):
    response = client.post("/api/demo/scenario-1-success")
    assert response.status_code == 200
    data = response.json()
    assert data["state"]["status"] == "COMPLETED"
    assert data["state"]["verification_passed"] is True

def test_demo_scenario_2(client):
    response = client.post("/api/demo/scenario-2-retry")
    assert response.status_code == 200
    data = response.json()
    assert data["state"]["status"] == "COMPLETED"
    assert data["state"]["verification_passed"] is True

def test_demo_scenario_3(client):
    response = client.post("/api/demo/scenario-3-verification-fail")
    assert response.status_code == 200
    data = response.json()
    assert data["state"]["status"] == "FAILED"
    assert data["state"]["verification_passed"] is False

def test_demo_scenario_4(client):
    response = client.post("/api/demo/scenario-4-generalization")
    assert response.status_code == 200
    data = response.json()
    assert data["state"]["status"] == "COMPLETED"
    assert data["state"]["verification_passed"] is True
