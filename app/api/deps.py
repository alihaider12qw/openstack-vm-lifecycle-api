from fastapi import Request

from app.services.vm_service import VMService


def get_vm_service(request: Request) -> VMService:
    service: VMService = request.app.state.vm_service
    return service
