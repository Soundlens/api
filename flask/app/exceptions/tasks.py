from app.exceptions.exception import BusinessLogicException


class InvalidTaskStatusException(BusinessLogicException):
    code = 404

    def __init__(self, description):
        super().__init__(description)


class InvalidUserException(BusinessLogicException):
    code = 403

    def __init__(self, description):
        super().__init__(description)
