from http import HTTPStatus


class InvalidInputData(Exception):
    ERR_STATUS = HTTPStatus.BAD_REQUEST
    ERR_MESSAGE = "InvalidInputData"
