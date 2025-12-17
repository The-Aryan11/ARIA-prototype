"""
ARIA - Adaptive Retail Intelligence Assistant
Main FastAPI Application

This is the entry point for the ARIA backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import sentry_sdk

from .core.config import settings
from .core.database import init_databases, close_databases

# Import API routers
from .api.chat import router as chat_router
from .api.whatsapp import router as whatsapp_router
from .api.analytics import router as analytics_router
from .api.color import router as color_router

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


# ============== Sentry Error Tracking ==============

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT
    )
    logger.info("Sentry initialized")


# ============== Application Lifespan ==============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    
    # Startup
    logger.info("Starting ARIA...", version=settings.APP_VERSION)
    
    try:
        await init_databases()
        logger.info("ARIA is ready! 🚀")
    except Exception as e:
        logger.error("Failed to initialize databases", error=str(e))
        # Continue anyway for demo purposes
    
    yield
    
    # Shutdown
    logger.info("Shutting down ARIA...")
    await close_databases()
    logger.info("ARIA shutdown complete")


# ============== Create FastAPI App ==============

app = FastAPI(
    title="ARIA - Adaptive Retail Intelligence Assistant",
    description="""
    🛍️ **ARIA** is an AI-powered omnichannel sales assistant for ABFRL.
    
    ## Features
    - 💬 **Multi-channel Chat**: WhatsApp, Web, Mobile, Store Kiosk
    - 🔄 **Cross-channel Memory**: Seamless context across all channels
    - 🎨 **Style DNA**: Color analysis for personalized recommendations
    - 🤖 **7 AI Agents**: Recommendation, Inventory, Payment, Fulfillment, Loyalty, Post-Purchase
    
    ## Demo
    - WhatsApp: Message +1 415 523 8886 (join sandbox first)
    - Web Chat: Coming soon
    
    Built for EY Techathon by Aryan Ranjan, VIT Bhopal
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan
)


# ============== CORS Middleware ==============

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Register Routers ==============

app.include_router(chat_router, prefix="/api/v1")
app.include_router(whatsapp_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(color_router, prefix="/api/v1")


# ============== Root Endpoints ==============

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "name": "ARIA - Adaptive Retail Intelligence Assistant",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "message": "Welcome to ARIA! 🛍️ I'm your AI-powered fashion assistant."
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ARIA Backend",
        "version": settings.APP_VERSION
    }


# ============== Error Handlers ==============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error("Unhandled exception", 
                error=str(exc), 
                path=request.url.path)
    
    return {
        "error": "Internal server error",
        "message": "Something went wrong. Please try again."
    }


# ============== Run with Uvicorn ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )