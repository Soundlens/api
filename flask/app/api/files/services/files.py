from typing import List, Dict, Any

from app.main import db
from app.exceptions import BusinessLogicException, ImplementationException
from app.api.files.integrations.aws import (
    get_s3_client,
    upload_file as aws_upload_file,
    get_file_url,
)
from sqlalchemy import or_, desc, and_, func
from flask import current_app
from uuid import uuid4
from app.utils.services import generic_filters
from app.utils.app import match_string, convert_to_list
from app.exceptions import BusinessLogicException
from app.utils.app.file import FileStatus, FileType

from app.utils.app.file import get_mime_type, get_file_size
from typing import Optional
from app.api.files.database import (
    File,
    CanHaveFileMixin,
    FileAssociation,
)
from app.utils.database import get_discriminator


class FileService:
    def get(id):
        file = db.session.get(File, id)
        if file is None:
            raise BusinessLogicException(f"File {id} not found", code=404)
        return file

    def create(file_name=None, stream=None, created_by: "User" = None, **kwargs):

        file_model = File(
            mime_type=None,
            size=None,
            remote_name=None,
            file_name=file_name,
            created_by=created_by,
        )

        db.session.add(file_model)

        if stream is not None:
            print("A " * 100, flush=True)
            print(file_name, flush=True)
            file_model = FileService.upload_file(
                file_model=file_model, stream=stream, remote_name=file_name, **kwargs
            )
            print("B " * 100, flush=True)
            print(file_model.url, flush=True)

        return file_model

    @generic_filters(cls=File)
    @convert_to_list("mime_types")
    def search(
        entity: CanHaveFileMixin = None,
        search: str = None,
        status: FileStatus = None,
        user_id: int = None,
        file_type: FileType = None,
        mime_types: str = None,
    ):
        query = db.session.query(File)

        if search is not None:
            query = query.filter(
                or_(
                    match_string(File.file_name, search),
                    match_string(File.remote_name, search),
                    match_string(File.mime_type, search),
                    match_string(File.status, search),
                )
            )

        if entity is not None:
            query = query.join(
                FileAssociation, FileAssociation.file_id == File.id
            ).filter(
                FileAssociation.entity_id == entity.id,
                FileAssociation.entity_class
                == get_discriminator(entity.__class__, CanHaveFileMixin),
            )

        if status is not None:
            query = query.filter(File.status == status)

        if file_type is not None:
            query = query.filter(File.file_type == file_type)

        if user_id is not None:
            query = query.filter(File.user_id == user_id)

        if mime_types is not None:
            query = query.filter(File.mime_type.in_(mime_types))

        return query

    def upload_file(file_model: File, stream, remote_name=None, **kwargs):
        if remote_name is None:
            remote_name = str(uuid4())

        file_model.remote_name = remote_name
        file_model.mime_type = get_mime_type(stream)
        file_model.size = get_file_size(stream)

        aws_upload_file(
            current_app.config["AWS_S3_CLIENT"],
            current_app.config["AWS_S3_BUCKET_NAME"],
            remote_name,
            stream,
            file_model.mime_type,
        )
        file_model.url = get_file_url(
            current_app.config["AWS_S3_CLIENT"],
            current_app.config["AWS_S3_BUCKET_NAME"],
            remote_name,
        )

        file_model.status = FileStatus.DONE
        db.session.add(file_model)
        return file_model

    def add_files(entity, user, files=[]):
        for f in files:
            entity.files.append(
                FileService.create(
                    stream=f.stream, file_name=f.file_name, created_by=user
                )
            )


        return entity

    def remove_file(entity, user, file_id):
        assoc = (
            db.session.query(FileAssociation)
            .filter(
                FileAssociation.file_id == file_id,
                FileAssociation.entity_class == get_discriminator(entity),
                FileAssociation.entity_id == entity.id,
            )
            .first()
        )
        if assoc is not None:
            db.session.delete(assoc)

        return entity

    def remove_files(entity, user, file_ids):
        for file_id in file_ids:
            FileService.remove_file(entity, user, file_id)

        return entity
