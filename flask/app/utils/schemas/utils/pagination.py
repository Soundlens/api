from app import ma


def paginate_query(query, page, per_page):
    return ((query, page, per_page),)


def get_paginated_schema(schema_class, **class_kwargs):
    class PaginatedSchema(ma.Schema):
        class Meta:
            ordered = True
            # orig_schema = schema_class
            # change Meta class and add a property to the Meta (ignore_optional_mixins) True

            schema_class.Meta.ignore_optional_mixins = True
            orig_schema = schema_class

        def dump(self, data, **kwargs):

            _exclude = (
                # "files",
                "comments",
            )
            # check if the fields are in the class_kwargs
            for field in _exclude:
                if field not in schema_class._declared_fields.keys():
                    # remove the field from the exclude list
                    _exclude = [x for x in _exclude if x != field]

            # append the exclude fields from the class_kwargs
            if "exclude" in class_kwargs:
                _exclude = _exclude + list(class_kwargs.pop("exclude"))

            query, page, per_page = data
            if per_page is None:
                return schema_class(exclude=tuple(_exclude), **class_kwargs).dump(
                    query.all(), many=True
                )
            elif per_page == 0:
                per_page = query.count()

            data = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                "result": schema_class(exclude=tuple(_exclude), **class_kwargs).dump(
                    data.items, many=True
                ),
                "pagination": {
                    "has_next": data.has_next,
                    "count": data.total,
                    "page": data.page,
                    "per_page": data.per_page,
                },
            }

    return PaginatedSchema
