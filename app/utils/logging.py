from enum import Enum
from datetime import datetime
import pytz

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class LogEntry:
    timeStamp: str
    level: LogLevel
    service: str
    module: str
    function: str
    message: str
    context: dict
    trace_id: str

    def __init__(
            self, 
            level: LogLevel = LogLevel.INFO, 
            service: str = "", 
            module: str = "", 
            function: str = "", 
            message: str = "",
            context: dict = {},
            trace_id: str = "",
            ):
    
        self.timeStamp = datetime.now(tz= pytz.timezone("Europe/Athens") ).isoformat()
        self.level = level
        self.service = service
        self.module = module
        self.function = function
        self.message = message
        self.context = context
        self.trace_id = trace_id