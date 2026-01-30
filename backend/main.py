from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import google.generativeai as genai
from datetime import datetime
import json
import os
import hashlib
import secrets
import sqlite3
from contextlib import contextmanager

app = FastAPI(
    title="KioMate API",
    description="Location-based business intelligence for Nigerian SMEs",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://kiomate.netlify.app",  # Production frontend
        "https://*.netlify.app",  # Netlify preview deploys
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash', tools='google_search_retrieval')

# Database setup
DATABASE_PATH = "kiomate.db"


@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize database tables"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Businesses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS businesses (
                business_id TEXT PRIMARY KEY,
                business_name TEXT NOT NULL,
                business_type TEXT NOT NULL,
                state TEXT NOT NULL,
                area TEXT,
                contact TEXT,
                created_at TEXT NOT NULL,
                last_active TEXT
            )
        """)

        # Insights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT,
                business_type TEXT NOT NULL,
                state TEXT NOT NULL,
                area TEXT,
                insight_data TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                FOREIGN KEY (business_id) REFERENCES businesses(business_id)
            )
        """)

        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT,
                session_id TEXT,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        # Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                business_id TEXT,
                metadata TEXT,
                timestamp TEXT NOT NULL
            )
        """)

        conn.commit()


# Initialize database on startup
init_database()

# Nigerian locations
with open('nigerian-states.json', 'r') as file:
    NIGERIA_LOCATIONS = json.load(file)



# Pydantic Models
class InsightRequest(BaseModel):
    business_type: str = Field(..., description="Type of business")
    state: str = Field(..., description="Nigerian state")
    area: Optional[str] = Field(None, description="Specific area/LGA within state")


class InsightResponse(BaseModel):
    peak_hours: str
    competition: str
    price_sensitivity: str
    quick_wins: List[str]
    customer_profile: str
    competitive_landscape: str
    growth_opportunity: str
    data_note: str
    generated_at: str


class ChatRequest(BaseModel):
    message: str
    business_type: str
    state: str
    area: Optional[str]
    insight_data: dict
    session_id: Optional[str]


class ChatResponse(BaseModel):
    response: str
    session_id: str


class SaveBusinessRequest(BaseModel):
    business_name: str
    business_type: str
    state: str
    area: Optional[str]
    contact: Optional[str]


class SaveBusinessResponse(BaseModel):
    business_id: str
    message: str


# Helper Functions
def generate_insights_internal(business_type: str, state: str, area: Optional[str]) -> dict:
    """Generate insights using Gemini"""
    current_date = datetime.now().strftime("%B %d, %Y")
    location_str = f"{area}, {state}" if area else state

    prompt = f"""You are analyzing a business environment in Nigeria as of {current_date}.

Business Type: {business_type}
Location: {location_str}, Nigeria

Use Google Search to find CURRENT information about this location and business type in Nigeria.

Generate insights in this EXACT JSON format (no markdown, no code blocks):
{{
    "peak_hours": "One clear sentence about when business is busiest in this area",
    "competition": "One sentence: HIGH/MEDIUM/LOW competition and why",
    "price_sensitivity": "One sentence about customer price expectations in this area",
    "quick_wins": [
        "Specific action they can take this week based on local market",
        "Another immediate opportunity relevant to {location_str}",
        "Third actionable recommendation for {business_type} in this area"
    ],
    "customer_profile": "2-3 sentences about typical customers in {location_str}",
    "competitive_landscape": "What the competition looks like for {business_type} in {location_str}",
    "growth_opportunity": "One specific untapped opportunity for this business type in {location_str}",
    "data_note": "Brief note on data sources (e.g., 'Based on recent market data for {location_str}')"
}}

