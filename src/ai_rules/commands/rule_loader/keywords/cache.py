"""Content-hash caching utilities for keyword generation.

Cache writes are protected by filelock.FileLock wrapping the entire
load-modify-save cycle to prevent lost-update under concurrent writers.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from filelock import FileLock


def _content_hash(content: str) -> str:
    """Compute SHA-256 hash of file content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _load_cache(cache_path: Path) -> dict:
    """Load keyword cache from disk (no lock — read-only)."""
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache_path: Path, cache: dict) -> None:
    """Save keyword cache to disk under a file lock (prevents concurrent corruption)."""
    lock_path = cache_path.with_suffix(cache_path.suffix + ".lock")
    try:
        with FileLock(str(lock_path), timeout=10):
            cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    except OSError:
        pass


def _get_cached_keywords(cache: dict, file_key: str, content_hash: str) -> list[str] | None:
    """Get cached keywords if content hash matches."""
    entry = cache.get(file_key)
    if entry and entry.get("hash") == content_hash:
        return entry.get("keywords")
    return None


def _set_cached_keywords(cache: dict, file_key: str, content_hash: str, kws: list[str]) -> None:
    """Store keywords in cache with content hash."""
    cache[file_key] = {"hash": content_hash, "keywords": kws}


def update_cache_atomic(cache_path: Path, file_key: str, content_hash: str, kws: list[str]) -> None:
    """Atomically load-modify-save the cache under a file lock.

    Use this in concurrent (ThreadPoolExecutor) contexts to prevent lost-updates.
    The entire load-modify-save cycle is protected by filelock.FileLock.
    """
    lock_path = cache_path.with_suffix(cache_path.suffix + ".lock")
    try:
        with FileLock(str(lock_path), timeout=10):
            cache = _load_cache(cache_path)
            _set_cached_keywords(cache, file_key, content_hash, kws)
            cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    except OSError:
        pass
