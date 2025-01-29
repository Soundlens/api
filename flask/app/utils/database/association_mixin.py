import inspect

from app import db
from app.exceptions import ImplementationException
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy import inspect as inspect_orm

from sqlalchemy.orm.util import AliasedClass
from sqlalchemy import inspect as inspect_orm


def get_discriminator(cls, mixin_cls=db.Model, tablename=True):
    if isinstance(cls, AliasedClass):
        insp = inspect_orm(cls)
        cls = insp.mapper.class_

    if not inspect.isclass(cls):
        cls = cls.__class__

    if not issubclass(cls, mixin_cls):
        raise ImplementationException(f"{cls} does not inherit from {mixin_cls}")

    # Direct connection with mixin class
    if mixin_cls in cls.__bases__:
        return cls.__tablename__ if tablename else cls.__name__

    for base in cls.__bases__:
        try:
            return get_discriminator(cls=base, mixin_cls=mixin_cls, tablename=tablename)
        except:
            pass

    raise ImplementationException(
        f"{cls} does not inherit from {mixin_cls} this should never happen"
    )


def check_mixins(cls, mixin_cls, strict=False):

    if isinstance(cls, AliasedClass):
        insp = inspect_orm(cls)
        cls = insp.mapper.class_

    if not inspect.isclass(cls):
        cls = cls.__class__

    # Direct connection with mixin class
    if mixin_cls in [base.__name__ if not strict else base for base in cls.__bases__]:
        return True

    for base in [base for base in cls.__bases__ if not strict]:
        try:
            return check_mixins(cls=base, mixin_cls=mixin_cls)
        except:
            pass

    return False
