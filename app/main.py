import logging
from app.utils.logging import LogEntry, LogLevel
from datetime import datetime, date
from app.config.settings import Settings
from typing import Union
from fastapi import FastAPI, Request, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pytz

from app.api.prospects import router as prospects_router
from app.api.prospects import get_prospects

settings = Settings()

# Set up logging
log_level = settings.LOG_LEVEL
print(f"Log level: {log_level}")
match log_level:
    case "DEBUG":
        logging_level = logging.DEBUG
    case "INFO":
        logging_level = logging.INFO
    case "WARNING":
        logging_level = logging.WARNING
    case "ERROR":
        logging_level = logging.ERROR
    case _:
        logging_level = logging.INFO

logging.basicConfig(
    filename=f"logs/{date.today()}app.log",
    level=logging_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Set up FastAPI
app = FastAPI()
router = APIRouter(prefix="/api/v1")


# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Set up logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now(tz=pytz.timezone(settings.TIMEZONE))
    response = await call_next(request)
    process_time = datetime.now(tz=pytz.timezone(settings.TIMEZONE)) - start_time
    log_entry = LogEntry(
        level=LogLevel.INFO,
        service="fastapi-backend",
        module="app.main",
        function="log_requests",
        message=f"Request: {request.method} {request.url} - Status: {response.status_code} - Process Time: {process_time}",
        context={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time_seconds": str(process_time.total_seconds()),
        },
    )
    logger.info(
        f"{log_entry.timeStamp} - {log_entry.level.value} - {log_entry.message}"
    )
    return response


# Set up error handling middleware
@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    log_entry = LogEntry(
        level=LogLevel.ERROR,
        service="fastapi-backend",
        module="app.main",
        function="handle_exception",
        message=f"Exception: {str(exc)}",
        context={
            "method": request.method,
            "url": str(request.url),
            "exception": str(exc),
        },
    )
    logger.error(
        f"{log_entry.timeStamp} - {log_entry.level.value} - {log_entry.message}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": f"An error occurred: {str(exc)}"},
        headers={"X-Error": "Internal Server Error"},
    )


# Endpoints
@router.get("/health")
async def health_check():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "healthy"})


# Add the router to the app
app.include_router(router)
app.include_router(prospects_router)

"""
def main():
    print("Hello from sales-assistant!\n Starting HTTP Server...")
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8111, reload=True, log_level="info", root_path="/app/api"
    )


if __name__ == "__main__":
    main()
"""
