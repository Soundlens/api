import magic
import base64
import io
from app.utils.app import Enum
from io import BytesIO
import base64



IMAGE_FORMATS = ["image/png", "image/jpeg", "image/gif", "image/bmp", "image/tiff"]


def get_mime_type(file):
    cursor_position = file.tell()
    file.seek(0, 0)
    mime_type = magic.from_buffer(file.read(), mime=True)
    file.seek(cursor_position, 0)
    return mime_type


def get_file_size(file):
    cursor_position = file.tell()

    # Move cursor to end of file
    file.seek(0, 2)

    size = file.tell()

    # Move cursor to previous position
    file.seek(cursor_position, 0)
    return size


def reader_from_b64(b64file):
    return io.BytesIO(base64.b64decode(b64file))


class FileStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class FileType(Enum):
    EXPORT = "export"
    IMPORT = "import"
    IMAGE = "image"
    AUDIO = "audio" 
    VIDEO = "video"
    PDF = "pdf"
