import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.openstack_client import MockOpenStackClient
from app.services.vm_service import VMService


@pytest.fixture()
def client() -> TestClient:
    adapter = MockOpenStackClient()
    app.state.vm_service = VMService(adapter=adapter)
    return TestClient(app)


@pytest.fixture()
def created_vm(client: TestClient) -> dict:
    payload = {
        "name": "test-vm",
        "image_id": "img-ubuntu-2204",
        "flavor_id": "m1.small",
        "network_id": "net-private",
    }
    resp = client.post("/v1/vms", json=payload)
    assert resp.status_code == 201
    return resp.json()
