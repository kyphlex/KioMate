# 🎯 Kiomate

> Helping Lagos SMEs know their customers better, earn more, and grow smarter.

Kiomate uses AI-powered insights with real-time Google Search to help small and medium enterprises in Lagos understand their local market, competition, and customers - all based on their specific location.

## 🌟 Features

- **🌐 Real-Time Location Intelligence**: Google Search integration for current, accurate market data
- **🔐 Passwordless Authentication**: Simple Business ID system - no emails, no passwords to forget
- **📊 Actionable Insights**: Customer profiles, peak hours, pricing strategies, and quick wins
- **🎯 Lagos-Focused**: Deep knowledge of Lagos neighborhoods and market dynamics
- **💾 Insight History**: Track and compare insights over time
- **📥 Export Reports**: Download insights as text files for offline use
- **🚀 API Backend**: Ready for fintech integrations (PayStack, Flutterwave, etc.)

## 🎨 Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **AI Model**: Google Gemini 2.0 Flash with Google Search grounding
- **Database**: SQLite (MVP) / PostgreSQL (Production)
- **API**: FastAPI (for fintech integrations)
- **Deployment**: Streamlit Cloud / Railway / Render

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/kiomate.git
cd kiomate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup your API key**

Create `.streamlit/secrets.toml`:
```bash
mkdir .streamlit
touch .streamlit/secrets.toml
```

Add your Gemini API key to `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

4. **Run the app**
```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

## 📦 Requirements

Create `requirements.txt` with:
```txt
streamlit>=1.29.0
google-generativeai>=0.3.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6
```

## 🎯 How It Works

### For SME Users

1. **Sign Up**: Enter business name, type, and Lagos location
2. **Get Business ID**: Receive a unique 8-character ID (e.g., `A1B2C3D4`)
3. **Generate Insights**: AI searches Google for real-time data about your area
4. **Take Action**: Get specific recommendations you can implement today

### Authentication Flow

- **No passwords required**: Users login with their Business ID
- **Easy to remember**: Just 8 characters to write down or screenshot
- **Shareable**: Business owners can share ID with partners/employees

### Example Business ID Flow

```
Sign Up:
Business: "Tunde's Shoe Store"
Type: "Shoes"
Location: "Ikeja"
↓
Generate ID: "A1B2C3D4"
↓
Login Anytime: Just enter "A1B2C3D4"
```

## 🌐 API for Fintechs

Kiomate provides a REST API for fintech partners to integrate location intelligence into their platforms.

### Run the API Backend

```bash
uvicorn api_backend:app --reload
```

API docs available at: `http://localhost:8000/docs`

### Example API Usage

```bash
curl -X POST "http://localhost:8000/insights" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "Restaurant",
    "location": "Lekki"
  }'
```


## 📍 Supported Lagos Areas

- Ikeja (Computer Village, commercial hub)
- Lekki (upscale residential, tech)
- Victoria Island (business district)
- Yaba (tech hub, students)
- Surulere (established residential)
- Oshodi (transport hub, high traffic)
- Ikorodu (suburban, family-oriented)
- Ajah (rapidly developing)
- Maryland (commercial & residential)
- Festac (large residential estate)
- Gbagada, Alaba, Apapa, Mushin, Lagos Island
>It's capable of generating insights for anywhere in Lagos, but these are the major areas for now...

## 🚀 Deployment

### Streamlit Cloud (Recommended for MVP)

1. Push code to GitHub
2. Connect repository at [streamlit.io/cloud](https://streamlit.io/cloud)
3. Add secrets in dashboard:
   ```toml
   GEMINI_API_KEY = "your_key"
   ```
4. Deploy!

### Production Deployment

For production with permanent data storage:

**Option 1: Railway**
- Supports PostgreSQL addon
- Easy environment variables
- Auto-deploy from GitHub

**Option 2: Render**
- Free PostgreSQL database
- Auto-scaling available
- Simple deployment process

**Option 3: Self-hosted**
- Use any VPS (DigitalOcean, Linode, etc.)
- Setup PostgreSQL
- Use nginx as reverse proxy

## 🗄️ Database Migration (MVP → Production)

The MVP uses session state. For production, use the included `database.py`:

```python
from database import save_user, get_user, save_insight, get_user_insights

# Replace session state calls with database functions
```

Then setup PostgreSQL and update connection string in `database.py`.

## 🔒 Security Best Practices

- ✅ Never commit `secrets.toml` to Git
- ✅ Use environment variables in production
- ✅ Add rate limiting to API endpoints
- ✅ Implement proper API key management
- ✅ Use HTTPS in production
- ✅ Regularly rotate API keys

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

### Phase 1 (MVP) ✅
- [x] Basic Streamlit interface
- [x] Passwordless authentication
- [x] Google Search integration
- [x] Insight generation
- [x] Export functionality

### Phase 2 (Q1 2026)
- [ ] PostgreSQL database
- [ ] User analytics dashboard
- [ ] WhatsApp Business integration
- [ ] More Lagos areas
- [ ] Industry-specific insights

### Phase 3 (Q2 2026)
- [ ] Fintech API partnerships
- [ ] Payment integration (Paystack)
- [ ] Competitor tracking
- [ ] Seasonal trend analysis
- [ ] Mobile app (React Native)

### Phase 4 (Q3 2026)
- [ ] Expand to other Nigerian cities
- [ ] Enterprise features
- [ ] White-label options
- [ ] Advanced analytics
- [ ] AI-powered recommendations

## 💼 For Fintech Partners

Interested in integrating Kiomate's location intelligence into your platform?

- **Email**: ayineuna@gmail.com (for now 😅)
- **Use Cases**: Merchant dashboards, lending risk assessment, POS optimization
- **Integration Time**: ~2 weeks
- **Documentation**: Available at `/docs` endpoint

## 📞 Support

- **Documentation**: [Full setup guide](./SETUP.md)
- **Issues**: [GitHub Issues](https://github.com/kyphlex/kiomate/issues)
- **Email**: ayineuna@gmail.com (for now 😅)

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Powered by [Google Gemini](https://ai.google.dev/)
- Designed for Lagos SMEs 🇳🇬

## 📊 Project Stats

- **Lines of Code**: ~800
- **Supported Areas**: 15+ Lagos locations
- **API Endpoints**: 5
- **Average Response Time**: <3 seconds
- **Languages**: Python (100%)

---

<p align="center">
  <strong>Built with ❤️ for Lagos entrepreneurs</strong>
  <br>
  <sub>Helping SMEs grow one insight at a time</sub>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#deployment">Deployment</a> •
  <a href="#support">Support</a>
</p>
