from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import google.generativeai as genai
import json
import os
from datetime import datetime
import hashlib


# Initialize FastAPI
app = FastAPI(
    title="Kiomate API",
    description="Customer insights API for Lagos SMEs",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# Lagos area context
LAGOS_AREAS = {
    "Ikeja": "Commercial hub, offices, Computer Village tech market, middle to upper-middle class",
    "Lekki": "Upscale residential, young professionals, expats, high purchasing power",
    "Surulere": "Established residential, mixed income, strong community, price-conscious",
    "Oshodi": "Transport hub, very high foot traffic, price-sensitive, bulk buyers",
    "Victoria Island": "Business district, high-end clientele, corporate workers, premium pricing",
    "Yaba": "Tech hub, students, startups, young demographics, value for money",
    "Ikorodu": "Suburban, family-oriented, growing middle class, value-conscious",
    "Ajah": "Rapidly developing, young families, commuters, competitive pricing",
    "Maryland": "Commercial, residential mix, consistent foot traffic, middle class",
    "Festac": "Large residential, community-focused, diverse demographics"
}


# Pydantic models
class InsightRequest(BaseModel):
    business_type: str = Field(..., description="Type of business", example="Shoe store")
    location: str = Field(..., description="Lagos area", example="Ikeja")
    api_key: Optional[str] = Field(None, description="Optional API key for authentication")


class QuickWin(BaseModel):
    action: str
    impact: str


class InsightResponse(BaseModel):
    business_type: str
    location: str
    customer_profile: str
    peak_hours: str
    pricing_strategy: str
    quick_wins: List[str]
    competition_insight: str
    growth_opportunity: str
    generated_at: str


class BatchInsightRequest(BaseModel):
    businesses: List[InsightRequest] = Field(..., max_items=5)


class APIKeyRequest(BaseModel):
    company_name: str
    email: str
    use_case: str


# Simple API key validation (use proper DB in production)
VALID_API_KEYS = {
    "demo_key_123": {"company": "Demo Company", "requests_remaining": 100},
    # Add more keys here or use a database
}


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key for fintech partners"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required. Contact us for access.")

    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")

    key_data = VALID_API_KEYS[x_api_key]
    if key_data["requests_remaining"] <= 0:
        raise HTTPException(status_code=429, detail="API quota exceeded")

    # Decrement requests (use proper tracking in production)
    key_data["requests_remaining"] -= 1

    return key_data


def generate_insights_internal(business_type: str, location: str) -> dict:
    """Internal function to generate insights"""

    area_context = LAGOS_AREAS.get(location, "Mixed commercial and residential area in Lagos")

    prompt = f"""You are a Lagos business consultant with deep knowledge of local markets.

Business Type: {business_type}
Location: {location}, Lagos
Area Context: {area_context}

Generate hyper-specific, actionable customer insights for this business. Be realistic about Lagos market dynamics, traffic patterns, customer behavior, and local competition.

Return ONLY a valid JSON object with this exact structure (no markdown, no code blocks):
{{
    "customer_profile": "2-3 sentences describing typical customers in this location",
    "peak_hours": "Specific times when business is likely busiest",
    "pricing_strategy": "How price-sensitive customers are and recommended approach",
    "quick_wins": [
        "Actionable tip 1 they can implement immediately",
        "Actionable tip 2 they can implement immediately",
        "Actionable tip 3 they can implement immediately"
    ],
    "competition_insight": "What the competitive landscape looks like",
    "growth_opportunity": "One specific opportunity to increase revenue"
}}

Be specific to {location} and {business_type}. Use local Lagos knowledge."""

    response = model.generate_content(prompt)

    # Parse response
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    return json.loads(text.strip())


# Endpoints

@app.get("/")
def root():
    """API health check"""
    return {
        "service": "Kiomate API",
        "status": "active",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/areas")
def list_areas():
    """Get list of supported Lagos areas"""
    return {
        "areas": list(LAGOS_AREAS.keys()),
        "total": len(LAGOS_AREAS)
    }


@app.post("/insights", response_model=InsightResponse)
def generate_insights(
        request: InsightRequest,
        key_data: dict = Depends(verify_api_key)
):
    """
    Generate customer insights for a specific business and location.

    Requires API key in X-API-Key header.
    """
    try:
        insights = generate_insights_internal(request.business_type, request.location)

        return InsightResponse(
            business_type=request.business_type,
            location=request.location,
            customer_profile=insights["customer_profile"],
            peak_hours=insights["peak_hours"],
            pricing_strategy=insights["pricing_strategy"],
            quick_wins=insights["quick_wins"],
            competition_insight=insights["competition_insight"],
            growth_opportunity=insights["growth_opportunity"],
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@app.post("/insights/batch")
def generate_batch_insights(
        request: BatchInsightRequest,
        key_data: dict = Depends(verify_api_key)
):
    """
    Generate insights for multiple businesses (max 5 per request).

    Requires API key in X-API-Key header.
    """
    results = []
    errors = []

    for idx, business in enumerate(request.businesses):
        try:
            insights = generate_insights_internal(business.business_type, business.location)
            results.append({
                "index": idx,
                "business_type": business.business_type,
                "location": business.location,
                "insights": insights
            })
        except Exception as e:
            errors.append({
                "index": idx,
                "business_type": business.business_type,
                "error": str(e)
            })

    return {
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


@app.post("/request-access")
def request_api_access(request: APIKeyRequest):
    """
    Request API access (for fintechs and partners).

    In production, this would trigger an email or store in DB for approval.
    """
    # Generate a demo key (use proper key generation in production)
    key_hash = hashlib.sha256(f"{request.email}{datetime.now()}".encode()).hexdigest()[:16]

    return {
        "message": "API access request received",
        "company": request.company_name,
        "email": request.email,
        "status": "pending_approval",
        "note": "You'll receive your API key via email within 24 hours"
    }


@app.get("/usage")
def check_usage(key_data: dict = Depends(verify_api_key)):
    """Check API usage for the authenticated key"""
    return {
        "company": key_data["company"],
        "requests_remaining": key_data["requests_remaining"]
    }


# For local testing
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)