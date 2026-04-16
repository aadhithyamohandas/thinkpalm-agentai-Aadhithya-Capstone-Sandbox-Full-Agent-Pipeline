# 🏎️ Capstone Sandbox — Full Agent Pipeline (F1 Race Strategy Agent)

**Name:** Aadhithya M  
**Track:** Python AI  
**Lab Name:** Capstone Sandbox — Full Agent Pipeline  

## 🎯 What it does
This is a multi-agent AI system that acts as an F1 Pit Stop Strategist. Given race conditions, it recommends the optimal pit stop strategy. It uses 4 specialized AI agents working together via a ReAct loop, 4 tools (including 2 live APIs), and features persistent cross-session memory backed by a SQLite database. 

## 🛠️ Tools Used
1. **Google Gemini / Groq LLM:** Large Language Model powering the reasoning.
2. **Open-Meteo API:** Used as a live tool to fetch real-time track weather.
3. **Jolpica F1 API:** Used as a live tool to fetch historical pit stop data.
4. **Streamlit:** Powers the interactive, dark-themed UI.
5. **SQLite:** Backs the persistent session memory and strategy history.

## 👀 Observations
- The ReAct loop (Thought -> Action -> Observation -> Answer) proved highly effective for chaining the APIs (getting weather, then fetching track data, then running the simulation).
- The Streamlit UI made it very easy to display the ReAct thought process live to the user.
- Implementing cross-session memory via SQLite dramatically improved the user experience, allowing the agent to remember user preferences across different runs.

## 🚀 How to Run

1. Install dependencies:
   `pip install -r requirements.txt`

2. Create a [.env](cci:7://file:///home/aadhithya.m@dc.thinkpalm.info/.gemini/antigravity/scratch/f1-strategy-agent/.env:0:0-0:0) file in the root directory:
   `GROQ_API_KEY=your_key_here`

3. Navigate to the source folder and run the app:
   `cd src`
   `streamlit run app.py`
