from marshmallow import validate, post_dump
from app import ma
from app.api.files.database import File
from app.utils.schemas.pagination import PaginationSchema
from app.utils.schemas.utils import (
    EnumField,
    QuerySchema,
    ArgList,
    CustomSQLAlchemySchema,
)
from app.utils.schemas.pagination import PaginationSchema
from app.utils.app.file import FileStatus, FileType
from flask_babel import lazy_gettext as _

# --------------- File model Schema------------------------------------


class FileSchema(CustomSQLAlchemySchema):
    class Meta:
        model = File
        ordered = True
        description = "This schema represents a File model"

    id = ma.auto_field(dump_only=True)

    file_name = ma.auto_field(
        dump_only=True,
        metadata={"title":"file_name", "description": "The name of the File "},
        error_messages={"required": "File name is required"},
    )

    mime_type = ma.auto_field(
        dump_only=True,
        metadata={"title":"mime_type", "description": "format of the File"},
        error_messages={"required": "File format is required"},
        validate=validate.Length(min=0),
    )

    size = ma.auto_field(
        dump_only=True,
        metadata={"title":"size", "description": "Size of the File"},
    )

    url = ma.String(
        dump_only=True,
        metadata={"title":"url", "description": "link of the File"},
        error_messages={"required": "File link is required"},
        validate=validate.Length(min=0),
    )

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {key: value for key, value in data.items() if value is not None}


class OriginFileSchema(CustomSQLAlchemySchema):
    class Meta:
        ordered = True

    uid = ma.String(required=False)


class UploadDocumentSchema(CustomSQLAlchemySchema):
    class Meta:
        ordered = True

    uid = ma.String(required=False)
    lastModified = ma.Integer(required=False)
    lastModifiedDate = ma.String(required=False)
    name = ma.String(required=False)
    size = ma.Integer(required=False)
    type = ma.String(required=False)
    percent = ma.Integer(required=False)
    originFileObj = ma.Nested(OriginFileSchema, required=False)
    url = ma.String(required=False)
    # The frontend sends the base64 field in the following format:
    # data:application/pdf;base64,<base 64 here>
    # We use this method to extract only the base64
    base64 = ma.Method(serialize=None, deserialize="extract_b64", required=False)

    def extract_b64(self, return_values):
        return return_values.split(",")[-1]

    def _jsonschema_type_mapping():
        return {
            # "properties": {
            "upload_files": {
                "title": "upload_files",
            },
            # },
        }


class UploadFilesSchema(ma.Schema):
    class Meta:
        ordered = True

    upload_files = ma.Nested(
        UploadDocumentSchema, many=True, load_only=True, load_default=[]
    )


class HasFilesSchemaMixin(UploadFilesSchema):
    files = ma.Nested(FileSchema, many=True, dump_only=True)


# pagination for Tag Schema
class PaginatedFileSchema(ma.Schema):
    class Meta:
        ordered = True

    pagination = ma.Nested(PaginationSchema)
    result = ma.Nested(FileSchema, many=True)


# pagination for Tag Schema
class BarCodeSchema(ma.Schema):
    barCode = ma.String(required=True)


class FilesQuerySchema(QuerySchema):
    file_type = EnumField(
        enum=FileType,
        required=False,
        load_default=None,
        metadata={"title":"file_type", "description": "The type of the file"},
    )

    status = EnumField(
        enum=FileStatus,
        required=False,
        load_default=None,
        metadata={"title":"status", "description": "The status of the file"},
    )

    mime_types = ArgList(
        ma.String,
        required=False,
        load_default=None,
        metadata={"title":"mime_types", "description": "filter by tag type"},
    )


class ExportSchema(ma.Schema):
    class Meta:
        ordered = True

    _type = ma.String(
        required=True,
        metadata={"title":"type", "description": "The type of the export"},
        error_messages={"required": "Export type is required"},
        validate=validate.Length(min=0),
    )
