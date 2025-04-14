from flask import jsonify

class ResponseDTO:
    def __init__(self, response_code: int, body: str, metadata: {str}):
        self.response_code : int = response_code
        self.body : str = body
        self.metadata : {str} = metadata
        
    def dto_json(self):
        """
        Converts the current object to JSON using flask.jsonify
        :return: JSON
        """
        return jsonify({
            "response_code": self.response_code,
            "body": self.body,
            "metadata": self.metadata
        })