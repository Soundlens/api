from app import ma


class NullableString(ma.String):
    def _deserialize(self, value, attr, data, **kwargs):
        if value == "":
            return None
        return super()._deserialize(value, attr, data, **kwargs)
