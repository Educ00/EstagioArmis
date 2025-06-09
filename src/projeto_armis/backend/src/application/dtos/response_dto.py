import json

class ResponseDTO:
    """
    Data Transfer Object that enforces non-null fields and
    serializes directly from provided keyword arguments.
    """
    def __init__(self, **kwargs):
        if not kwargs:
            raise ValueError("At least one field must be provided")
        for name, value in kwargs.items():
            if value is None:
                raise ValueError(f"Field '{name}' cannot be None")
            setattr(self, name, value)

    def to_dict(self) -> dict:
        """
        Convert the DTO instance into a standard dictionary.
        """
        return self.__dict__.copy()

    def __str__(self) -> str:
        """
        JSON string representation of the DTO.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __repr__(self) -> str:
        return self.__str__()
