from flask import Blueprint, request
from app.api.files.integrations.aws import list_buckets, bucket_exists, create_bucket, delete_bucket, upload_file, get_all_files, delete_file, get_file_url
from app.utils.app.file import get_mime_type, get_file_size

from flask import current_app as app

aws_bp = Blueprint("aws", __name__)


@aws_bp.route("/aws")
def testing():
    return "ok"


@aws_bp.route("/aws/buckets", methods=["GET"])
def all_buckets():
    return list_buckets(app.config["AWS_S3_CLIENT"])


@aws_bp.route("/aws/buckets/<string:bucket_name>", methods=["GET"])
def get(bucket_name):
    if bucket_exists(app.config["AWS_S3_CLIENT"], bucket_name):
        return f"Bucket {bucket_name} exists"
    else:
        return f"Bucket {bucket_name} does not exist"


@aws_bp.route("/aws/buckets/<string:bucket_name>", methods=["POST"])
def create(bucket_name):
    create_bucket(app.config["AWS_S3_CLIENT"], bucket_name)
    return "created"


@aws_bp.route("/aws/buckets/<string:bucket_name>", methods=["DELETE"])
def delete(bucket_name):
    delete_bucket(app.config["AWS_S3_CLIENT"], bucket_name)
    return f'Successfully deleted bucket "{bucket_name}"'


@aws_bp.route("/aws/buckets/<string:bucket_name>/files", methods=["POST"])
def save_file(bucket_name):
    new_files = []
    for key in request.files.keys():
        for file in request.files.getlist(key):
            file_name = file.filename
            stream = file.stream
            mime_type = get_mime_type(stream)
            size = get_file_size(stream)
            upload_file(
                app.config["AWS_S3_CLIENT"],
                bucket_name,
                file_name,
                stream,
                mime_type,
            )

            url = get_file_url(app.config["AWS_S3_CLIENT"], bucket_name, file_name)

            new_files.append((file_name, f"{size} B", url))
            file.close()
    return f"Successfully created files: {new_files}"


@aws_bp.route("/aws/buckets/<string:bucket_name>/files", methods=["GET"])
def get_all_files(bucket_name):
    return get_all_files(app.config["AWS_S3_CLIENT"], bucket_name)


@aws_bp.route(
    "/aws/buckets/<string:bucket_name>/files/<string:file_name>",
    methods=["DELETE"],
)
def delete_file(bucket_name, file_name):
    delete_file(app.config["AWS_S3_CLIENT"], bucket_name, file_name)
    return f'"{file_name}" deleted successfully from bucket "{bucket_name}"'


@aws_bp.route("/aws/buckets/<string:bucket_name>/files/all", methods=["DELETE"])
def delete_all_files(bucket_name):
    files = get_all_files(app.config["AWS_S3_CLIENT"], bucket_name)
    deleted = []
    for file in files:
        key = file["Key"]
        delete_file(app.config["AWS_S3_CLIENT"], bucket_name, key)
        deleted.append(key)

    if len(deleted) > 0:
        return f"Successfully deleted {deleted}"
    else:
        return f"No files to delete"
