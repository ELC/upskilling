from typing import Any, ClassVar, cast, get_args

from pydantic import BaseModel

from .models import Base


class BaseMapper[DomainT: BaseModel, ModelT: Base]:
    """Maps a single domain entity to a single database entity.

    Subclasses configure two class variables:

    * ``_exclude_fields`` - domain fields to drop (auto-generated IDs,
      computed props, collections).
    * ``_fk_mappings`` - nested domain objects to flatten into FK columns.
      A plain ``str`` value is used as both the FK column name **and** the key
      inside the nested dict (e.g. ``"user": "user_id"``).
      A ``tuple[str, str]`` of ``(fk_column, id_key)`` is used when the column
      name differs from the nested key
      (e.g. ``"manager": ("manager_user_id", "user_id")``).

    If a single domain entity maps to multiple database entities, define
    one mapper per target model.
    """

    _exclude_fields: ClassVar[frozenset[str]] = frozenset()
    _fk_mappings: ClassVar[dict[str, str | tuple[str, str]]] = {}

    @classmethod
    def _model_class(cls) -> type[ModelT]:
        return cast("type[ModelT]", get_args(cls.__orig_bases__[0])[1])  # type: ignore[attr-defined]

    @classmethod
    def _to_db_dict(cls, data: DomainT, *, exclude_unset: bool = False) -> dict[str, Any]:
        d = data.model_dump(exclude_unset=exclude_unset)

        for field, mapping in cls._fk_mappings.items():
            if field not in d:
                continue
            nested = d.pop(field)
            if isinstance(mapping, tuple):
                fk_column, id_key = mapping
            else:
                fk_column = id_key = mapping
            if nested is not None:
                d[fk_column] = nested[id_key]

        for field in cls._exclude_fields:
            d.pop(field, None)

        return d

    @classmethod
    def to_model(cls, data: DomainT) -> ModelT:
        """Create a new database entity from a domain object."""
        db_dict = cls._to_db_dict(data)
        model_cls = cls._model_class()
        return model_cls(**db_dict)

    @classmethod
    def update_model(cls, instance: ModelT, data: DomainT) -> None:
        """Apply domain object changes onto an existing database entity."""
        db_dict = cls._to_db_dict(data, exclude_unset=True)
        for key, value in db_dict.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

    @classmethod
    def to_domain(cls, instance: ModelT) -> DomainT:
        """Convert a database entity to a domain object."""
        return DomainT.model_validate(instance)
