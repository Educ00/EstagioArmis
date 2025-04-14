import json

class EntityDTO:
    def __init__(self, name: str, category: str, description: str):
        self.name = name
        self.category = category
        self.description = description
        
    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description
        }
    
    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)
    
    def __repr__(self):
        return self.__str__()
        