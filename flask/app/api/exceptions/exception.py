from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

class BusinessLogicException(Exception):
    """
    This exception represents an invalid action by the user.
    """

    def __init__(self, description, errors=[], code=500):
        self.description = description
        self.code = code
        self.errors = errors

    def to_dict(self):
        if len(self.errors) == 1:
            return self.errors[0].to_dict()

        result = {
            "code": self.code,
            "description": self.description,
        }
        if self.errors != []:
            result["errors"] = [e.to_dict() for e in self.errors]
            
        return result



class InsufficientAmountException(Exception):
    def __init__(self, description):
        self.message = "Insufficient Amount: " + description
        self.code = 400


class ImplementationException(Exception):
    """
    This exception represents an implementation error by the developers
    """

    def __init__(self, description):
        self.description = description
        self.code = 500


class DatabaseInconsistencyException(AttributeError, Exception):
    """
    This exception represents an inconsistent database state (should never happen)
    """

    def __init__(self, description):
        self.description = description
        self.code = 500



