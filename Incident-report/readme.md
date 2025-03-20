# Incident Report Agent

## Overview
This project implements an **Incident Report Agent** using **LangGraph**, **LangChain**, and **Gentoro**. The agent processes incident reports, retrieves relevant runbooks, and interacts with tools to assist in resolution. The system is designed as a **stateful graph-based workflow**, leveraging OpenAI's `gpt-4o-mini` model.

## Features
- **Incident Report Processing**: Accepts structured incident reports and processes them for analysis.
- **Runbook Retrieval**: Automatically fetches relevant runbook documentation for incidents.
- **Tool Execution**: Executes predefined tools using Gentoro to analyze and resolve incidents.
- **Graph-based Decision Flow**: Uses `StateGraph` to model the flow of the incident resolution process.
- **Multi-message Handling**: Supports various message formats including AI, System, Tool, and Human messages.

## Installation
### 1. Clone the Repository
```sh
git clone https://github.com/gentoro-GT/python-sdk-examples.git
cd python-sdk-examples
```

### 2. Install Dependencies
Ensure you have Python installed (>= 3.8). Install dependencies using:
```sh
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file with the following variables:
```env
GENTORO_BRIDGE_UID=<your_gentoro_bridge_uid>
OPENAI_API_KEY=<your_openai_api_key>
```

## How It Works
### 1. **State Management**
The agent uses the `IncidentReportState` class to maintain state. Messages are stored and processed as lists of dictionaries and LangChain message objects.

### 2. **Graph Workflow**
The execution flow is modeled using `StateGraph` with the following nodes:
- **loadRunBook**: Retrieves relevant runbook content.
- **callModel**: Invokes OpenAI's model for processing.
- **callTools**: Executes tools provided by Gentoro.
- **reAct**: Determines the next course of action based on the processed messages.

### 3. **Tool Integration**
The system integrates with tools using `Gentoro`. Tools are retrieved dynamically and used to execute actions required for resolving the incident.

## Usage
To run the incident report agent, execute the script:
```sh
python main.py
```
Alternatively, run asynchronously using:
```sh
asyncio.run(main())
```

## Example Incident Report
The initial state is created with an example report:
```yaml
title: S3 Bucket Access Denied
report:
  Issue: Application Crashing on Login
  Description: After a recent deployment, users reported that the application crashes upon entering valid login credentials.
  Impact: 100% of active users are affected.
  Resolution: Rolled back to the previous version and scheduled a hotfix deployment.
```

## Future Enhancements
- **Enhance Error Handling**: Improve logging and debugging for failed tool executions.
- **Expand Toolset**: Integrate more tools to cover additional incident resolution scenarios.
- **Real-time Updates**: Enable real-time monitoring of incident status.
