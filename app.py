
import streamlit as st
from typing import TypedDict
from uuid import uuid4
from langgraph.graph import StateGraph, START, END


# Shared information
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
        "outage", "critical",
        "patients at risk"
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


# Agent 2: Provide troubleshooting steps
def knowledge_agent(state):
    issue = state["issue_type"]

    solutions = {
        "EHR Problem": (
            "If you cannot access the EHR system:\n\n"
            "1. Check your network connection.\n"
            "2. Make sure you are using the correct login.\n"
            "3. Try signing in again.\n"
            "4. If the issue continues, contact IT support.\n\n"
            "Never share your password."
        ),

        "Printer Problem": (
            "If your printer is not working:\n\n"
            "1. Check that the printer is turned on.\n"
            "2. Make sure it has paper and ink or toner.\n"
            "3. Check the printer connection.\n"
            "4. Try printing a test page.\n"
            "5. Contact IT if the issue continues."
        ),

        "Network Problem": (
            "If your network or Wi-Fi is not working:\n\n"
            "1. Check whether Wi-Fi is enabled.\n"
            "2. Make sure you are connected to the "
            "approved hospital network.\n"
            "3. Check if other approved websites work.\n"
            "4. Contact IT if the connection is still down.\n\n"
            "Do not connect hospital devices to "
            "unapproved networks."
        ),

        "Computer Problem": (
            "If your computer is not working:\n\n"
            "1. Check the power connection.\n"
            "2. Make sure the monitor is turned on.\n"
            "3. Check the keyboard and mouse.\n"
            "4. Restart only if hospital policy allows it.\n"
            "5. Contact IT if the problem continues."
        ),

        "Other": (
            "I can help with hospital IT problems "
            "such as EHR access, computers, printers, "
            "and network connections.\n\n"
            "Please describe the problem in more detail."
        )
    }

    return {"response": solutions[issue]}


# Agent 3: Create a demo support ticket
def workflow_agent(state):
    question = state["question"].lower()

    ticket_words = [
        "ticket", "still not working",
        "didn't work", "cannot fix",
        "not resolved", "need support",
        "create a ticket"
    ]

    if any(word in question for word in ticket_words):
        ticket = "IT-" + uuid4().hex[:8].upper()

        return {
            "ticket": ticket,
            "response": (
                state["response"]
                + "\n\n---\n"
                + f"Support Ticket: {ticket}\n\n"
                + f"Issue Type: {state['issue_type']}\n\n"
                + "Status: Demo ticket created\n\n"
                + "This is a sample ticket only. "
                + "No real IT request has been submitted."
            )
        }

    return {"ticket": ""}


# Agent 4: Escalate urgent IT problems
def escalation_agent(state):
    ticket = "URG-" + uuid4().hex[:8].upper()

    return {
        "ticket": ticket,
        "response": (
            "🚨 URGENT IT ISSUE\n\n"
            f"Issue Type: {state['issue_type']}\n\n"
            f"Demo Escalation Ticket: {ticket}\n\n"
            "Priority: Critical\n\n"
            "This issue may affect hospital operations "
            "or patient care.\n\n"
            "Please contact your hospital's emergency "
            "IT support team immediately and follow "
            "the hospital's downtime procedures.\n\n"
            "This is a demonstration only. "
            "No real alert or ticket has been sent."
        )
    }


# Decide which agent handles the problem
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


# Store conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Chat input
question = st.chat_input("Describe your IT problem...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

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
