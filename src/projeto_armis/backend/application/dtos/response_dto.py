import json

class ResponseDTO:
    def __init__(self, title: str, **kwargs):
        self.title : str = title
        self.body : dict = kwargs
        
    def to_dict(self):
        """
        Converts the current object to dict
        :return: dict
        """
        return {
            "title": self.title,
            "body": self.body
        }
    
    def __str__(self):
        json.dumps(self.to_dict())

    def __repr__(self):
        return self.__str__()