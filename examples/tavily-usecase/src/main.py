import os
from dotenv import load_dotenv

from Gentoro import Gentoro, SdkConfig, Providers
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage, HumanMessage

# Load env variables
load_dotenv()

# Initialize Gentoro and OpenAI
gentoro = Gentoro(SdkConfig(provider=Providers.LANGCHAIN))
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

def filter_valid_messages(messages):
    return [
        msg for msg in messages
        if (isinstance(msg, dict) and 'role' in msg and 'content' in msg)
        or isinstance(msg, (AIMessage, ToolMessage))
    ]

def prepare_messages(messages):
    return [
        msg.model_dump() if isinstance(msg, (AIMessage, SystemMessage, ToolMessage, HumanMessage)) else msg
        for msg in messages
    ]

print("🤖 LangChain Chatbot w/ Gentoro Tools via .bind_tools Ready!\n")

user_input = input("You: ")

messages = [{"role": "user", "content": user_input}]
bridge_uid = os.getenv("GENTORO_BRIDGE_UID")
tools = gentoro.get_tools(bridge_uid, messages)
llm_with_tools = llm.bind_tools(tools)

# First LLM response
response = llm_with_tools.invoke(prepare_messages(messages))
messages.append(response)

# If tools needed, run them
tool_calls = getattr(response, "tool_calls", [])
if tool_calls:
    tool_outputs = gentoro.run_tools(bridge_uid, messages, tool_calls=tool_calls)
    messages.extend(tool_outputs)

    messages = filter_valid_messages(messages)
    final_response = llm_with_tools.invoke(messages)
    print(f"AI: {final_response.content}")
else:
    print(f"AI: {response.content}")
