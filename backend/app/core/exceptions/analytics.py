from app.core.exceptions.base import NotFoundException


class AttemptNotFoundException(NotFoundException):
    default_detail = "Попытка не найдена"
