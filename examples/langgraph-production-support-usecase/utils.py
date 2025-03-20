from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

class Message:
    @staticmethod
    def last_message(messages: list[BaseMessage]) -> BaseMessage:
        return messages[-1] if messages else None
    
    @staticmethod
    def human(content: str) -> HumanMessage:
        return HumanMessage(content=content)
    
    @staticmethod
    def system(content: str) -> SystemMessage:
        return SystemMessage(content=content)