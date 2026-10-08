"""A bounded, injectable paginated JSON API reader using only the standard library."""
from __future__ import annotations

import json
import random
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

MAX_RESPONSE_BYTES = 16 * 1024 * 1024


@dataclass(frozen=True)
class Page:
    items: tuple[dict[str, Any], ...]
    next_cursor: str | None


class RetryableRequestError(Exception):
    def __init__(self, message: str, retry_after_seconds: float | None = None) -> None:
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class ApiResponseError(ValueError):
    """The response is successful HTTP but violates the documented page contract."""


def _read_page(
    endpoint: str,
    cursor: str | None,
    bearer_token: str | None,
    timeout_seconds: float,
) -> Page:
    parsed = urlsplit(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("endpoint must be an absolute HTTP(S) URL")
    query = parsed.query
    if cursor is not None:
        query = "&".join(part for part in (query, urlencode({"cursor": cursor})) if part)
    url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))
    headers = {"Accept": "application/json"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    try:
        with urlopen(Request(url, headers=headers), timeout=timeout_seconds) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                raise ApiResponseError("page response exceeds the 16 MiB limit")
            payload = json.loads(body.decode("utf-8"))
    except HTTPError as error:
        if error.code == 429 or 500 <= error.code <= 599:
            retry_after: float | None = None
            try:
                retry_after = max(0.0, float(error.headers.get("Retry-After", "")))
            except (TypeError, ValueError):
                pass
            raise RetryableRequestError(
                f"transient HTTP status {error.code}", retry_after
            ) from error
        raise RuntimeError(f"non-retryable HTTP status {error.code}") from error
    except (URLError, TimeoutError) as error:
        raise RetryableRequestError("network request failed") from error

    if not isinstance(payload, dict):
        raise ApiResponseError("page response must be a JSON object")
    items = payload.get("items")
    next_cursor = payload.get("next_cursor")
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        raise ApiResponseError("'items' must be a list of JSON objects")
    if next_cursor is not None and not isinstance(next_cursor, str):
        raise ApiResponseError("'next_cursor' must be a string or null")
    return Page(tuple(items), next_cursor)


PageReader = Callable[[str, str | None, str | None, float], Page]


def iter_api_pages(
    endpoint: str,
    *,
    bearer_token: str | None = None,
    timeout_seconds: float = 10.0,
    max_retries: int = 3,
    max_backoff_seconds: float = 60.0,
    max_pages: int = 10_000,
    read_page: PageReader = _read_page,
    sleep: Callable[[float], None] = time.sleep,
    random_value: Callable[[], float] = random.random,
) -> Iterator[Page]:
    """Yield API pages, retrying transient failures and rejecting cursor cycles.

    ``max_retries`` counts retries after the initial request. The caller is
    responsible for durably saving a page before persisting its next cursor.
    """
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if max_retries < 0:
        raise ValueError("max_retries cannot be negative")
    if max_backoff_seconds < 0:
        raise ValueError("max_backoff_seconds cannot be negative")
    if max_pages <= 0:
        raise ValueError("max_pages must be positive")

    cursor: str | None = None
    seen_cursors: set[str] = set()
    pages_read = 0
    while True:
        if pages_read >= max_pages:
            raise ApiResponseError("API pagination exceeded max_pages")
        if cursor is not None:
            if cursor in seen_cursors:
                raise ApiResponseError("API returned a repeated pagination cursor")
            seen_cursors.add(cursor)

        page = _read_with_retries(
            endpoint,
            cursor,
            bearer_token,
            timeout_seconds,
            max_retries,
            max_backoff_seconds,
            read_page,
            sleep,
            random_value,
        )
        pages_read += 1
        yield page
        cursor = page.next_cursor
        if cursor is None:
            return


def _read_with_retries(
    endpoint: str,
    cursor: str | None,
    bearer_token: str | None,
    timeout_seconds: float,
    max_retries: int,
    max_backoff_seconds: float,
    read_page: PageReader,
    sleep: Callable[[float], None],
    random_value: Callable[[], float],
) -> Page:
    for attempt in range(max_retries + 1):
        try:
            return read_page(endpoint, cursor, bearer_token, timeout_seconds)
        except RetryableRequestError as error:
            if attempt == max_retries:
                raise
            if (
                error.retry_after_seconds is not None
                and error.retry_after_seconds > max_backoff_seconds
            ):
                raise
            exponential = min(max_backoff_seconds, 2**attempt)
            jittered = min(max_backoff_seconds, exponential * (0.5 + random_value()))
            delay = max(error.retry_after_seconds or 0.0, jittered)
            sleep(delay)
    raise RuntimeError("retry loop exhausted without a response")
