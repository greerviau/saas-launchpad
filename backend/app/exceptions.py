class NotFoundException(Exception):
    pass


class BadRequestException(Exception):
    pass


class UnauthorizedException(Exception):
    pass


class InternalServerErrorException(Exception):
    pass


class TooManyRequestsException(Exception):
    pass
