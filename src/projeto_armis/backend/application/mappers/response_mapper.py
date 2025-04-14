from application.dtos.response_dto import ResponseDTO


class ResponseMapper:
    @staticmethod
    def to_response_dto(response_code: int, body: str, metadata: {str}):
        return ResponseDTO(response_code=response_code, body=body, metadata=metadata)