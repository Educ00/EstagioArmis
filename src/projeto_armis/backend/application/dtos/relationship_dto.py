import json

class RelationshipDTO:
    def __init__(self, source : str, target: str, value: str):
        self.source = source
        self.target = target
        self.value = value
        
    def to_dict(self):
        return {
            "source": self.source,
            "target": self.target,
            "value": self.value
        }
    
    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)

    def __repr__(self):
        return self.__str__()