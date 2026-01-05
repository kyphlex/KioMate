import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import json
import hashlib
import secrets

# Configure page
st.set_page_config(
    page_title="KioMate - Know Your Customers",
    page_icon="🎯",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    /* Main background - teal */
    .main {
        background: linear-gradient(135deg, #E0F2F1 0%, #B2DFDB 100%);
    }

    /* Buttons - orange */
    .stButton>button {
        background-color: #FF8C42;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #e67a2e;
    }

    /* Headers - teal */
    h1, h2, h3 {
        color: #008B8B;
    }

    /* Insight boxes - white with orange accent */
    .insight-box {
        background-color: teal;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #FF8C42;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Business ID box - gradient */
    .business-id-box {
        background: linear-gradient(135deg, #008B8B 0%, #FF8C42 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin: 2rem 0;
    }
    .business-id {
        font-size: 2rem;
        font-weight: bold;
        letter-spacing: 3px;
        font-family: monospace;
        margin: 1rem 0;
        background: rgba(255,255,255,0.2);
        padding: 1rem;
        border-radius: 8px;
    }

    /* Research badge - teal */
    .research-badge {
        background: #008B8B;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.5rem 0;
    }

    /* Logo styling */
    .logo {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .logo-kio {
        color: #008B8B;
    }
    .logo-mate {
        color: #FF8C42;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'insights_history' not in st.session_state:
    st.session_state.insights_history = []
if 'current_insights' not in st.session_state:
    st.session_state.current_insights = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'chat_mode' not in st.session_state:
    st.session_state.chat_mode = False


# Initialize Gemini with Google Search

client = genai.Client(api_key=st.secrets.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))
grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)
config = types.GenerateContentConfig(
    tools=[grounding_tool]
)


LAGOS_AREAS = {
    "Agege": "Agege",
    "Ajeromi-Ifelodun": "Ajeromi-Ifelodun",
    "Alimosho": "Alimosho",
    "Amuwo-Odofin": "Amuwo-Odofin",
    "Apapa": "Apapa",
    "Badagry": "Badagry",
    "Epe": "Epe",
    "Eti-Osa": "Eti-Osa",
    "Ibeju-Lekki": "Ibeju-Lekki",
    "Ifako-Ijaiye": "Ifako-Ijaiye",
    "Ikeja": "Ikeja",
    "Ikorodu": "Ikorodu",
    "Kosofe": "Kosofe",
    "Lagos Island": "Lagos Island",
    "Lagos Mainland": "Lagos Mainland",
    "Mushin": "Mushin",
    "Ojo": "Ojo",
    "Oshodi-Isolo": "Oshodi-Isolo",
    "Somolu": "Somolu",
    "Surulere": "Surulere"
}


def generate_business_id(business_name, business_type, location):
    """Generate unique 8-character business ID"""
    combined = f"{business_name}{business_type}{location}{secrets.token_hex(4)}".lower()
    hash_obj = hashlib.sha256(combined.encode())
    business_id = f"KM-{hash_obj.hexdigest()[:8].upper()}"
    return business_id


def save_user(business_id, business_name, business_type, location):
    """Save user data"""
    user_data = {
        'business_id': business_id,
        'business_name': business_name,
        'business_type': business_type,
        'location': location,
        'created_at': datetime.now().isoformat()
    }

    if 'users_db' not in st.session_state:
        st.session_state.users_db = {}

    st.session_state.users_db[business_id] = user_data
    return user_data


def get_user(business_id):
    """Retrieve user data by business ID"""
    if 'users_db' not in st.session_state:
        st.session_state.users_db = {}
    return st.session_state.users_db.get(business_id)


def generate_insights_with_search(business_type, location):
    """Generate insights using Gemini with Google Search for real-time data"""

    area_context = LAGOS_AREAS.get(location, "Lagos area")
    current_date = datetime.now().strftime("%B %d, %Y")

    prompt = f"""You are a Lagos business intelligence consultant operating on {current_date}. Use Google Search to find CURRENT, REAL information about {location}, Lagos, Nigeria.

Business Type: {business_type}
Location: {location}, Lagos, Nigeria
Area Context: {area_context}
Current Date: {current_date}

IMPORTANT: Search Google for:
1. Recent news and developments in {location}, Lagos (up to {current_date})
2. Current businesses and competition in {location}
3. Demographics and economic activity in {location}
4. Traffic patterns and busy areas in {location}
5. Recent trends affecting {business_type} businesses in Lagos

Based on your Google search findings and Lagos market knowledge, generate hyper-specific, actionable customer insights.

Return ONLY a valid JSON object (no markdown, no code blocks):
{{
    "customer_profile": "2-3 sentences describing typical customers based on REAL current data about {location}",
    "peak_hours": "Specific times based on actual traffic and activity patterns in {location}",
    "pricing_strategy": "Price sensitivity based on real economic data about the area",
    "quick_wins": [
        "Actionable tip 1 based on current trends you found",
        "Actionable tip 2 based on actual competition you discovered",
        "Actionable tip 3 based on real demographic insights"
    ],
    "competition_insight": "REAL information about actual businesses and competition in {location}",
    "growth_opportunity": "Specific opportunity based on current market gaps you found",
    "data_sources": "Brief note on what real data you found (e.g., 'Based on recent traffic data and business listings in {location}')"
}}

Use REAL, CURRENT information from your searches as of {current_date}. Be specific and cite what you found."""


    # Generate with search enabled
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config,
    )

    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    insights = json.loads(text.strip())

    # Add metadata
    insights['search_enabled'] = True
    insights['generated_at'] = datetime.now().isoformat()

    return insights


def chat_with_insights(user_message, insights, business_type, location):
    """Chat with AI about the generated insights"""
    current_date = datetime.now().strftime("%B %d, %Y")

    prompt = f"""You are a Lagos business consultant chatting with a business owner on {current_date}. 

Business Context:
- Business Type: {business_type}
- Location: {location}, Lagos
- Current Date: {current_date}

Their Business Insights:
{json.dumps(insights, indent=2)}

Chat History:
{json.dumps(st.session_state.chat_messages[-6:], indent=2) if st.session_state.chat_messages else "No previous messages"}

Business Owner's Question: {user_message}

Respond conversationally and helpfully. Use Google Search if you need current information about Lagos, {location}, or {business_type} businesses. Reference their specific insights when relevant. Keep responses concise (2-4 paragraphs max). Be practical and actionable.

If they ask about implementing the insights, give specific Lagos-based advice. If they mention competitors or challenges, offer realistic solutions."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config,
    )

    return response.text.strip()


def signup_page():
    """Sign up page"""
    st.markdown("<div class='logo'><span class='logo-kio'>Kio</span><span class='logo-mate'>Mate</span> 🎯</div>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #008B8B; font-weight: 500;'>Tell us about your business, get your unique Business ID</p>",
        unsafe_allow_html=True)

    st.markdown("---")

    # Check if user just signed up
    if 'just_signed_up' in st.session_state and st.session_state.just_signed_up:
        user_data = st.session_state.new_user_data

        st.success("✨ Your business is registered!")

        st.markdown(f"""
            <div class='business-id-box'>
                <h2>Your Business ID</h2>
                <div class='business-id'>{user_data['business_id']}</div>
                <p style='margin-top: 1rem;'>Save this ID! Use it to login anytime.</p>
                <p style='font-size: 0.9rem; opacity: 0.9;'>📱 Screenshot this or write it down</p>
            </div>
        """, unsafe_allow_html=True)

        st.info(
            "💡 **Tip:** This ID is unique to your business. Anyone with this ID can access your insights, so keep it safe!")

        if st.button("Continue to Dashboard", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_data = user_data
            st.session_state.just_signed_up = False
            st.rerun()
    else:
        # Show signup form
        with st.form("signup_form"):
            business_name = st.text_input(
                "Business Name",
                placeholder="e.g., Tunde's Fashion Store"
            )

            col1, col2 = st.columns(2)
            with col1:
                business_type = st.text_input(
                    "What do you sell?",
                    placeholder="e.g., Shoes, Food, Phones"
                )

            with col2:
                location = st.selectbox(
                    "Where in Lagos?",
                    options=[""] + sorted(LAGOS_AREAS.keys()),
                    format_func=lambda x: "Select location..." if x == "" else x
                )

            submit = st.form_submit_button("🚀 Create My Business ID", use_container_width=True)

            if submit:
                if not business_name or not business_type or not location:
                    st.error("Please fill in all fields")
                else:
                    business_id = generate_business_id(business_name, business_type, location)
                    user_data = save_user(business_id, business_name, business_type, location)

                    # Store in session state and trigger rerun
                    st.session_state.just_signed_up = True
                    st.session_state.new_user_data = user_data
                    st.rerun()

        st.markdown("---")

        if st.button("← I have a Business ID", use_container_width=True):
            st.session_state.show_login = True
            st.rerun()


def login_page():
    """Login page"""
    st.markdown("<div class='logo'><span class='logo-kio'>Kio</span><span class='logo-mate'>Mate</span> 🎯</div>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #008B8B; font-weight: 500;'>Enter your Business ID to continue</p>",
        unsafe_allow_html=True)

    st.markdown("---")

    business_id = st.text_input(
        "Business ID",
        placeholder="e.g., KM-A1B2C3D4",
        max_chars=12
    ).upper()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔓 Access Dashboard", use_container_width=True):
            if len(business_id) != 12:
                st.error("Business ID must be 8 characters")
            else:
                user_data = get_user(business_id)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user_data = user_data
                    st.success(f"Welcome back, {user_data['business_name']}!")
                    st.rerun()
                else:
                    st.error("Business ID not found. Please check and try again.")

    st.markdown("---")

    if st.button("← Create New Business ID", use_container_width=True):
        st.session_state.show_login = False
        st.rerun()


def dashboard_page():
    """Main dashboard after login"""
    user = st.session_state.user_data

    # Header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<h1 style='color: #008B8B;'>👋 {user['business_name']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #666;'>{user['business_type']} • {user['location']}</p>", unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.rerun()

    st.markdown("---")

    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Business ID", user['business_id'])
    with col2:
        st.metric("Location", user['location'])
    with col3:
        st.metric("Insights Generated", len(st.session_state.insights_history))

    st.markdown("---")

    # Generate new insights section
    st.markdown("### 🔍 Generate Fresh Insights")
    st.markdown("<span class='research-badge'>🌐 Powered by Real-Time Google Search</span>", unsafe_allow_html=True)
    st.caption("We'll search Google for current information about your location to give you the most accurate insights")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ Generate Live Insights", use_container_width=True):
            with st.spinner(f"🔍 Searching Google for real data about {user['location']}..."):
                try:
                    insights = generate_insights_with_search(user['business_type'], user['location'])

                    # Save to history and set as current
                    st.session_state.insights_history.append(insights)
                    st.session_state.current_insights = insights
                    st.session_state.chat_mode = False
                    st.session_state.chat_messages = []  # Reset chat

                    st.rerun()

                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")
                    st.info("💡 Tip: Make sure your Gemini API key has access to Google Search features")

    # Show insights if available
    if st.session_state.current_insights:
        insights = st.session_state.current_insights

        # Display insights
        st.success("✨ Fresh insights generated from live data!")

        # Show data source info
        if 'data_sources' in insights:
            st.info(f"📊 {insights['data_sources']}")

        st.markdown("### 👥 Your Customers")
        st.markdown(f"<div class='insight-box'>{insights['customer_profile']}</div>",
                    unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ⏰ Peak Hours")
            st.markdown(f"<div class='insight-box'>{insights['peak_hours']}</div>",
                        unsafe_allow_html=True)

        with col2:
            st.markdown("### 💰 Pricing Strategy")
            st.markdown(f"<div class='insight-box'>{insights['pricing_strategy']}</div>",
                        unsafe_allow_html=True)

        st.markdown("### 🎯 Quick Wins - Do These Today!")
        for i, tip in enumerate(insights['quick_wins'], 1):
            st.markdown(f"<div class='insight-box'><strong>{i}.</strong> {tip}</div>",
                        unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🏪 Competition")
            st.markdown(f"<div class='insight-box'>{insights['competition_insight']}</div>",
                        unsafe_allow_html=True)

        with col2:
            st.markdown("### 📈 Growth Opportunity")
            st.markdown(f"<div class='insight-box'>{insights['growth_opportunity']}</div>",
                        unsafe_allow_html=True)

        # Export and Chat options
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            report_text = f"""KIOMATE BUSINESS INSIGHTS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Based on: Real-time Google Search data

Business: {user['business_name']}
Type: {user['business_type']}
Location: {user['location']}, Lagos
Business ID: {user['business_id']}

CUSTOMER PROFILE:
{insights['customer_profile']}

PEAK HOURS:
{insights['peak_hours']}

PRICING STRATEGY:
{insights['pricing_strategy']}

QUICK WINS:
1. {insights['quick_wins'][0]}
2. {insights['quick_wins'][1]}
3. {insights['quick_wins'][2]}

COMPETITION:
{insights['competition_insight']}

GROWTH OPPORTUNITY:
{insights['growth_opportunity']}

DATA SOURCE:
{insights.get('data_sources', 'Based on real-time market research')}

---
Powered by KioMate with Google Search
"""

            st.download_button(
                label="📥 Download Report",
                data=report_text,
                file_name=f"kiomate_{user['business_id']}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:
            if st.button("💬 Ask Questions About These Insights", use_container_width=True):
                st.session_state.chat_mode = True
                st.rerun()

        # Chat interface
        if st.session_state.chat_mode:
            st.markdown("---")
            st.markdown("### 💬 Chat with Your Business Consultant")
            st.caption("Ask questions about your insights or get advice on implementing them")

            # Display chat history
            for message in st.session_state.chat_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input
            if prompt := st.chat_input("Ask a question about your business insights..."):
                # Add user message
                st.session_state.chat_messages.append({"role": "user", "content": prompt})

                with st.chat_message("user"):
                    st.markdown(prompt)

                # Get AI response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = chat_with_insights(
                            prompt,
                            insights,
                            user['business_type'],
                            user['location']
                        )
                        st.markdown(response)

                # Add assistant message
                st.session_state.chat_messages.append({"role": "assistant", "content": response})

            if st.button("← Back to Insights", use_container_width=True):
                st.session_state.chat_mode = False
                st.rerun()

    # Show previous insights if any
    if st.session_state.insights_history:
        st.markdown("---")
        st.markdown("### 📊 Previous Insights")
        with st.expander(f"View {len(st.session_state.insights_history)} previous insight(s)"):
            for idx, past_insight in enumerate(reversed(st.session_state.insights_history), 1):
                st.markdown(f"**Insight #{idx}** - Generated {past_insight.get('generated_at', 'recently')}")
                st.caption(f"✓ {past_insight.get('customer_profile', '')[:100]}...")


def main():
    """Main app logic"""

    if not st.session_state.logged_in:
        if 'show_login' not in st.session_state:
            st.session_state.show_login = False

        if st.session_state.show_login:
            login_page()
        else:
            signup_page()
    else:
        dashboard_page()

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #008B8B; font-size: 0.9rem; font-weight: 500;'>🇳🇬 Built for Lagos SMEs | 🌐 Powered by Real-Time Google Search</p>",
        unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 0.85rem;'><span style='color: #008B8B; font-weight: bold;'>Kio</span><span style='color: #FF8C42; font-weight: bold;'>Mate</span> © 2026</p>",
        unsafe_allow_html=True)


if __name__ == "__main__":
    main()