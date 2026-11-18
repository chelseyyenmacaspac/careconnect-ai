
# CareConnect AI
Hospital IT Support Assistant

## Project Overview
CareConnect AI is a chatbot designed to help hospital staff with common IT problems. It provides basic troubleshooting instructions, identifies urgent issues, and creates sample IT support tickets.

## Problem
Hospital staff rely on computers, printers, networks, and electronic health record (EHR) systems every day. When these systems stop working, staff may have trouble completing their tasks or accessing important information.

## How It Works
CareConnect AI uses Python, Streamlit, and LangGraph to organize four agents:

1. Intake Agent - Identifies the IT problem and checks if it is urgent.
2. Knowledge Agent - Provides troubleshooting steps.
3. Workflow Agent - Creates sample IT support tickets.
4. Escalation Agent - Handles urgent problems and recommends contacting emergency IT support.

## Features
- IT problem identification
- Troubleshooting instructions
- Urgent issue detection
- Demo support ticket creation
- Chat conversation history

## Technologies
- Python
- Streamlit
- LangGraph

## How to Run
Install the required packages:

pip install -r requirements.txt

Start the chatbot:

python -m streamlit run app.py

## Limitations
This is a rule-based demonstration. It does not use a generative AI model or connect to real hospital IT systems.

No real support tickets or emergency alerts are sent.

Do not enter patient information.

## Project Goal
The goal is to demonstrate how a multi-agent workflow can help organize hospital IT support requests and direct urgent problems to the appropriate support team.
