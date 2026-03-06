# ✈️ AI Travel Planner

> Conversational AI travel planner — generates day-wise itineraries, budget breakdowns, weather-aware planning, packing lists & PDF export using Groq LLaMA 3.3

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-travel-planner.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3-orange.svg)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 Live Demo

**[👉 Try it here → AI Travel Planner](https://ai-travel-planner.streamlit.app)**

---

## ✨ Features

- 🧠 **Natural Language Input** — type your trip in plain English
- 📅 **Day-wise Itinerary** — morning, afternoon, evening with real place names
- 💸 **Smart Budget Breakdown** — auto-split across stay, food, transport & activities
- 🌤️ **Weather-Aware Planning** — mention travel month, date, or weather type → itinerary updates
- 👥 **Group Size Support** — solo, couple, family or group → per-person budget + tailored activities
- 🎒 **Packing List Generator** — weather + destination + group aware
- ⬇️ **PDF & Text Export** — download full itinerary + budget + packing list
- 💬 **Full Conversation Memory** — remembers your trip throughout the chat
- 🎭 **Mood-based Planning** — adventure, chill, romantic, family, culture

---

## 💬 How to Use

### Plan a new trip
```
3 days in Manali, ₹12k, adventure vibe
5 day Goa trip under ₹20,000, chill
Weekend trip to Coorg, ₹8k, romantic
3 days Amsterdam, €500, culture
Family of 4 in Kerala, ₹30k, 5 days
```

### Refine with weather
```
I'm going in December
Going tomorrow
Travelling next week
It's going to be rainy
Planning for monsoon season
Going on March 15th
```

### Update group size
```
Travelling with 3 friends
It's a couple trip
Family of 4
Solo trip
Me and my girlfriend
Group of 6
```

### Other refinements
```
Make it more adventurous
Add 5k to my budget
Change budget to 25k
Suggest some hotels
What should I pack?
Generate packing list
Reduce accommodation cost
```

---

## 🧠 How It Works

```
User: "3 days Manali ₹12k adventure, group of 4"
           ↓
   Intent Extraction (LLaMA 3.3)
   → Destination: Manali | Days: 3 | Budget: ₹12k
   → Mood: Adventure | Persons: 4 | Group: group
           ↓
   Itinerary Generator → Day-wise plan with real places
           ↓
   Budget Splitter → Per person breakdown
           ↓
   Displayed in Streamlit (chat left | itinerary + budget right)
           ↓
   User: "going in December"
           ↓
   Weather Service (Open-Meteo API / seasonal estimate)
   → Cold, 5-10°C, clear skies
           ↓
   Itinerary updates for weather conditions
           ↓
   User: "generate packing list"
           ↓
   Packing list → weather + group + destination aware
           ↓
   Click Download PDF → full formatted PDF
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | Python 3.10+ |
| LLM | Groq — LLaMA 3.3 70B Versatile (free) |
| Weather API | Open-Meteo (free, no key needed) |
| PDF Export | fpdf2 |
| Session Memory | Streamlit session_state |
| Deployment | Streamlit Cloud |

---

## 🗂️ Project Structure

```
Travel-Planner/
│
├── app.py                    # Streamlit entry point
├── requirements.txt
├── .env                      # API keys (not committed)
├── .gitignore
├── README.md
│
├── llm/
│   ├── prompts.py            # All prompt templates
│   └── chains.py             # LLM chains + generation functions
│
├── services/
│   ├── planner.py            # Core trip planning logic
│   ├── budget.py             # Budget split + formatting
│   ├── chat_service.py       # Conversation handler with full memory
│   └── weather.py            # Open-Meteo weather service
│
├── ui/
│   ├── chat_ui.py            # Chat panel
│   └── itinerary_view.py     # Trip display panel
│
└── utils/
    └── pdf_export.py         # PDF generation
```

---

## 🛠️ Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/Ayush-jais05/Travel-Planner.git
cd Travel-Planner
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add API key
Create `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```
Get your **free** Groq key at → [console.groq.com](https://console.groq.com)

> No OpenWeatherMap key needed — uses Open-Meteo (100% free, no registration)

### 5. Run
```bash
streamlit run app.py
```

---

## 🚀 Deploy on Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo: `Ayush-jais05/Travel-Planner`
4. Main file: `app.py`
5. Add secret in **App Settings → Secrets**:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```
6. Click **Deploy** 🎉

---

## 📦 Requirements

```
streamlit==1.45.1
groq==0.13.0
python-dotenv==1.0.1
requests==2.32.3
fpdf2==2.7.9
```

---

## 🗺️ Roadmap

- [x] Natural language intent extraction
- [x] Day-wise itinerary generation
- [x] Budget breakdown by category
- [x] Real-time chat refinement
- [x] Full conversation memory
- [x] Weather-aware planning (Open-Meteo API)
- [x] Group size & per-person budget
- [x] Packing list generator
- [x] PDF + Text export
- [ ] Google Maps links for every place
- [ ] Multi-language support
- [ ] Trip history & saved plans
- [ ] Voice input

---

## 👨‍💻 Author

**Ayush Raj** · [GitHub @Ayush-jais05](https://github.com/Ayush-jais05)

---

> ⭐ If you found this useful, give it a star!