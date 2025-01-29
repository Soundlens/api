from app import ma

class UserStampedSchemaMixin(ma.Schema):

    class Meta:
        ordered = True
        
    created_by = ma.Nested("UserSchema", dump_only=True, only=["id", "name", "email"])

    updated_by = ma.Nested("UserSchema", dump_only=True, only=["id", "name", "email"])


