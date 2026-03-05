# ✈️ AI Travel Planner

A conversational AI travel assistant that plans personalized trips based on your **budget, mood, and constraints** — and lets you refine them in real-time through chat.

> Built with Python · Streamlit · Google Gemini API

---

## 🚀 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

---

## ✨ Features

- 🧠 **Natural Language Input** — type your trip request in plain English
- 📅 **Day-wise Itinerary Generation** — morning, afternoon, evening breakdown
- 💸 **Smart Budget Breakdown** — auto-split across stay, food, transport & activities
- 💬 **Real-time Chat Refinement** — say "make it cheaper" or "add cafes" to update instantly
- 🎭 **Mood-based Planning** — adventure, chill, romantic, family, culture
- ⬇️ **Download Itinerary** — save your trip plan as a text file

---

## 🖥️ Screenshots

> _Add screenshots here after running the app_

---

## 🗂️ Project Structure

```
Travel-Planner/
│
├── app.py                    # Streamlit entry point
├── requirements.txt          # Dependencies
├── .env                      # API keys (not committed)
├── .gitignore
├── README.md
│
├── llm/
│   ├── client.py             # Gemini API wrapper
│   ├── prompts.py            # All prompt templates
│   └── chains.py             # Intent extraction + itinerary chains
│
├── services/
│   ├── planner.py            # Core trip planning logic
│   ├── budget.py             # Budget split + formatting
│   └── chat_service.py       # Conversation + session handler
│
└── ui/
    ├── chat_ui.py            # Chat panel components
    └── itinerary_view.py     # Trip display panel
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | Python |
| AI Model | Google Gemini 1.5 Flash (free) |
| Intent Parsing | Gemini + JSON structured output |
| Session State | Streamlit session_state |

---

## 🛠️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Travel-Planner.git
cd Travel-Planner
```

### 2. Create and activate virtual environment

```bash
# Create venv
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your free API key at → [aistudio.google.com](https://aistudio.google.com)

### 5. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 💬 How to Use

### Plan a new trip
Type a natural language request in the chat:

```
3 days in Manali, ₹12k, adventure vibe
```

```
5 day Goa trip under ₹20,000, chill
```

```
Weekend trip to Coorg, ₹8k, romantic
```

### Refine your plan
Once a trip is planned, send follow-up messages:

```
Make it more adventurous
```

```
Reduce the accommodation cost
```

```
Add some local street food spots
```

```
I'm travelling with family, adjust accordingly
```

---

## 🚀 Deploy on Streamlit Cloud

1. Push your code to GitHub (make sure `.env` is in `.gitignore`)

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Connect your GitHub repository

4. Add your API key in **App Settings → Secrets**:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

5. Click **Deploy** — your app gets a public URL instantly

---

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | ✅ Yes |

---

## 📦 Dependencies

```
streamlit==1.45.1
google-generativeai==0.8.3
python-dotenv==1.0.1
requests==2.32.3
```

---

## 🗺️ Roadmap

- [x] Natural language intent extraction
- [x] Day-wise itinerary generation
- [x] Budget breakdown by category
- [x] Real-time chat refinement
- [x] Download itinerary
- [ ] Weather-aware planning
- [ ] Google Maps integration
- [ ] Multi-language support
- [ ] Trip history & saved plans

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

[MIT](LICENSE)

---

## 👨‍💻 Author

Made by **[Your Name]** · [GitHub](https://github.com/your-username) · [LinkedIn](https://linkedin.com/in/your-profile)

---

> ⭐ If you found this useful, give it a star on GitHub!
