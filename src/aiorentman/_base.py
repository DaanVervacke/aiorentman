"""Link and page types shared by every result model."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RentmanLink:
    """A reference to another resource, given as its API path.

    Linked fields hold a path string such as ``/equipment/12`` unless the
    request expanded them, in which case the parser returns the full typed
    model instead of this link. An expanded object without a usable id
    parses to None.
    """

    path: str

    @property
    def id(self) -> int | None:
        """The numeric id at the end of the path, or None when absent."""
        tail = self.path.rsplit("/", 1)[-1]
        try:
            return int(tail)
        except ValueError:
            return None


@dataclass(frozen=True, slots=True)
class RentmanPage[ModelT]:
    """One page of a collection: the parsed items and the paging metadata.

    The parser drops items without a usable id, and logs each one at debug
    level on the ``aiorentman.parsers`` logger. ``item_count`` is the count
    the API reported, so it can be higher than ``len(items)``.
    """

    items: tuple[ModelT, ...]
    item_count: int
    limit: int
    offset: int
    next_page_url: str | None
