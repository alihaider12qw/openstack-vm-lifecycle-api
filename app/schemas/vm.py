from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class VMStatus(StrEnum):
    build = "BUILD"
    active = "ACTIVE"
    stopped = "SHUTOFF"
    rebooting = "REBOOT"
    deleting = "DELETING"
    deleted = "DELETED"
    error = "ERROR"


VALID_START_STATES = {VMStatus.stopped}
VALID_STOP_STATES = {VMStatus.active}
VALID_REBOOT_STATES = {VMStatus.active}
VALID_DELETE_STATES = {VMStatus.active, VMStatus.stopped, VMStatus.error}


class VMCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9._-]+$")
    image_id: str = Field(min_length=3, max_length=128)
    flavor_id: str = Field(min_length=3, max_length=128)
    network_id: str = Field(min_length=3, max_length=128)
    key_name: str | None = Field(default=None, max_length=128)


class VMActionResponse(BaseModel):
    vm_id: str
    action: str
    status: VMStatus
    message: str
    timestamp: datetime


class VMDetailsResponse(BaseModel):
    id: str
    name: str
    status: VMStatus
    image_id: str
    flavor_id: str
    network_id: str
    key_name: str | None = None
    created_at: datetime
    updated_at: datetime


class VMListResponse(BaseModel):
    items: list[VMDetailsResponse]
    total: int
    limit: int
    offset: int


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
