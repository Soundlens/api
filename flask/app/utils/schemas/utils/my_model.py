from app import ma
from app.utils.schemas.utils import UTCDateTime

class MyModelSchemaMixin(ma.Schema):
    id = ma.String(dump_only=True)

    inserted_at = UTCDateTime(format="%Y-%m-%d %H:%M", dump_only=True)

    updated_at = UTCDateTime(format="%Y-%m-%d %H:%M", dump_only=True)
