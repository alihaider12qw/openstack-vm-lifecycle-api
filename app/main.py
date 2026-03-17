import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.api.routes.vms import router as vm_router
from app.core.config import settings
from app.core.exceptions import AppError, InvalidStateTransitionError, VMNotFoundError
from app.core.logging_config import setup_logging
from app.core.middleware import RequestIdMiddleware
from app.services.openstack_client import MockOpenStackClient
from app.services.vm_service import VMService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None]:
    setup_logging()
    logger.info(
        "starting %s v%s env=%s mock=%s",
        settings.app_name,
        settings.app_version,
        settings.environment,
        settings.use_mock_openstack,
    )

    if settings.use_mock_openstack:
        adapter = MockOpenStackClient()
    else:
        # Placeholder: swap in RealOpenStackClient(settings) once implemented
        raise RuntimeError("Real OpenStack adapter not yet implemented — set USE_MOCK_OPENSTACK=true")

    application.state.vm_service = VMService(adapter=adapter)
    yield
    logger.info("shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    responses={
        404: {"description": "Resource not found"},
        409: {"description": "Invalid state transition"},
        422: {"description": "Validation error"},
    },
)

app.add_middleware(RequestIdMiddleware)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(VMNotFoundError)
async def vm_not_found_handler(_request: Request, exc: VMNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": {"code": exc.code, "message": str(exc)}})


@app.exception_handler(InvalidStateTransitionError)
async def invalid_state_handler(_request: Request, exc: InvalidStateTransitionError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"error": {"code": exc.code, "message": str(exc)}})


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    logger.error("unhandled app error code=%s message=%s", exc.code, str(exc))
    return JSONResponse(status_code=500, content={"error": {"code": exc.code, "message": str(exc)}})


@app.exception_handler(Exception)
async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )


app.include_router(vm_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version, "environment": settings.environment}
