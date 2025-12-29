import logging
from utils import LogEntry, LogLevel
from datetime import datetime, date
from config import Settings

settings = Settings()
log_level = settings.LOG_LEVEL
print(f"Log level: {log_level}")
match log_level:
    case "DEBUG":
        logging_level = logging.DEBUG
    case "INFO":
        logging_level = l
    case "WARNING":
        logging_level = logging.WARNING
    case "ERROR":
        logging_level = logging.ERROR
    case _:
        logging_level = logging.INFO

logging.basicConfig(
    filename = f"logs/{date.today()}app.log",
    level=logging_level,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def main():
    print("Hello from sales-assistant!")
    


if __name__ == "__main__":
    main()
