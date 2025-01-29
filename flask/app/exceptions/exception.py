from flask import current_app


class BusinessLogicException(Exception):
    """
    This exception represents an invalid action by the user.
    """
    

    def __init__(self, description, errors=[], code=500):
        print("make exception")
        self.description = description
        self.code = code
        self.errors = errors
        
        print(self.code)
        print(self.description)

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

    def log(self, exception_url):
        current_app.logger.error(f"{self.code}: {self.description}: {exception_url}")
        for e in self.errors:
            e.log(exception_url)


class PermissionException(BusinessLogicException):
    def __init__(self, description: str):
        super().__init__(description, code=403)


class InsufficientAmountException(Exception):
    def __init__(self, description):
        self.description = _("Insufficient Amount: ") + description
        self.code = 400


class ImplementationException(Exception):
    """
    This exception represents an implementation error by the developers
    """

    def __init__(self, description):
        self.description = description
        self.code = 500


class DatabaseInconsistencyException(Exception):
    """
    This exception represents an inconsistent database state (should never happen)
    """

    def __init__(self, description):
        self.description = description
        self.code = 500


class UnitException(Exception):
    def __init__(self, description="", code=500):
        self.description = description
        self.code = code
