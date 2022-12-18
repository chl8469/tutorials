from fastapi import APIRouter

from app.routes import stock, animegan


router = APIRouter()
router.include_router(
    stock.router, tags=["stock"], prefix="/stock"
)
router.include_router(
    animegan.router, tags=["image"], prefix="/gan"
)
