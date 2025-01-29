from app import ma


class FormattedTimeDeltaField(ma.Field):
    def _serialize(self, value, attr, obj):
        return str(value) if value else None
