"""Main API endpoint (FastAPI)."""

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from .schema import EvaluateHandRequest, EvaluateHandResponse, DecisionRequest, DecisionResponse
    from .service import PokerAIService
    
    app = FastAPI(title="Poker AI API", version="0.1.0")
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    service = PokerAIService()
    
    @app.post("/evaluate", response_model=EvaluateHandResponse)
    async def evaluate_hand(request: EvaluateHandRequest):
        """Evaluate a hand against a range."""
        return service.evaluate_hand(request)
    
    @app.post("/decision", response_model=DecisionResponse)
    async def get_decision(request: DecisionRequest):
        """Get a decision recommendation."""
        return service.get_decision(request)
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

except ImportError:
    # FastAPI not installed - create a placeholder
    app = None
    print("FastAPI not installed. Install with: pip install fastapi uvicorn")

