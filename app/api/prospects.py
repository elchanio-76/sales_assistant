from fastapi import APIRouter, HTTPException
from app.models.api import ProspectCreate, ProspectUpdate, ProspectResponse
from app.services.db_crud import (
    create_or_update_prospect,
    get_prospect_by_id,
    get_all_prospects,
)


router = APIRouter(
    prefix="/api/v1/prospects",
    tags=["prospects"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[ProspectResponse])
async def get_prospects():
    """Get all prospects from the database."""
    prospects = get_all_prospects()
    # Use model_validate to convert SQLAlchemy objects to Pydantic models
    return [ProspectResponse.model_validate(prospect) for prospect in prospects]


@router.get("/{prospect_id}")
async def get_prospect(prospect_id: int):
    prospect = get_prospect_by_id(prospect_id)
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")
    
    return ProspectResponse.model_validate(prospect)


@router.post("/")
async def create_prospect(prospect: ProspectCreate):
    return {"message": "Create a new prospect"}


@router.put("/prospects/{prospect_id}")
async def update_prospect(prospect_id: int, prospect: ProspectUpdate):
    return {"message": f"Update prospect with ID {prospect_id}"}
