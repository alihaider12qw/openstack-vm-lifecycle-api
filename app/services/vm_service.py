from __future__ import annotations

import logging
from dataclasses import dataclass

from app.core.exceptions import InvalidStateTransitionError, VMNotFoundError
from app.core.time import utcnow
from app.schemas.vm import (
    VALID_DELETE_STATES,
    VALID_REBOOT_STATES,
    VALID_START_STATES,
    VALID_STOP_STATES,
    VMActionResponse,
    VMCreateRequest,
    VMDetailsResponse,
    VMStatus,
)
from app.services.openstack_client import OpenStackAdapter, VMRecord

logger = logging.getLogger(__name__)


def _action_response(vm_id: str, action: str, status: VMStatus, message: str) -> VMActionResponse:
    return VMActionResponse(
        vm_id=vm_id,
        action=action,
        status=status,
        message=message,
        timestamp=utcnow(),
    )


@dataclass
class VMService:
    adapter: OpenStackAdapter

    def _to_details(self, vm: VMRecord) -> VMDetailsResponse:
        return VMDetailsResponse(
            id=vm.id,
            name=vm.name,
            status=vm.status,
            image_id=vm.image_id,
            flavor_id=vm.flavor_id,
            network_id=vm.network_id,
            key_name=vm.key_name,
            created_at=vm.created_at,
            updated_at=vm.updated_at,
        )

    def _get_active_vm(self, vm_id: str) -> VMRecord:
        vm = self.adapter.get_server(vm_id)
        if vm is None or vm.status == VMStatus.deleted:
            raise VMNotFoundError(vm_id)
        return vm

    def _assert_state(self, vm: VMRecord, action: str, valid_states: set[VMStatus]) -> None:
        if vm.status not in valid_states:
            raise InvalidStateTransitionError(vm.id, action, vm.status.value)

    def create_vm(self, payload: VMCreateRequest) -> VMDetailsResponse:
        logger.info("creating VM name=%s image=%s flavor=%s", payload.name, payload.image_id, payload.flavor_id)
        vm = self.adapter.create_server(payload)
        logger.info("created VM id=%s", vm.id)
        return self._to_details(vm)

    def list_vms(self, *, limit: int = 50, offset: int = 0) -> tuple[list[VMDetailsResponse], int]:
        all_vms = [vm for vm in self.adapter.list_servers() if vm.status != VMStatus.deleted]
        total = len(all_vms)
        page = all_vms[offset : offset + limit]
        return [self._to_details(vm) for vm in page], total

    def get_vm(self, vm_id: str) -> VMDetailsResponse:
        vm = self._get_active_vm(vm_id)
        return self._to_details(vm)

    def start_vm(self, vm_id: str) -> VMActionResponse:
        vm = self._get_active_vm(vm_id)
        self._assert_state(vm, "start", VALID_START_STATES)
        vm = self.adapter.start_server(vm_id)
        logger.info("started VM id=%s", vm_id)
        return _action_response(vm_id, "start", vm.status, "VM start requested")

    def stop_vm(self, vm_id: str) -> VMActionResponse:
        vm = self._get_active_vm(vm_id)
        self._assert_state(vm, "stop", VALID_STOP_STATES)
        vm = self.adapter.stop_server(vm_id)
        logger.info("stopped VM id=%s", vm_id)
        return _action_response(vm_id, "stop", vm.status, "VM stop requested")

    def reboot_vm(self, vm_id: str) -> VMActionResponse:
        vm = self._get_active_vm(vm_id)
        self._assert_state(vm, "reboot", VALID_REBOOT_STATES)
        vm = self.adapter.reboot_server(vm_id)
        logger.info("rebooted VM id=%s", vm_id)
        return _action_response(vm_id, "reboot", vm.status, "VM reboot requested")

    def delete_vm(self, vm_id: str) -> VMActionResponse:
        vm = self._get_active_vm(vm_id)
        self._assert_state(vm, "delete", VALID_DELETE_STATES)
        vm = self.adapter.delete_server(vm_id)
        logger.info("deleted VM id=%s", vm_id)
        return _action_response(vm_id, "delete", vm.status, "VM delete requested")
