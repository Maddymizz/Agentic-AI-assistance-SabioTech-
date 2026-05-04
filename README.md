🧠 SabioTech AI Portal

An intelligent Agentic AI system that dynamically decides how to answer user queries using:

🔍 Web Search (Tavily)
💻 Code Generation & Execution
💬 Direct LLM Responses (Groq Llama 3)

Built with Streamlit + LangGraph + Groq API

🚀 Features
🧭 Smart Query Routing
Automatically decides whether to:
Search the web
Write & execute Python code
Answer directly
🔍 Real-time Web Search
Uses Tavily API for up-to-date information
💻 Code Generation & Execution
Generates Python code using LLM
Executes it securely in a temporary environment
Returns output instantly
💬 Conversational Memory
Maintains recent history for context-aware responses
🎨 Modern UI
Built using Streamlit with custom styling
Interactive history panel
Example prompts for quick testing
🏗️ Architecture

The system is built using a LangGraph-based agent pipeline:

User Input
   ↓
Planner (LLM decides action)
   ↓
 ┌───────────────┬───────────────┬───────────────┐
 │   Search      │    Code       │   General     │
 │ (Tavily API)  │ (LLM + Exec)  │ (LLM Direct)  │
 └───────────────┴───────────────┴───────────────┘
   ↓
Response Generator
   ↓
Final Answer
🛠️ Tech Stack
Frontend: Streamlit
LLM: Groq (Llama 3.1)
Agent Framework: LangGraph
Search Tool: Tavily API
Environment Handling: python-dotenv
Execution Engine: Python subprocess
📂 Project Structure
├── app.py          # Streamlit UI
├── agent.py        # Core agent logic (LangGraph pipeline)
├── .env            # API keys (DO NOT PUSH)
├── .env.example    # Sample environment variables
├── requirements.txt
└── README.md
🔐 Environment Variables

Create a .env file in the root directory:

GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key

⚠️ Never commit your .env file.
Use .gitignore to keep it private.

⚙️ Installation
1. Clone the repository
git clone https://github.com/your-username/sabiotech-ai-portal.git
cd sabiotech-ai-portal
2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
3. Install dependencies
pip install -r requirements.txt
▶️ Run the Application
streamlit run app.py

Then open:

http://localhost:8501
🧪 Example Queries
What is the current price of Bitcoin?
Calculate compound interest on ₹50,000 at 8% for 10 years
What happened in AI news this week?
Generate the first 20 Fibonacci numbers
🧠 How It Works
1. Planner Node
Uses LLM to classify query into:
search
code
general
2. Execution Paths
Search → Tavily API → structured results
Code → LLM generates Python → executed via subprocess
General → Direct LLM response
3. Response Generator
Converts outputs into human-readable answers
⚠️ Limitations
Code execution is sandboxed but not fully secure for production
Depends on API rate limits (Groq & Tavily)
Limited long-term memory (only recent history used)
🌟 Future Improvements
Add authentication system
Persistent database for conversation history
Deploy on cloud (Streamlit Cloud / AWS)
Add tool plugins (PDF reader, database queries)
Improve code execution sandbox security
👩‍💻 Author

Madhumitha Jyothi Prasad

📜 License

This project is for educational and portfolio purposes.