Be specific to {location_str} and {business_type}. Use real, current data from Nigeria."""

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Clean JSON
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    return json.loads(text.strip())


def track_event(event_type: str, business_id: Optional[str] = None, metadata: Optional[dict] = None):
    """Track analytics events"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analytics (event_type, business_id, metadata, timestamp)
                VALUES (?, ?, ?, ?)
            """, (event_type, business_id, json.dumps(metadata) if metadata else None, datetime.now().isoformat()))
            conn.commit()
    except:
        pass  # Don't fail if analytics fails


# API Endpoints

@app.get("/")
def root():
    """API health check"""
    return {
        "service": "KioMate API",
        "status": "active",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/locations")
def get_locations():
    """Get all supported Nigerian locations"""
    return {
        "states": list(NIGERIA_LOCATIONS.keys()),
        "locations": NIGERIA_LOCATIONS
    }


@app.post("/insights/generate", response_model=InsightResponse)
def generate_insights(request: InsightRequest):
    """
    Generate business insights for a specific location.
    This is the main endpoint - no authentication required.
    """
    try:
        # Track event
        track_event("insight_generated", metadata={
            "business_type": request.business_type,
            "state": request.state,
            "area": request.area
        })

        # Generate insights
        insights = generate_insights_internal(request.business_type, request.state, request.area)

        # Save to database (anonymous if no business_id)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO insights (business_type, state, area, insight_data, generated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (request.business_type, request.state, request.area,
                  json.dumps(insights), datetime.now().isoformat()))
            conn.commit()

        return InsightResponse(
            **insights,
            generated_at=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
def chat_with_insights(request: ChatRequest):
    """
    Chat about generated insights.
    Contextual to the business and location.
    """
    try:
        current_date = datetime.now().strftime("%B %d, %Y")
        location_str = f"{request.area}, {request.state}" if request.area else request.state

        # Generate or use existing session ID
        session_id = request.session_id or secrets.token_hex(8)

        # Get recent chat history for this session
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, message FROM chat_history 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 6
            """, (session_id,))
            history = [dict(row) for row in cursor.fetchall()]

        prompt = f"""You are a Nigerian business advisor chatting on {current_date}.

Business Context:
- Type: {request.business_type}
- Location: {location_str}

Their Insights:
{json.dumps(request.insight_data, indent=2)}

Recent Chat:
{json.dumps(history[-4:], indent=2) if history else "No previous messages"}

User Question: {request.message}

Respond in 2-3 short paragraphs. Be specific, practical, and reference their insights. 
Use Google Search if you need current information about Nigeria, {location_str}, or {request.business_type} businesses.
Keep responses conversational and actionable."""

        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Save chat to database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (session_id, role, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, "user", request.message, datetime.now().isoformat()))
            cursor.execute("""
                INSERT INTO chat_history (session_id, role, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, "assistant", response_text, datetime.now().isoformat()))
            conn.commit()

        # Track event
        track_event("chat_message", metadata={"session_id": session_id})

        return ChatResponse(response=response_text, session_id=session_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/business/save", response_model=SaveBusinessResponse)
def save_business(request: SaveBusinessRequest):
    """
    Save a business for future access.
    Generates a unique Business ID.
    """
    try:
        # Generate unique business ID
        combined = f"{request.business_name}{request.business_type}{request.state}{secrets.token_hex(4)}"
        business_id = hashlib.sha256(combined.encode()).hexdigest()[:8].upper()

        # Save to database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO businesses 
                (business_id, business_name, business_type, state, area, contact, created_at, last_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (business_id, request.business_name, request.business_type,
                  request.state, request.area, request.contact,
                  datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()

        # Track event
        track_event("business_saved", business_id=business_id)

        return SaveBusinessResponse(
            business_id=business_id,
            message="Business saved successfully! Save this ID to access your insights anytime."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving business: {str(e)}")


@app.get("/business/{business_id}")
def get_business(business_id: str):
    """Get business details by ID"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM businesses WHERE business_id = ?", (business_id,))
            business = cursor.fetchone()

            if not business:
                raise HTTPException(status_code=404, detail="Business not found")

            # Update last active
            cursor.execute("""
                UPDATE businesses SET last_active = ? WHERE business_id = ?
            """, (datetime.now().isoformat(), business_id))
            conn.commit()

            return dict(business)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/summary")
def get_analytics_summary():
    """Get high-level analytics (public, no auth required for MVP)"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            # Total insights generated
            cursor.execute("SELECT COUNT(*) as count FROM insights")
            total_insights = cursor.fetchone()['count']

            # Total businesses saved
            cursor.execute("SELECT COUNT(*) as count FROM businesses")
            total_businesses = cursor.fetchone()['count']

            # Total chat messages
            cursor.execute("SELECT COUNT(*) as count FROM chat_history WHERE role = 'user'")
            total_chats = cursor.fetchone()['count']

            # Most popular states
            cursor.execute("""
                SELECT state, COUNT(*) as count 
                FROM insights 
                GROUP BY state 
                ORDER BY count DESC 
                LIMIT 5
            """)
            popular_states = [dict(row) for row in cursor.fetchall()]

            return {
                "total_insights_generated": total_insights,
                "total_businesses_saved": total_businesses,
                "total_chat_messages": total_chats,
                "popular_states": popular_states
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# For local testing
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)