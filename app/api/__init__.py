from .prospects import get_prospects
from .prospects import get_prospect
from .prospects import create_prospect
from .prospects import update_prospect
from .prospects import router as prospects_router

__all__ = [
    "get_prospects",
    "get_prospect",
    "create_prospect",
    "update_prospect",
    "prospects_router",
]
