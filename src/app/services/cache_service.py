import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel

from app.db.redis_conn import redis_client

logger = logging.getLogger(__name__)

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class CacheService:
    """
    Cache Pydantic schemas (API-safe views) in Redis.

    Key features:
    - Caches BaseModel JSON using model_dump_json / model_validate_json.
    - Composite key support via pk_field_map or heuristics.
    - Namespace and version prefixing for clean segmentation and bulk invalidation.
    - Per-model TTL overrides.
    - get_or_set convenience to fetch on miss and populate the cache.

    Notes:
    - We only cache schemas (never raw SQLAlchemy models) for security and speed.
    - Cached instances are ready-to-serialize API responses, or you can return the JSON
      directly if your handler prefers that.
    """

    def __init__(
        self,
        ttl: int = 300,
        namespace: Optional[str] = None,
        version: Optional[str] = None,
        *,
        # Map a schema class to the ordered PK field names (e.g., {UserRead: ("id",), TeamMemberRead: ("team_id","user_id")})
        pk_field_map: Optional[Dict[Type[BaseModel], Tuple[str, ...]]] = None,
        # Per-model TTL overrides (falls back to ttl above)
        ttl_overrides: Optional[Dict[Type[BaseModel], int]] = None,
        # If True, require pk_field_map entries for any schema without an `id` field
        strict_pk_resolution: bool = False,
        # Dump options propagated to model_dump_json
        dump_by_alias: bool = False,
        dump_exclude_none: bool = False,
        validate_strict: bool = False,
    ):
        self.default_ttl = int(ttl)
        self.namespace = namespace
        self.version = version
        self.pk_field_map = pk_field_map or {}
        self.ttl_overrides = ttl_overrides or {}
        self.strict_pk_resolution = strict_pk_resolution
        self.dump_by_alias = dump_by_alias
        self.dump_exclude_none = dump_exclude_none
        self.validate_strict = validate_strict

    # ---------- TTL helpers ----------

    def _ttl_for(self, schema_type: Type[SchemaType]) -> int:
        return int(self.ttl_overrides.get(schema_type, self.default_ttl))

    # ---------- PK + key helpers ----------

    def _schema_name(self, schema_type: Type[SchemaType]) -> str:
        return schema_type.__name__.lower()

    def _prefix(self, schema_type: Type[SchemaType]) -> str:
        parts: List[str] = []
        if self.namespace:
            parts.append(self.namespace)
        if self.version:
            parts.append(f"v{self.version}")
        parts.append(self._schema_name(schema_type))
        return ":".join(parts)

    def _pk_fields(self, schema_type: Type[SchemaType]) -> Tuple[str, ...]:
        # 1) explicit mapping wins
        explicit = self.pk_field_map.get(schema_type)
        if explicit:
            return explicit

        # 2) heuristics
        try:
            fields = getattr(schema_type, "model_fields", {})  # pydantic v2
        except Exception:
            fields = {}

        if "id" in fields:
            return ("id",)

        # Next best: exactly one field ending in "_id"
        id_like = tuple(name for name in fields.keys() if name.endswith("_id"))
        if len(id_like) == 1:
            return (id_like[0],)

        # Multiple *_id found or none. If strict, require explicit pk_field_map.
        if self.strict_pk_resolution:
            raise ValueError(
                f"Cannot infer PK fields for {schema_type.__name__}. Provide pk_field_map entry."
            )

        # Last resort: stable order of all fields with 'id' in the name (composite-ish)
        id_contains = tuple(sorted(n for n in fields.keys() if "id" in n))
        if id_contains:
            # This is a heuristic; consider adding an explicit pk_field_map for this schema.
            logger.debug(
                "Heuristic PK resolution for %s -> %s",
                schema_type.__name__,
                id_contains,
            )
            return id_contains

        # Give up: fallback to "id" (may raise later if missing at usage)
        return ("id",)

    def _pk_values_from_obj(self, obj: SchemaType) -> Tuple[Any, ...]:
        schema_type = type(obj)
        pk_fields = self._pk_fields(schema_type)
        try:
            values = tuple(getattr(obj, f) for f in pk_fields)
        except AttributeError as exc:
            raise ValueError(
                f"Object of type {schema_type.__name__} is missing PK field: {exc}"
            )
        if any(v is None for v in values):
            raise ValueError(
                f"Cannot cache {schema_type.__name__} with null PK component(s): {pk_fields} -> {values}"
            )
        return values

    def _pk_values_from_identifier(
        self,
        schema_type: Type[SchemaType],
        obj_id: Union[Any, Tuple[Any, ...], List[Any], Dict[str, Any]],
    ) -> Tuple[Any, ...]:
        pk_fields = self._pk_fields(schema_type)

        # Single PK: scalar is fine
        if len(pk_fields) == 1 and not isinstance(obj_id, (tuple, list, dict)):
            return (obj_id,)

        if isinstance(obj_id, (tuple, list)):
            if len(obj_id) != len(pk_fields):
                raise ValueError(
                    f"{schema_type.__name__}: expected {len(pk_fields)} PK values, got {len(obj_id)}"
                )
            return tuple(obj_id)

        if isinstance(obj_id, dict):
            # Use configured pk_fields order if available; otherwise stable sort
            ordered_fields = pk_fields or tuple(sorted(obj_id.keys()))
            try:
                return tuple(obj_id[name] for name in ordered_fields)
            except KeyError as e:
                raise ValueError(
                    f"{schema_type.__name__}: missing PK component in obj_id: {e.args[0]}"
                )

        # Fallback for single PK if user still passed scalar
        if len(pk_fields) == 1:
            return (obj_id,)
        raise ValueError(
            f"{schema_type.__name__}: composite PK requires tuple/list in PK order or dict {{pk_name: value}}."
        )

    def _key_from_values(
        self, schema_type: Type[SchemaType], pk_values: Iterable[Any]
    ) -> str:
        pk_part = ":".join(str(v) for v in pk_values)
        return f"{self._prefix(schema_type)}:{pk_part}"

    def _key_for_obj(self, obj: SchemaType) -> str:
        return self._key_from_values(type(obj), self._pk_values_from_obj(obj))

    def _key_for_id(
        self,
        schema_type: Type[SchemaType],
        obj_id: Union[Any, Tuple[Any, ...], List[Any], Dict[str, Any]],
    ) -> str:
        values = self._pk_values_from_identifier(schema_type, obj_id)
        return self._key_from_values(schema_type, values)

    # ---------- Public API ----------

    async def get(
        self,
        schema_type: Type[SchemaType],
        obj_id: Union[Any, Tuple[Any, ...], List[Any], Dict[str, Any]],
    ) -> Optional[SchemaType]:
        """
        Retrieve a cached schema instance by its ID(s).
        obj_id can be:
          - single scalar for single-PK schemas,
          - tuple/list in PK order for composite keys,
          - dict {pk_name: value}.
        """
        key = self._key_for_id(schema_type, obj_id)
        try:
            cached = await redis_client.get(key)
            if not cached:
                return None
            if isinstance(cached, bytes):
                cached = cached.decode("utf-8")
            return schema_type.model_validate_json(cached, strict=self.validate_strict)
        except Exception:
            logger.warning("Cache lookup failed for key: %s", key, exc_info=True)
            return None

    async def set(self, obj: SchemaType, *, ttl: Optional[int] = None) -> None:
        """
        Cache a schema instance. Uses configured PK fields to build the key.
        """
        try:
            key = self._key_for_obj(obj)
        except Exception:
            logger.warning(
                "Attempted to cache object of type %s but could not derive key.",
                type(obj).__name__,
                exc_info=True,
            )
            return

        try:
            payload = obj.model_dump_json(
                by_alias=self.dump_by_alias, exclude_none=self.dump_exclude_none
            )
            await redis_client.set(
                key, payload, ex=int(ttl or self._ttl_for(type(obj)))
            )
        except Exception:
            logger.warning("Failed to cache object with key: %s", key, exc_info=True)

    async def invalidate(
        self,
        schema_type: Type[SchemaType],
        obj_id: Union[Any, Tuple[Any, ...], List[Any], Dict[str, Any]],
    ) -> None:
        """
        Invalidate a single cached entry.
        """
        key = self._key_for_id(schema_type, obj_id)
        try:
            await redis_client.delete(key)
        except Exception:
            logger.warning("Failed to invalidate cache for key: %s", key, exc_info=True)

    async def get_json(
        self,
        schema_type: Type[SchemaType],
        obj_id: Union[Any, Tuple[Any, ...], List[Any], Dict[str, Any]],
    ) -> Optional[str]:
        """
        Retrieve the raw JSON string (useful if your endpoint returns JSON directly).
        """
        key = self._key_for_id(schema_type, obj_id)
        try:
            cached = await redis_client.get(key)
            if not cached:
                return None
            return cached.decode("utf-8") if isinstance(cached, bytes) else cached
        except Exception:
            logger.warning("Cache lookup (raw) failed for key: %s", key, exc_info=True)
            return None

    async def get_or_set(
        self,
        schema_type: Type[SchemaType],
        obj_id: Union[Any, Tuple[Any, ...], List[Any], Dict[str, Any]],
        loader: Callable[[], Awaitable[Optional[SchemaType]]],
        *,
        ttl: Optional[int] = None,
        return_json: bool = False,
    ) -> Optional[Union[SchemaType, str]]:
        """
        Fetch from cache; on miss, await loader(), cache the result, and return it.
        Optionally return the cached JSON string instead of a model.
        """
        # 1) Try cache
        cached_model = await self.get(schema_type, obj_id)
        if cached_model is not None:
            if return_json:
                return await self.get_json(schema_type, obj_id)
            return cached_model

        # 2) Load on miss
        obj = await loader()
        if obj is None:
            return None

        # Validate type (defensive)
        if not isinstance(obj, schema_type):
            raise TypeError(
                f"Loader returned {type(obj).__name__}, expected {schema_type.__name__}"
            )

        await self.set(obj, ttl=ttl)
        return await self.get_json(schema_type, obj_id) if return_json else obj


# Create a single, reusable instance for the rest of the application
cache_service = CacheService()
