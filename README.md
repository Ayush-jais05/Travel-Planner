# ✈️ AI Travel Planner

> Conversational AI travel planner — generates day-wise itineraries, budget breakdowns & real-time refinements using Groq LLaMA 3.3

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-travel-planner.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3-orange.svg)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 Live Demo

**[👉 Try it here → AI Travel Planner](https://ai-travel-planner.streamlit.app)**

---

## 📸 Screenshots

| Chat + Itinerary | Budget Breakdown |
|---|---|
| ![Chat UI](https://via.placeholder.com/400x250?text=Chat+UI) | ![Budget](https://via.placeholder.com/400x250?text=Budget+Breakdown) |

> _Replace with actual screenshots after deployment_

---

## ✨ Features

- 🧠 **Natural Language Input** — type your trip request in plain English
- 📅 **Day-wise Itinerary** — morning, afternoon, evening breakdown with real place names
- 💸 **Smart Budget Breakdown** — auto-split across stay, food, transport & activities
- 💬 **Real-time Chat Refinement** — say "make it adventurous", "add 5k budget", "suggest hotels"
- 🧠 **Full Conversation Memory** — remembers your trip context throughout the chat
- 🎭 **Mood-based Planning** — adventure, chill, romantic, family, culture
- ⬇️ **Download Itinerary** — save your trip plan as a text file

---

## 💬 How to Use

### Plan a new trip
```
3 days in Manali, ₹12k, adventure vibe
```
```
5 day Goa trip under ₹20,000, chill
```
```
Weekend trip to Coorg, ₹8k, romantic
```

### Refine your plan (remembers full context)
```
Make it more adventurous
Add 5k to my budget
Suggest some hotels
Change vibe to chill
What should I pack?
Reduce accommodation cost
```

---

## 🧠 How It Works

```
User: "3 days Manali ₹12k adventure"
           ↓
   Intent Extraction (LLaMA 3.3)
   → Destination: Manali | Days: 3 | Budget: ₹12k | Mood: Adventure
           ↓
   Itinerary Generator (LLaMA 3.3)
   → Day 1: Solang Valley → Day 2: Rohtang → Day 3: Old Manali
           ↓
   Budget Splitter
   → Stay: ₹3.6k | Food: ₹2.4k | Transport: ₹2.4k | Activities: ₹3k
           ↓
   Displayed in Streamlit (chat left | itinerary + budget right)
           ↓
   User: "add cafes and reduce stay cost"
           ↓
   LLM updates itinerary with full context memory → panel refreshes
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | Python 3.10+ |
| LLM | Groq — LLaMA 3.3 70B Versatile (free) |
| Intent Parsing | LLM structured JSON output |
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
│   ├── client.py             # Groq client wrapper
│   ├── prompts.py            # All prompt templates
│   └── chains.py             # Intent extraction + generation chains
│
├── services/
│   ├── planner.py            # Core trip planning logic
│   ├── budget.py             # Budget split + formatting
│   └── chat_service.py       # Conversation handler with full memory
│
└── ui/
    ├── chat_ui.py            # Chat panel
    └── itinerary_view.py     # Trip display panel
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

### 5. Run
```bash
streamlit run app.py
```

---

## 🚀 Deploy on Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo: `Ayush-jais05/Travel-Planner`
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
```

---

## 🗺️ Roadmap

- [x] Natural language intent extraction
- [x] Day-wise itinerary generation
- [x] Budget breakdown by category
- [x] Real-time chat refinement
- [x] Full conversation memory
- [x] Download itinerary
- [ ] Weather-aware planning
- [ ] Google Maps integration
- [ ] Multi-language support
- [ ] Trip history & saved plans

---

## 👨‍💻 Author

**Ayush Raj** · [GitHub @Ayush-jais05](https://github.com/Ayush-jais05)

---

> ⭐ If you found this useful, give it a star!