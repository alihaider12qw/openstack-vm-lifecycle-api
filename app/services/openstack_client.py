from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import uuid4

from app.core.exceptions import VMNotFoundError
from app.core.time import utcnow
from app.schemas.vm import VMCreateRequest, VMStatus


@dataclass
class VMRecord:
    id: str
    name: str
    status: VMStatus
    image_id: str
    flavor_id: str
    network_id: str
    key_name: str | None
    created_at: datetime
    updated_at: datetime


class OpenStackAdapter(Protocol):
    def create_server(self, payload: VMCreateRequest) -> VMRecord: ...

    def list_servers(self) -> list[VMRecord]: ...

    def get_server(self, vm_id: str) -> VMRecord | None: ...

    def start_server(self, vm_id: str) -> VMRecord: ...

    def stop_server(self, vm_id: str) -> VMRecord: ...

    def reboot_server(self, vm_id: str) -> VMRecord: ...

    def delete_server(self, vm_id: str) -> VMRecord: ...


class MockOpenStackClient:
    """In-memory OpenStack simulator for local development and tests."""

    def __init__(self) -> None:
        self._vms: dict[str, VMRecord] = {}

    def create_server(self, payload: VMCreateRequest) -> VMRecord:
        now = utcnow()
        vm = VMRecord(
            id=str(uuid4()),
            name=payload.name,
            status=VMStatus.active,
            image_id=payload.image_id,
            flavor_id=payload.flavor_id,
            network_id=payload.network_id,
            key_name=payload.key_name,
            created_at=now,
            updated_at=now,
        )
        self._vms[vm.id] = vm
        return vm

    def list_servers(self) -> list[VMRecord]:
        return list(self._vms.values())

    def get_server(self, vm_id: str) -> VMRecord | None:
        return self._vms.get(vm_id)

    def _get_or_raise(self, vm_id: str) -> VMRecord:
        vm = self.get_server(vm_id)
        if vm is None:
            raise VMNotFoundError(vm_id)
        return vm

    def start_server(self, vm_id: str) -> VMRecord:
        vm = self._get_or_raise(vm_id)
        vm.status = VMStatus.active
        vm.updated_at = utcnow()
        return vm

    def stop_server(self, vm_id: str) -> VMRecord:
        vm = self._get_or_raise(vm_id)
        vm.status = VMStatus.stopped
        vm.updated_at = utcnow()
        return vm

    def reboot_server(self, vm_id: str) -> VMRecord:
        vm = self._get_or_raise(vm_id)
        vm.status = VMStatus.rebooting
        vm.updated_at = utcnow()
        return vm

    def delete_server(self, vm_id: str) -> VMRecord:
        vm = self._get_or_raise(vm_id)
        vm.status = VMStatus.deleted
        vm.updated_at = utcnow()
        return vm
