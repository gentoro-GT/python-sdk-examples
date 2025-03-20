import yaml
import os
from typing import Dict, List, Any

class Template:
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content

class PromptTemplates:
    def __init__(self, templates: List[Template]):
        self.templates = templates

class TemplateGenerator:
    def __init__(self):
        self._data: PromptTemplates | None = None
        
        file_path = os.path.join(os.path.dirname(__file__), "templates.yaml")
        with open(file_path, "r", encoding="utf-8") as file:
            file_contents = yaml.safe_load(file)
            
        templates = [Template(**template) for template in file_contents.get("templates", [])]
        self._data = PromptTemplates(templates)
    
    def template(self, name: str) -> str:
        if self._data is None:
            raise ValueError("Template file not initialized")
        
        template = next((t for t in self._data.templates if t.name == name), None)
        if template is None:
            raise ValueError(f"Template {name} not found")
        
        return template.content
    
    def formatted_template(self, name: str, values: Dict[str, Any]) -> str:
        content = self.template(name)
        # print("Template before replacement:", content)

        for key, value in values.items():
            # Convert list or other types to string
            if isinstance(value, list):
                value = "\n".join(value)  # Convert list to a newline-separated string
            elif not isinstance(value, str):
                value = str(value)  # Convert other data types to string

            # print("Replacing:", f"{{{{{key}}}}}")  # Debugging statement
            content = content.replace(f"{{{{{key}}}}}", value)

        return content
