from flask import Blueprint, abort, request, jsonify
from app.main import db
from apifairy import authenticate, body, response, other_responses, arguments
from app.api.files.database import File

import json
from app.api.files.services import FileService, ImportExportService

from app.utils.app.file import reader_from_b64
from app.utils.services import NewFileData
from app.utils.app.file import IMAGE_FORMATS
from app.exceptions import BusinessLogicException
from app.utils.database import get_discriminator


from app.api.files.schemas import (
    FileSchema,
    UploadFilesSchema,
    PaginatedFileSchema,
    UploadDocumentSchema,
    BarCodeSchema,
    FilesQuerySchema,
)

# files = Blueprint("files", __name__)
file_schema = FileSchema()
paginated_files_schema = PaginatedFileSchema()
updated_file_schema = FileSchema(partial=True)
barCode_schema = BarCodeSchema()


from flask import Blueprint, current_app, jsonify
from apifairy import authenticate, body, response, arguments, other_responses

from app import db

from app.utils.routes import (
    get_file_data,
    format_response_message,
)
from app.utils.schemas.utils import (
    get_paginated_schema,
    paginate_query,
)

bp = Blueprint("files", __name__)


@bp.route("/files", methods=["POST"])
@body(UploadDocumentSchema)
@response(file_schema, 201, description="Newly created File")
@other_responses({401: "Invalid inputs", 400: "Bad Request"})
def new(args):
    """Add new File"""

    try:
        user = token_auth.current_user()
        f = NewFileData(args["name"], reader_from_b64(args["base64"]))

        file = FileService.create(
            stream=f.stream, file_name=f.file_name, created_by=user
        )
        db.session.commit()
        return file
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        raise e


@bp.route("/files", methods=["GET"])
@arguments(FilesQuerySchema)
@response(
    get_paginated_schema(FileSchema),
    200,
    description="Success: batches Retrieved Successfully",
)
@other_responses({404: "files not found"})
def all(args):
    """Retrieve all Files"""

    page = args.pop("page", None)
    per_page = args.pop("per_page", None)
    files = FileService.search(**args)
    return paginate_query(query=files, page=page, per_page=per_page)


@bp.route("/files/<int:id>", methods=["GET"])
@arguments(FilesQuerySchema)
@response(file_schema, description="Retrieve an File by Id")
@other_responses({404: "File not found"})
def get(id):
    """Retrieve an File by id"""
    file = FileService.get(id)

    return file


@bp.route("/files/<int:id>", methods=["PUT"])
@body(updated_file_schema)
@response(file_schema, description="Update an File by Id")
@other_responses({403: "Not allowed to edit this File", 404: "File not found"})
def put(data, id):
    """Update an File by id"""
    file = FileService.get(id)

    file.update(data)
    db.session.commit()
    return file


@bp.route("/files/<int:id>", methods=["DELETE"])
@other_responses({403: "Not allowed to delete the File"})
def delete(id):
    """Delete an File by id"""
    file = FileService.get(id)

    db.session.delete(file)
    db.session.commit()
    return jsonify({"success": "delete File successfully"}, 204)

