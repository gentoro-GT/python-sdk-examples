from langgraph.graph import StateGraph, START, END
from langchain_core.messages import ToolMessage,HumanMessage,SystemMessage, AIMessage, AIMessageChunk,BaseMessage
# from langchain_core.language_models.base import ToolDefination 
from Gentoro import Gentoro, SdkConfig, Providers
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import json
import asyncio
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Optional

llm = ChatOpenAI(
    model="gpt-4o-mini")
# Load environment variables
load_dotenv()
from state import StateAnnotation
from template import TemplateGenerator
from utils import Message

env = "process"

# class IncidentReportState(BaseModel):
#     messages: List[Union[Dict[str, Union[str, Dict]], SystemMessage, AIMessage, ToolMessage, HumanMessage]]
#     endGraphSignal: Optional[bool] = Field(default=False)
class IncidentReportState(BaseModel):
    messages: List[Union[
        Dict[str, Union[str, Dict]], 
        SystemMessage, 
        AIMessage, 
        HumanMessage,
        ToolMessage
    ]]
    endGraphSignal: Optional[bool] = Field(default=False)

    @classmethod
    def convert_messages(cls, messages):
        """ Ensures all messages are in a valid format before creating an instance """
        converted_messages = []
        for msg in messages:
            if isinstance(msg, ToolMessage) and isinstance(msg.content, dict):
                msg.content = json.dumps(msg.content)  # Convert dict to JSON string
            converted_messages.append(msg)
        return converted_messages

    @classmethod
    def create(cls, messages, endGraphSignal=False):
        """ Factory method to create a valid IncidentReportState instance """
        return cls(messages=cls.convert_messages(messages), endGraphSignal=endGraphSignal)

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


# Initialize the Gentoro and OpenAI instances
_gentoro = Gentoro(SdkConfig(provider=Providers.OPENAI))
templateGenerator = TemplateGenerator()

GENTORO_BRIDGE_UID = os.getenv("GENTORO_BRIDGE_UID")
gentoro_tools = _gentoro.get_tools(GENTORO_BRIDGE_UID, [])

tools = []
for tool in gentoro_tools:
    function_def = tool.get('function')
    parameters = function_def.get('parameters')
    properties = {}
    
    for key, value in parameters.get('properties', {}).items():
        # Store in the properties dictionary
        properties[key] = {
            "type": "string",
            "description": value.get('description'),
        }
    tools.append({
        "type": tool.get('type'),
        "function": {
            "name": function_def.get('name'),
            "description": function_def.get('description'),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": parameters.get('required'),
            },
        },
    })
end_graph_tool_def = {
    "type": "function",
    "function": {
      "name": "end_graph",
      "description": "Use this function to report the end of the graph execution",
      "parameters": {
        "type": "object",
        "properties": {
          "summary": {
            "type": "string",
            "description": "Pass here the summary of the execution and actions taken, if any. In case of errors or issues, please provide a detailed description."
          }
        },
        "required": [
          "summary"
        ]
      }
    }
  }
tools.append(end_graph_tool_def)


def load_runbook(state:IncidentReportState):
    result = _gentoro.run_tool_natively(GENTORO_BRIDGE_UID, "retrieve_runbook_content", {})
    print("                  runbook",result)
    if result.get('type') == "error":
        exec_error = result.data
        return IncidentReportState(
            messages=state.messages + [
                Message.system(
                    TemplateGenerator.formatted_template("report_unrecoverable_error", {
                        "error_message": "There was an error attempting to load the runbook." + exec_error.message,
                    })
                )
            ],
            endGraphSignal=True)
    else:
        data = result
        runbook = json.loads(data.get('content'))["runbook"]
        print("message",state.messages[0])
        return IncidentReportState(
            messages=state.messages + [
                Message.system(
                    templateGenerator.formatted_template("leading_message_with_context", {
                        "run_book_content": runbook,
                        "incident_report": state.messages[0].get("content", "No incident report available.")
                    })
                )
            ]
        )


