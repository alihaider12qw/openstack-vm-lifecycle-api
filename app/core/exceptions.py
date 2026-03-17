class AppError(Exception):
    """Base application error with a machine-readable code."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        super().__init__(message)
        self.code = code


class VMNotFoundError(AppError):
    def __init__(self, vm_id: str) -> None:
        super().__init__(f"VM with id '{vm_id}' not found", code="VM_NOT_FOUND")
        self.vm_id = vm_id


class InvalidStateTransitionError(AppError):
    def __init__(self, vm_id: str, action: str, current_status: str) -> None:
        super().__init__(
            f"Cannot {action} VM '{vm_id}' in state {current_status}",
            code="INVALID_STATE_TRANSITION",
        )


class OpenStackConnectionError(AppError):
    def __init__(self, detail: str = "OpenStack backend unreachable") -> None:
        super().__init__(detail, code="OPENSTACK_CONNECTION_ERROR")


class QuotaExceededError(AppError):
    def __init__(self, detail: str = "Resource quota exceeded") -> None:
        super().__init__(detail, code="QUOTA_EXCEEDED")
