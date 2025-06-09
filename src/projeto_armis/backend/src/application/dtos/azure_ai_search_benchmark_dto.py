class AzureAiSearchBenchmarkDTO:
    def __init__(self, response: str, docs):
        self.response = response
        self.docs = docs
        