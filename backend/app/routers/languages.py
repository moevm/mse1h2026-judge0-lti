from typing import List

from fastapi import APIRouter, Depends

from app.schemas.language import LanguageResponse
from app.services.language import LanguageService, get_language_service

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get(
    "/",
    response_model=List[LanguageResponse],
    summary="Получить список всех языков",
)
def get_languages(
    service: LanguageService = Depends(get_language_service),
) -> List[LanguageResponse]:
    languages = service.get_all_languages()
    return languages
