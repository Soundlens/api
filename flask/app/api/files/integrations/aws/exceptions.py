class AWSException(Exception):
    def __init__(self, description):
        self.description = description


class AWSNotFoundException(AWSException):
    pass


class AWSForbiddenException(AWSException):
    pass


class AWSInvalidBucketNameException(AWSException):
    pass


class AWSBucketAlreadyExistsException(AWSException):
    pass


class AWSBucketNotEmptyException(AWSException):
    pass
