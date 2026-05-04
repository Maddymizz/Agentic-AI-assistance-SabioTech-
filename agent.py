# agent.py
import os
import subprocess
import tempfile
import json

from dotenv import load_dotenv
from typing import TypedDict, Literal
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END

load_dotenv(dotenv_path=".env")  # ✅ separate line
# ── LLM setup ──────────────────────────────────────────────────────────────
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0
)

# ── Tavily search tool ──────────────────────────────────────────────────────
search_tool = TavilySearchResults(
    api_key=os.getenv("TAVILY_API_KEY"),
    max_results=5
)

# ── Agent state ─────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    question: str
    action: str          # "search" | "code" | "general"
    search_results: str
    generated_code: str
    execution_output: str
    sources: list
    answer: str
    history: list        # ✦ NEW: conversation memory

# ── Node 1: Planner ─────────────────────────────────────────────────────────
def planner(state: AgentState) -> AgentState:
    question = state["question"]
    history_text = ""
    if state.get("history"):
        history_text = "\n".join(
            [f"Q: {h['question']}\nA: {h['answer']}" for h in state["history"][-3:]]
        )

    prompt = f"""You are a routing agent. Given a user question, decide the best action.
Previous conversation context:
{history_text if history_text else "None"}

User question: {question}

Choose ONE action:
- "search": if the question needs current/real-world information, news, facts, prices, events
- "code": if the question involves math, calculations, data analysis, simulations, or programming
- "general": if it's a simple conversational question or general knowledge you can answer directly

Respond with ONLY one word: search, code, or general"""

    response = llm.invoke(prompt)
    action = response.content.strip().lower()
    if action not in ["search", "code", "general"]:
        action = "general"

    return {**state, "action": action}

# ── Node 2: Search Tool ──────────────────────────────────────────────────────
def search_node(state: AgentState) -> AgentState:
    results = search_tool.invoke(state["question"])
    sources = []
    result_text = ""

    for r in results:
        if isinstance(r, dict):
            sources.append(r.get("url", ""))
            result_text += f"Source: {r.get('url', '')}\n{r.get('content', '')}\n\n"
        else:
            result_text += str(r) + "\n\n"

    return {**state, "search_results": result_text, "sources": sources}

# ── Node 3: Code Writer ──────────────────────────────────────────────────────
def code_writer(state: AgentState) -> AgentState:
    prompt = f"""Write clean Python code to answer this question: {state['question']}

Rules:
- Output ONLY executable Python code
- No markdown, no backticks, no explanations
- Use print() for all output values
- Handle edge cases with try/except
- Import only standard libraries (math, statistics, datetime, etc.)"""

    response = llm.invoke(prompt)
    code = response.content.strip()

    # Strip markdown fences if the model added them
    if code.startswith("```"):
        lines = code.split("\n")
        code = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

    return {**state, "generated_code": code}

# ── Node 4: Code Executor ────────────────────────────────────────────────────
def code_executor(state: AgentState) -> AgentState:
    code = state.get("generated_code", "")
    if not code:
        return {**state, "execution_output": "No code was generated."}

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=15
        )
        output = result.stdout.strip() or result.stderr.strip() or "No output produced."
    except subprocess.TimeoutExpired:
        output = "Error: Code execution timed out (15s limit)."
    except Exception as e:
        output = f"Error: {str(e)}"
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return {**state, "execution_output": output}

# ── Node 5: Response Generator ───────────────────────────────────────────────
def response_generator(state: AgentState) -> AgentState:
    action = state.get("action", "general")

    if action == "search":
        prompt = f"""Based on these search results, answer the question clearly and concisely.

Question: {state['question']}

Search Results:
{state.get('search_results', 'No results found.')}

Write a clear, factual answer. Be specific. Mention sources where relevant."""

    elif action == "code":
        prompt = f"""Based on the code execution result, explain the answer clearly.

Question: {state['question']}
Code executed:
{state.get('generated_code', '')}

Execution output:
{state.get('execution_output', '')}

Explain what the code calculated and what the result means. Be clear and friendly."""

    else:
        prompt = f"""Answer this question directly and helpfully: {state['question']}"""

    response = llm.invoke(prompt)
    return {**state, "answer": response.content.strip()}

# ── Router ───────────────────────────────────────────────────────────────────
def route_action(state: AgentState) -> Literal["search_node", "code_writer", "response_generator"]:
    action = state.get("action", "general")
    if action == "search":
        return "search_node"
    elif action == "code":
        return "code_writer"
    return "response_generator"

# ── Build LangGraph ──────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner)
    graph.add_node("search_node", search_node)
    graph.add_node("code_writer", code_writer)
    graph.add_node("code_executor", code_executor)
    graph.add_node("response_generator", response_generator)

    graph.set_entry_point("planner")

    graph.add_conditional_edges(
        "planner",
        route_action,
        {
            "search_node": "search_node",
            "code_writer": "code_writer",
            "response_generator": "response_generator"
        }
    )

    graph.add_edge("search_node", "response_generator")
    graph.add_edge("code_writer", "code_executor")
    graph.add_edge("code_executor", "response_generator")
    graph.add_edge("response_generator", END)

    return graph.compile()

compiled_graph = build_graph()

# ── Public runner ────────────────────────────────────────────────────────────
def run_agent(question: str, history: list = []) -> dict:
    initial_state = AgentState(
        question=question,
        action="",
        search_results="",
        generated_code="",
        execution_output="",
        sources=[],
        answer="",
        history=history
    )
    result = compiled_graph.invoke(initial_state)
    return {
        "answer": result.get("answer", ""),
        "code": result.get("generated_code", ""),
        "execution_output": result.get("execution_output", ""),
        "sources": result.get("sources", []),
        "action": result.get("action", "general")
    }