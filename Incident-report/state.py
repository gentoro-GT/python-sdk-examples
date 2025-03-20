from typing import List, Optional
from pydantic import BaseModel

class BaseMessage(BaseModel):
    role: str
    content: str
    id: Optional[str] = None

class StateAnnotation(BaseModel):
    """
    A graph's StateAnnotation defines:
    1. The structure of the data passed between nodes
    2. Default values for each field
    3. Reducers for state updates
    """
    messages: List[BaseMessage] = []
    end_graph_signal: bool = False

    def add_message(self, message: BaseMessage):
        """Appends a new message to the state."""
        existing_ids = {msg.id for msg in self.messages if msg.id}
        if message.id in existing_ids:
            self.messages = [msg if msg.id != message.id else message for msg in self.messages]
        else:
            self.messages.append(message)
