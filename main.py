from fastapi import FastAPI
import logging

from app.config import settings
from app.api.assets import router as assets_router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto Portfolio API",
    description="Track crypto prices, portfolio, and alerts",
    version="1.0.0"
)

app.include_router(assets_router)
# Add more routers later (portfolio, alerts, exports)

# TODO: Include all routers (assets, portfolio, alerts, exports)

@app.get("/")
def root():
    return {"message": "Crypto Portfolio API is running!", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}
