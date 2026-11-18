
import os
import streamlit as st
from typing import TypedDict
from uuid import uuid4
from langgraph.graph import StateGraph, START, END
from google import genai

from rag import search_knowledge
from mcp_client import create_mcp_ticket


# Shared information between agents
class SupportState(TypedDict):
    question: str
    issue_type: str
    urgent: bool
    response: str
    ticket: str


# Agent 1: Identify the IT problem
def intake_agent(state):
    question = state["question"].lower()

    urgent_words = [
        "urgent", "emergency", "immediately",
        "multiple nurses", "entire unit",
        "hospital-wide", "patient care",
        "all workstations", "system down",
        "system is down", "ehr down",
        "cannot access patient charts",
        "outage", "critical", "patients at risk"
    ]

    urgent = any(word in question for word in urgent_words)

    if any(word in question for word in [
        "ehr", "electronic health record",
        "patient chart", "login", "password"
    ]):
        issue = "EHR Problem"

    elif any(word in question for word in [
        "printer", "printing", "print"
    ]):
        issue = "Printer Problem"

    elif any(word in question for word in [
        "wifi", "wi-fi", "internet", "network"
    ]):
        issue = "Network Problem"

    elif any(word in question for word in [
        "computer", "workstation", "laptop"
    ]):
        issue = "Computer Problem"

    else:
        issue = "Other"

    return {
        "issue_type": issue,
        "urgent": urgent
    }


# Agent 2: Search ChromaDB and generate an AI answer
def knowledge_agent(state):
    question = state["question"]

    # Retrieve relevant instructions from ChromaDB
    context = search_knowledge(question)

    try:
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        client = genai.Client(api_key=api_key)

        prompt = f"""
You are CareConnect AI, a hospital IT support assistant.

Answer the question using only the IT guide below.

Rules:
- Give simple, clear troubleshooting steps.
- Do not invent instructions or hospital policies.
- Never request patient names or medical information.
- If the guide does not answer the question, recommend IT support.
- Do not claim a real ticket was created.
- Keep your response short and professional.

IT Guide:
{context}

User Question:
{question}
"""

        result = client.models.generate_content(
            model="gemini-4-neon",
            contents=prompt
        )

        state["response"] = (
            result.text or "Please contact IT support."
        )

    except Exception as e:
        print(
            "GEMINI ERROR:",
            type(e).__name__,
            str(e),
            flush=True
        )

        state["response"] = (
            "AI-generated guidance is currently unavailable.\n\n"
            "Here are the instructions from the IT guide:\n\n"
            f"{context}"
        )

    return state


# Agent 3: Create demo support tickets through MCP
def workflow_agent(state):
    question = state["question"].lower()

    ticket_words = [
        "ticket", "still not working",
        "didn't work", "cannot fix",
        "not resolved", "need support",
        "create a ticket"
    ]

    if not any(word in question for word in ticket_words):
        return {"ticket": ""}

    try:
        # Call the MCP server through the MCP client
        result = create_mcp_ticket(
            state["issue_type"],
            state["question"]
        )

        ticket = result["ticket_id"]

        return {
            "ticket": ticket,
            "response": (
                state["response"]
                + "\n\n---\n\n"
                + f"**MCP Support Ticket:** {ticket}\n\n"
                + f"**Issue Type:** {state['issue_type']}\n\n"
                + "**Status:** Demo ticket created through MCP\n\n"
                + "This is a sample ticket only. "
                + "No real IT request has been submitted."
            )
        }

    except Exception as e:
        print(
            "MCP ERROR:",
            type(e).__name__,
            str(e),
            flush=True
        )

        return {
            "ticket": "",
            "response": (
                state["response"]
                + "\n\nThe demo ticket tool is currently unavailable. "
                + "No ticket was created."
            )
        }


# Agent 4: Escalate urgent IT problems
def escalation_agent(state):
    ticket = "URG-" + uuid4().hex[:8].upper()

    return {
        "ticket": ticket,
        "response": (
            "🚨 **URGENT IT ISSUE**\n\n"
            f"**Issue Type:** {state['issue_type']}\n\n"
            f"**Demo Escalation Ticket:** {ticket}\n\n"
            "**Priority:** Critical\n\n"
            "This issue may affect hospital operations "
            "or patient care.\n\n"
            "Contact your hospital's emergency IT "
            "support team immediately and follow "
            "the hospital's downtime procedures.\n\n"
            "This is a demonstration only. "
            "No real alert or ticket has been sent."
        )
    }


# Decide which agent handles the request
def route_request(state):
    if state["urgent"]:
        return "Escalation Agent"

    return "Knowledge Agent"


# Build the LangGraph workflow
graph = StateGraph(SupportState)

graph.add_node("Intake Agent", intake_agent)
graph.add_node("Knowledge Agent", knowledge_agent)
graph.add_node("Workflow Agent", workflow_agent)
graph.add_node("Escalation Agent", escalation_agent)

graph.add_edge(START, "Intake Agent")

graph.add_conditional_edges(
    "Intake Agent",
    route_request,
    {
        "Knowledge Agent": "Knowledge Agent",
        "Escalation Agent": "Escalation Agent"
    }
)

graph.add_edge("Knowledge Agent", "Workflow Agent")
graph.add_edge("Workflow Agent", END)
graph.add_edge("Escalation Agent", END)

app_graph = graph.compile()


# Streamlit chatbot interface
st.set_page_config(
    page_title="CareConnect AI",
    page_icon="🏥"
)

st.title("🏥 CareConnect AI")
st.subheader("Hospital IT Support Assistant")

st.caption(
    "Demo system — do not enter patient information."
)

st.write(
    "How can I help you with your IT problem today?"
)


# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Chat input
question = st.chat_input(
    "Describe your IT problem..."
)

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    # Run the four-agent workflow
    with st.spinner("Checking IT support instructions..."):
        result = app_graph.invoke({
            "question": question,
            "issue_type": "",
            "urgent": False,
            "response": "",
            "ticket": ""
        })

    answer = result["response"]

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    with st.chat_message("assistant"):
        st.write(answer)
