from app import ma
from app.utils.app import import_blueprint
from app.utils.database import check_mixins
from app.utils.schemas.utils import generate_uischema


class CustomSQLAlchemySchema(ma.SQLAlchemySchema):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.apply_mixins()
        
        fields_to_include = {
            name: field
            for name, field in self.declared_fields.items()
            if not field.dump_only
        }

        # get only names of fields
        fields = fields_to_include.keys()

        elements_per_row = 3  # You can customize this as needed

        # raise Exception(super().Meta.__dict__)
        current_meta = getattr(self.Meta, "react_uischema_extra", {})
        # print("current_meta", current_meta, flush=True)
        # print("AA " * 100, flush=True)
        if not current_meta:
            self.Meta.react_uischema_extra = {}

        self.Meta.react_uischema_extra = generate_uischema(fields, elements_per_row, current_meta)

    def apply_mixins(self):

        optional_mixins_modules = {
            "app.api.tags.schemas": ["HasTagsSchemaMixin"],
            "app.api.files.schemas": ["HasFilesSchemaMixin"],
            "app.api.comments.schemas": ["HasCommentsSchemaMixin"],
            "app.utils.schemas.utils": ["UserStampedSchemaMixin", "MyModelSchemaMixin"],
        }

        optional_mixins_modules_mapper = {
            "HasTagsSchemaMixin": "CanHaveTagMixin",
            "HasFilesSchemaMixin": "CanHaveFileMixin",
            "HasCommentsSchemaMixin": "CanHaveCommentMixin",
            "UserStampedSchemaMixin": "UserStampedMixin",
            "MyModelSchemaMixin": "MyModel",
        }

        mixin_schemas_mapper = {}
        for module, fns in optional_mixins_modules.items():

            for fn in fns:
                mixin_schemas_mapper[optional_mixins_modules_mapper[fn]] = (
                    import_blueprint(module, fn)
                )

        model = self.opts.model
        for mixin, mixin_schema in mixin_schemas_mapper.items():
            if check_mixins(model, mixin):
                # print("Model already has mixin", mixin, flush=True)
                for field_name, field in mixin_schema._declared_fields.items():
                    if field_name not in self._declared_fields:
                        self._declared_fields[field_name] = field

        my_model_mixin = mixin_schemas_mapper.pop("MyModel", None)

        if my_model_mixin:
            for field_name, field in my_model_mixin._declared_fields.items():
                if field_name not in self._declared_fields:
                    self._declared_fields[field_name] = field

