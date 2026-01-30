# 🎯 KioMate

> Location-based business intelligence for Nigerian SMEs

KioMate uses AI-powered insights with real-time Google Search to help small and medium enterprises across Nigeria understand their local market, competition, and customers.

## 🌟 What Makes KioMate Different

- **🇳🇬 Nigeria-Wide Coverage:** All major states and cities
- **🌐 Real-Time Intelligence:** Google Search integration for current market data
- **🎯 Discovery-First Design:** Value before signup, guidance before data
- **⚡ Instant Insights:** Get actionable recommendations in under 60 seconds
- **💬 Contextual AI Chat:** Ask questions specific to YOUR business
- **🔐 Simple Auth:** No passwords - just a Business ID
- **🚀 API-First:** Ready for fintech integrations

## 🏗️ Tech Stack

### Backend (Render)
- **Framework:** FastAPI (Python)
- **AI Model:** Google Gemini 2.0 Flash with Search Grounding
- **Database:** SQLite (MVP) / PostgreSQL (Production)
- **API Docs:** Auto-generated with Swagger/OpenAPI

### Frontend (Netlify)
- **Pure HTML/CSS/JavaScript** - No frameworks, lightning fast
- **Responsive Design** - Works on all devices
- **Offline-Ready** - Progressive enhancement

### Deployment
- **Backend:** Render (Free tier with auto-deploy)
- **Frontend:** Netlify (Free tier with auto-deploy)
- **Domain:** Custom domain support
- **SSL:** Auto HTTPS on both platforms

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.8+
- Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Backend Setup

```bash
# Clone repo
git clone https://github.com/yourusername/kiomate.git
cd kiomate/backend

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GEMINI_API_KEY="your_gemini_api_key"

# Run backend
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd ../frontend

# Just open in browser (no build needed!)
open index.html

# Or use a simple server
python -m http.server 3000
```

Frontend runs at: `http://localhost:3000`

## 📦 Deployment

### Deploy Backend to Render

1. Push code to GitHub
2. Go to [Render.com](https://render.com)
3. New Web Service → Connect repo
4. Set environment variable: `GEMINI_API_KEY`
5. Deploy!

Your API: `https://kiomate-api.onrender.com`

### Deploy Frontend to Netlify

1. Update API_URL in `index.html` to your Render URL
2. Go to [Netlify](https://netlify.com)
3. Drag and drop `frontend/` folder
4. Done!

Your site: `https://kiomate.netlify.app`

**Full deployment guide:** See [DEPLOYMENT.md](./DEPLOYMENT.md)

## 🎯 Product Philosophy

KioMate follows a **discovery-first** approach:

1. **Value before signup** - Try it instantly, save later
2. **Guidance before data** - Clear next steps, no overwhelm
3. **Confidence before accuracy** - Better to be helpful than perfect
4. **Learning before scale** - Understand users before adding features

## 🔌 API Endpoints

### Generate Insights
```bash
POST /insights/generate
{
  "business_type": "Restaurant",
  "state": "Lagos",
  "area": "Ikeja"
}
```

### Chat About Insights
```bash
POST /chat
{
  "message": "How can I compete better?",
  "business_type": "Restaurant",
  "state": "Lagos",
  "area": "Ikeja",
  "insight_data": {...}
}
```

### Save Business
```bash
POST /business/save
{
  "business_name": "Tunde's Restaurant",
  "business_type": "Restaurant",
  "state": "Lagos",
  "area": "Ikeja"
}
```

Full API docs: `https://kiomate-api.onrender.com/docs`

## 🎨 User Flow

```
Landing (No Login Required)
    ↓
Generate Insights (AI + Google Search)
    ↓
View Insights (Peak hours, competition, pricing, quick wins)
    ↓
    ├─→ Ask Questions (Contextual AI chat)
    └─→ Save Business (Get Business ID)
```

## 📍 Supported Locations

Currently covering **8 Nigerian states** with **60+ specific areas:**

- Lagos (15 areas)
- Abuja (8 areas)
- Rivers (4 areas)
- Kano (4 areas)
- Oyo (4 areas)
- Kaduna (4 areas)
- Enugu (4 areas)
- Anambra (4 areas)

**Expanding nationwide!**

## 💡 For Fintech Partners

KioMate provides a REST API for easy integration:

- **Merchant Dashboards:** Show location insights to your sellers
- **Lending Platforms:** Use insights for risk assessment
- **POS Providers:** Help agents optimize their territories
- **SME Banking:** Add value to business accounts

**Interested?** Email: partnerships@kiomate.ng

## 📊 Metrics We Track

- Insights generated
- Chat engagement
- Businesses saved
- Popular locations
- Popular business types

**Privacy:** All analytics are anonymous unless user saves their business.

## 🗺️ Roadmap

### ✅ Phase 1: MVP (Current)
- [x] Nigeria-wide coverage
- [x] Real-time insights
- [x] Contextual chat
- [x] Business saving
- [x] API backend
- [x] Production deployment

### 🚧 Phase 2: Engagement (Next 2 Months)
- [ ] Weekly insight emails
- [ ] Competitor alerts
- [ ] Progress tracking
- [ ] Success stories feed
- [ ] WhatsApp notifications

### 📱 Phase 3: Mobile App (Months 3-6)
- [ ] React Native app
- [ ] Push notifications
- [ ] Offline mode
- [ ] Camera features
- [ ] Voice input

### 💰 Phase 4: Monetization (Months 4-6)
- [ ] Pro tier (₦5k/month)
- [ ] Business tier (₦15k/month)
- [ ] Fintech partnerships
- [ ] White-label options

### 🌍 Phase 5: Expansion (Months 6-12)
- [ ] All Nigerian cities
- [ ] Ghana, Kenya, South Africa
- [ ] Industry-specific insights
- [ ] Multi-language support

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

**Areas we need help:**
- Improving insight quality
- Adding more Nigerian locations
- Better UI/UX
- Performance optimization
- Documentation

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com)
- Powered by [Google Gemini](https://ai.google.dev)
- Deployed on [Render](https://render.com) & [Netlify](https://netlify.com)
- Designed for Nigerian entrepreneurs 🇳🇬

## 💼 Business Model

### Free Tier (Always Free)
- 1 insight per week
- Basic chat
- All locations
- Business saving

### Pro Tier (Coming Soon - ₦5,000/month)
- Unlimited insights
- Unlimited chat
- Competitor alerts
- Weekly reports
- Priority support

### API Tier (For Fintechs - Custom Pricing)
- Volume-based pricing
- White-label options
- SLA guarantees
- Dedicated support

## 📞 Contact

- **Website:** [kiomate.ng](https://kiomate.ng)
- **Email:** hello@kiomate.ng
- **Partnerships:** partnerships@kiomate.ng
- **Twitter:** [@kiomate_ng](https://twitter.com/kiomate_ng)
- **LinkedIn:** [KioMate](https://linkedin.com/company/kiomate)

## 📈 Stats

- **Lines of Code:** ~1,500
- **API Endpoints:** 7
- **Supported Locations:** 60+
- **Average Response Time:** <3 seconds
- **Uptime:** 99.9% (when not sleeping on free tier 😅)

---

<p align="center">
  <strong>Built with ❤️ for Nigerian entrepreneurs</strong>
  <br>
  <sub>Helping SMEs grow one insight at a time</sub>
</p>

<p align="center">
  <a href="#quick-start-local-development">Quick Start</a> •
  <a href="#deployment">Deployment</a> •
  <a href="#api-endpoints">API</a> •
  <a href="#roadmap">Roadmap</a> •
  <a href="#contact">Contact</a>
</p>

---