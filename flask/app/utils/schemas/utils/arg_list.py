from app import ma


class ArgList(ma.Field):
    def __init__(self, field, separator: str = ",", *args, **kwargs):
        self.field = field
        self.separator = separator
        super().__init__(*args, **kwargs)

    def _serialize(self, values, attr, obj):
        if values is None:
            return ""
        return self.separator.join([self.field.serialize(value) for value in values])

    def _deserialize(self, value, attr, data, partial=None):
        if value is None:
            return []
        
        if self.field == ma.String:
            return value.split(self.separator)

        return [self.field.deserialize(v) for v in value.split(self.separator)]


class ListIdsParse(ma.Field):
    def __init__(self, field, separator: str = ",", *args, **kwargs):
        self.field = field
        self.separator = separator
        super().__init__(*args, **kwargs)

    def _serialize(self, values, attr, obj):
        if values is None:
            return ""
        return self.separator.join([self.field.serialize(value) for value in values])

    def _deserialize(self, value, attr, data, partial=None):
        if value is None:
            return []
        
        if isinstance(value, list):
            value = ", ".join([str(item) for item in value])
        
        if self.field == ma.String:
            return value.split(self.separator)

        return [self.field.deserialize(v) for v in value.split(self.separator)]
