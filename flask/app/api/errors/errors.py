from flask import Blueprint, current_app, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException, InternalServerError
from app.main import apifairy, logger
from app.exceptions.exception import (
    BusinessLogicException,
    InsufficientAmountException,
    DatabaseInconsistencyException,
    ImplementationException,
)
import traceback

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(HTTPException)
def http_error(error):
    traceback.print_exc()
    exception_url = request.url
    current_app.logger.error(
        f"{error.code}: {error.name}: {error.description}: {exception_url}"
    )
    return {
        "success": False,
        "result": {
            "code": error.code,
            "message": error.name,
            "description": error.description,
        },
    }, error.code


@errors.app_errorhandler(BusinessLogicException)
def business_logic_error(error):
    traceback.print_exc()
    error.log(request.url)

    if error.errors == []:
        return {
            "success": False,
            "result": {
                "code": error.code,
                "description": error.description,
            },
        }, error.code
    else:
        return {"success": False, "result": error.to_dict()}, error.code


@errors.app_errorhandler(DatabaseInconsistencyException)
def database_inconsistency_error(error):
    traceback.print_exc()
    exception_url = request.url
    current_app.logger.error(f"{error.code}: {error.description}: {exception_url}")
    return {
        "success": False,
        "result": {
            "code": error.code,
            "description": error.description,
        },
    }, error.code


@errors.app_errorhandler(ImplementationException)
def implementation_error(error):
    traceback.print_exc()
    exception_url = request.url
    current_app.logger.error(f"{error.code}: {error.description}: {exception_url}")
    return {
        "success": False,
        "result": {
            "code": 500,
            "description": error.description,
        },
    }, error.code


@errors.app_errorhandler(InsufficientAmountException)
def insufficient_amount_error(error):
    traceback.print_exc()
    exception_url = request.url
    current_app.logger.error(f"{error.code}: {error.description}: {exception_url}")
    return {
        "success": False,
        "result": {
            "code": error.code,
            "description": error.description,
        },
    }, error.code


@errors.app_errorhandler(IntegrityError)
def sqlalchemy_integrity_error(error):  # pragma: no cover
    traceback.print_exc()
    url = request.url
    current_app.logger.error(f"{str(error.orig)}: {url}")
    return {
        "success": False,
        "result": {
            "code": 400,
            "message": "Database integrity error",
            "description": str(error.orig),
        },
    }, 400


@errors.app_errorhandler(SQLAlchemyError)
def sqlalchemy_error(error):  # pragma: no cover
    traceback.print_exc()
    url = request.url
    current_app.logger.error(f"{InternalServerError.code}: {url} : {str(error)}")

    if current_app.config["DEBUG"] is True:
        return {
            "code": InternalServerError.code,
            "message": "Database error",
            "description": str(error),
        }, 500
    else:
        return {
            "code": InternalServerError.code,
            "message": InternalServerError().name,
            "description": InternalServerError.description,
        }, 500


@apifairy.error_handler
def validation_error(code, messages):
    traceback.print_exc()
    url = request.url
    current_app.logger.error(f"{code} : {messages}: {url}")
    return {
        "success": False,
        "result": {
            "code": code,
            "message": "Validation Error",
            "description": (
                "The server found one or more errors in the "
                "information that you sent."
            ),
            "errors": messages,
        },
    }, code