async def call_tools(state: IncidentReportState):
    last_message = state.messages[-1]
    print("tool call last message", last_message)

    if isinstance(last_message, (AIMessage, AIMessageChunk)):
        tool_calls = getattr(last_message, "tool_calls", [])
        end_graph_signal = None
        end_graph_summary = None
        
        if any(tc["name"] == "end_graph" for tc in tool_calls):
            end_graph_entry = next((item for item in tool_calls if item['name'] == 'end_graph'), None)
            end_graph_summary = end_graph_entry['args']['summary'] if end_graph_entry else "No summary found"  
            end_graph_signal = True
            end_graph_id = end_graph_entry['id'] if end_graph_entry else "No ID found"
            # end_graph_summary = tool_calls['args']['summary'] if tool_calls else None
            tool_calls = [item for item in tool_calls if item['name'] != 'end_graph']
        
        if tool_calls:
            _tools = [
                {
                    "id": tool_call["id"],
                    "type": tool_call["type"],
                    "details": {
                        "name": tool_call["name"],
                        "arguments": json.dumps(tool_call.get("args", {})),
                    },
                }
                for tool_call in tool_calls
            ]
            print("Calling tools", _tools)
            result = _gentoro.run_tools(GENTORO_BRIDGE_UID, None, _tools)

            _tool_messages = result
            # Directly append `_tool_messages` to `updated_messages`
            updated_messages = state.messages+_tool_messages
            if end_graph_signal:
                end_graph_message = [{'role':'tool','tool_call_id':end_graph_id,'content':end_graph_summary}]
                updated_messages = state.messages+end_graph_message
                return IncidentReportState(messages=updated_messages, endGraphSignal=True)
        if end_graph_signal:
            end_graph_message = [{'role':'tool','tool_call_id':end_graph_id,'content':end_graph_summary}]
            updated_messages = state.messages+end_graph_message
            return IncidentReportState(messages=updated_messages, endGraphSignal=True)
            
        return IncidentReportState(messages=state.messages+_tool_messages)
    
    raise ValueError("Invalid state, expected an AI message or chunk")



def call_model(state:IncidentReportState):
    llm = ChatOpenAI( model="gpt-4o-mini").bind_tools(tools)
    message = llm.invoke([msg.model_dump() if isinstance(msg, (AIMessage, SystemMessage, ToolMessage, HumanMessage)) else msg for msg in state.messages])
    return IncidentReportState(messages=state.messages + [message])

def re_act(state: IncidentReportState):
    return IncidentReportState(messages=state.messages, endGraphSignal=state.endGraphSignal)


def route(state: IncidentReportState):
    last_message = state.messages[-1]
    endGraphSignal=state.endGraphSignal
    if endGraphSignal:
        return "__end__"
    if isinstance(last_message, (AIMessage, AIMessageChunk)):
        tool_calls = getattr(last_message, 'tool_calls', [])
        if tool_calls:
            return "callTools"

    if isinstance(last_message, (HumanMessage, SystemMessage, ToolMessage)):
        return "callModel"
    
    if last_message.get('role')=='tool':
        return "callModel"

    else:
        return "__end__"

    return "__end__"


graph_builder = StateGraph(IncidentReportState)
graph_builder.add_node("callModel", call_model)
graph_builder.add_node("callTools", call_tools)
graph_builder.add_node("loadRunBook", load_runbook)
graph_builder.add_node("reAct", re_act)

graph_builder.add_edge(START, "loadRunBook")
graph_builder.add_edge("loadRunBook", "reAct")
graph_builder.add_edge("callTools", "reAct")
graph_builder.add_edge("callModel", "reAct")
graph_builder.add_conditional_edges("reAct", route, ["callModel", "callTools", "__end__"])

# graph = builder

incident_graph = graph_builder.compile()
incident_graph.name = "Incident Report Agent"


# Create an initial state with an incident report message
initial_state = IncidentReportState(messages=[{"role": "system", "content": " title: S3 Bucket Access Denied report: | Issue: Application Crashing on Login Description: After a recent deployment, users reported that the application crashes upon entering valid login credentials. The issue was traced to a null pointer exception introduced in the new authentication logic. Impact: Users are unable to log in, resulting in service downtime for 100% of active users. Resolution: Rolled back to the previous version of the login module and scheduled a hotfix deployment after thorough testing."}])
# initial_state = IncidentReportState(messages=[SystemMessage(content="Incident reported: Server outage detected.").dict()])

# Run the graph
async def main():
    result = await incident_graph.ainvoke(initial_state)
    print("Final State:", result)

asyncio.run(main())
