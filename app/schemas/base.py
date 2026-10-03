from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


class DataResponse(BaseResponse, Generic[T]):
    data: T


class PaginatedMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseResponse, Generic[T]):
    data: List[T]
    pagination: PaginatedMeta
