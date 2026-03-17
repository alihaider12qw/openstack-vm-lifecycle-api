from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_vm_service
from app.schemas.vm import VMActionResponse, VMCreateRequest, VMDetailsResponse, VMListResponse
from app.services.vm_service import VMService

router = APIRouter(prefix="/v1/vms", tags=["vms"])

Service = Annotated[VMService, Depends(get_vm_service)]


@router.post("", response_model=VMDetailsResponse, status_code=201)
def create_vm(payload: VMCreateRequest, service: Service) -> VMDetailsResponse:
    return service.create_vm(payload)


@router.get("", response_model=VMListResponse)
def list_vms(
    service: Service,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> VMListResponse:
    items, total = service.list_vms(limit=limit, offset=offset)
    return VMListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{vm_id}", response_model=VMDetailsResponse)
def get_vm(vm_id: UUID, service: Service) -> VMDetailsResponse:
    return service.get_vm(str(vm_id))


@router.post("/{vm_id}/start", response_model=VMActionResponse)
def start_vm(vm_id: UUID, service: Service) -> VMActionResponse:
    return service.start_vm(str(vm_id))


@router.post("/{vm_id}/stop", response_model=VMActionResponse)
def stop_vm(vm_id: UUID, service: Service) -> VMActionResponse:
    return service.stop_vm(str(vm_id))


@router.post("/{vm_id}/reboot", response_model=VMActionResponse)
def reboot_vm(vm_id: UUID, service: Service) -> VMActionResponse:
    return service.reboot_vm(str(vm_id))


@router.delete("/{vm_id}", response_model=VMActionResponse)
def delete_vm(vm_id: UUID, service: Service) -> VMActionResponse:
    return service.delete_vm(str(vm_id))
