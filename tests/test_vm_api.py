from fastapi.testclient import TestClient


class TestHealth:
    def test_returns_ok(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert "version" in body
        assert "environment" in body


class TestCreateVM:
    def test_success(self, client: TestClient) -> None:
        payload = {
            "name": "new-vm",
            "image_id": "img-ubuntu",
            "flavor_id": "m1.small",
            "network_id": "net-priv",
        }
        resp = client.post("/v1/vms", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "new-vm"
        assert body["status"] == "ACTIVE"
        assert "id" in body
        assert "created_at" in body

    def test_missing_required_field(self, client: TestClient) -> None:
        resp = client.post("/v1/vms", json={"name": "vm"})
        assert resp.status_code == 422

    def test_name_too_short(self, client: TestClient) -> None:
        payload = {
            "name": "ab",
            "image_id": "img-ubuntu",
            "flavor_id": "m1.small",
            "network_id": "net-priv",
        }
        resp = client.post("/v1/vms", json=payload)
        assert resp.status_code == 422

    def test_name_invalid_characters(self, client: TestClient) -> None:
        payload = {
            "name": "bad name!",
            "image_id": "img-ubuntu",
            "flavor_id": "m1.small",
            "network_id": "net-priv",
        }
        resp = client.post("/v1/vms", json=payload)
        assert resp.status_code == 422


class TestListVMs:
    def test_empty(self, client: TestClient) -> None:
        resp = client.get("/v1/vms")
        assert resp.status_code == 200
        body = resp.json()
        assert body["items"] == []
        assert body["total"] == 0

    def test_with_vms(self, client: TestClient, created_vm: dict) -> None:
        resp = client.get("/v1/vms")
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["id"] == created_vm["id"]

    def test_pagination(self, client: TestClient) -> None:
        for i in range(5):
            client.post(
                "/v1/vms",
                json={
                    "name": f"vm-{i:03d}",
                    "image_id": "img-ubuntu",
                    "flavor_id": "m1.small",
                    "network_id": "net-priv",
                },
            )
        resp = client.get("/v1/vms?limit=2&offset=0")
        body = resp.json()
        assert len(body["items"]) == 2
        assert body["total"] == 5

        resp2 = client.get("/v1/vms?limit=2&offset=4")
        body2 = resp2.json()
        assert len(body2["items"]) == 1


class TestGetVM:
    def test_success(self, client: TestClient, created_vm: dict) -> None:
        resp = client.get(f"/v1/vms/{created_vm['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created_vm["id"]

    def test_not_found(self, client: TestClient) -> None:
        resp = client.get("/v1/vms/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "VM_NOT_FOUND"

    def test_invalid_uuid(self, client: TestClient) -> None:
        resp = client.get("/v1/vms/not-a-uuid")
        assert resp.status_code == 422


class TestLifecycleActions:
    def test_stop_active_vm(self, client: TestClient, created_vm: dict) -> None:
        resp = client.post(f"/v1/vms/{created_vm['id']}/stop")
        assert resp.status_code == 200
        assert resp.json()["status"] == "SHUTOFF"

    def test_start_stopped_vm(self, client: TestClient, created_vm: dict) -> None:
        client.post(f"/v1/vms/{created_vm['id']}/stop")
        resp = client.post(f"/v1/vms/{created_vm['id']}/start")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ACTIVE"

    def test_reboot_active_vm(self, client: TestClient, created_vm: dict) -> None:
        resp = client.post(f"/v1/vms/{created_vm['id']}/reboot")
        assert resp.status_code == 200
        assert resp.json()["status"] == "REBOOT"

    def test_delete_active_vm(self, client: TestClient, created_vm: dict) -> None:
        resp = client.delete(f"/v1/vms/{created_vm['id']}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "DELETED"

    def test_get_deleted_vm_returns_404(self, client: TestClient, created_vm: dict) -> None:
        client.delete(f"/v1/vms/{created_vm['id']}")
        resp = client.get(f"/v1/vms/{created_vm['id']}")
        assert resp.status_code == 404

    def test_deleted_vm_excluded_from_list(self, client: TestClient, created_vm: dict) -> None:
        client.delete(f"/v1/vms/{created_vm['id']}")
        resp = client.get("/v1/vms")
        assert resp.json()["total"] == 0


class TestStateTransitionGuards:
    def test_cannot_start_active_vm(self, client: TestClient, created_vm: dict) -> None:
        resp = client.post(f"/v1/vms/{created_vm['id']}/start")
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "INVALID_STATE_TRANSITION"

    def test_cannot_stop_stopped_vm(self, client: TestClient, created_vm: dict) -> None:
        client.post(f"/v1/vms/{created_vm['id']}/stop")
        resp = client.post(f"/v1/vms/{created_vm['id']}/stop")
        assert resp.status_code == 409

    def test_cannot_reboot_stopped_vm(self, client: TestClient, created_vm: dict) -> None:
        client.post(f"/v1/vms/{created_vm['id']}/stop")
        resp = client.post(f"/v1/vms/{created_vm['id']}/reboot")
        assert resp.status_code == 409

    def test_cannot_delete_deleted_vm(self, client: TestClient, created_vm: dict) -> None:
        client.delete(f"/v1/vms/{created_vm['id']}")
        resp = client.delete(f"/v1/vms/{created_vm['id']}")
        assert resp.status_code == 404

    def test_action_on_nonexistent_vm(self, client: TestClient) -> None:
        fake_id = "00000000-0000-0000-0000-000000000000"
        for action in ["start", "stop", "reboot"]:
            resp = client.post(f"/v1/vms/{fake_id}/{action}")
            assert resp.status_code == 404
        resp = client.delete(f"/v1/vms/{fake_id}")
        assert resp.status_code == 404


class TestCorrelationId:
    def test_response_has_request_id(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert "x-request-id" in resp.headers

    def test_echoes_provided_request_id(self, client: TestClient) -> None:
        resp = client.get("/health", headers={"X-Request-ID": "test-trace-123"})
        assert resp.headers["x-request-id"] == "test-trace-123"
