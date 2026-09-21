"""Resume support: a chapter-link index and a per-volume checkpoint.

The crawler used to discover each chapter's page links while fetching content, in a loop that
carried state from one chapter to the next, and it kept the whole book in memory until the last
page had been read. An interrupted run therefore lost everything, and no volume could be skipped
safely. This module stores the resolved links once, up front, and each volume as it finishes.
"""
import json
import os
import pickle
from typing import Any, Optional

INDEX_VERSION = 2


def index_payload(catalog_list: list, indexed: dict) -> dict:
    """Serialise the resolved links. Only volumes listed in `indexed` are complete; the rest are
    written as they stand so an interrupted index pass can continue where it stopped.

    `indexed` maps a volume id to the link the pagination walk ended on, which is what the next
    volume has to start from when a chapter's own catalog link is broken.
    """
    return {
        'version': INDEX_VERSION,
        'volumes': [
            {
                'vid': volume.vid,
                'indexed': volume.vid in indexed,
                'url_next_after': indexed.get(volume.vid, ''),
                'chapters': [
                    {'url': chapter.chapter_url, 'pages': list(chapter.other_paginated_chapter_urls)}
                    for chapter in volume.chapters
                ],
            }
            for volume in catalog_list
        ],
    }


def apply_index(catalog_list: list, payload: Optional[dict]) -> dict:
    """Put the saved links back into a freshly parsed catalog.

    Returns a map of the volume ids that were restored to the link the walk ended on. An empty
    map means nothing was reused and the catalog was left untouched, which is what happens when
    the book has gained a volume or a chapter since the index was written.
    """
    if not isinstance(payload, dict) or payload.get('version') != INDEX_VERSION:
        return {}
    volumes = payload.get('volumes')
    if not isinstance(volumes, list) or len(volumes) != len(catalog_list):
        return {}
    for saved, volume in zip(volumes, catalog_list):
        chapters = saved.get('chapters')
        if saved.get('vid') != volume.vid or not isinstance(chapters, list):
            return {}
        if len(chapters) != len(volume.chapters):
            return {}
        if saved.get('indexed') and any(not chapter.get('url') for chapter in chapters):
            return {}
    restored = {}
    for saved, volume in zip(volumes, catalog_list):
        if not saved.get('indexed'):
            continue
        for saved_chapter, chapter in zip(saved['chapters'], volume.chapters):
            chapter.chapter_url = saved_chapter['url']
            chapter.other_paginated_chapter_urls = list(saved_chapter.get('pages') or [])
        restored[volume.vid] = saved.get('url_next_after') or ''
    return restored


def _write_atomically(path: str, data: bytes) -> None:
    """A checkpoint half-written by an interrupted run must not replace a good one."""
    temporary = f'{path}.tmp'
    with open(temporary, 'wb') as file:
        file.write(data)
    os.replace(temporary, path)


class ResumeStore:
    def __init__(self, folder: str, run_identifier: str) -> None:
        self.folder = folder
        self.index_path = os.path.join(folder, f'{run_identifier}.index.json')
        self.partial_path = os.path.join(folder, f'{run_identifier}.partial.pickle')

    def save_index(self, catalog_list: list, indexed: dict) -> None:
        os.makedirs(self.folder, exist_ok=True)
        body = json.dumps(index_payload(catalog_list, indexed), ensure_ascii=False)
        _write_atomically(self.index_path, body.encode('utf-8'))

    def load_index(self) -> Optional[dict]:
        try:
            with open(self.index_path, encoding='utf-8') as file:
                return json.load(file)
        except (OSError, ValueError):
            return None

    def save_partial(self, novel: Any) -> None:
        os.makedirs(self.folder, exist_ok=True)
        _write_atomically(self.partial_path, pickle.dumps(novel))

    def load_partial(self) -> Optional[Any]:
        try:
            with open(self.partial_path, 'rb') as file:
                return pickle.load(file)
        except (OSError, EOFError, AttributeError, pickle.UnpicklingError):
            return None

    def clear(self) -> None:
        for path in (self.index_path, self.partial_path):
            try:
                os.remove(path)
            except OSError:
                pass
