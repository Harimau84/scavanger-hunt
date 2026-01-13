#!/usr/bin/env python3
"""
generate_content_index.py

Generates content-index.json for a given game/version by scanning the bundled nodes directory.

Default bundle root:
  ios-app/Resources/BundledContent

Default output:
  games/<GameName>/<GameVersion>/indexes/content-index.json

What it does:
- scans nodes/*.json
- loads each node JSON
- extracts:
  - node number
  - tagRef.tagID
  - pageIDs
- infers mediaDir from pageIDs (e.g., "P001-1" -> "media/P001") if that folder exists
- writes a deterministic index file
- (optional) checks folder/game/version consistency

Usage examples:
  python scripts/build/generate_content_index.py --game FamilyHunt2026 --version 260113.01
  python scripts/build/generate_content_index.py --game FamilyHunt2026 --version 260113.01 --bundle-root ios-app/Resources/BundledContent
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


INDEX_FORMAT_VERSION = "1.0"


def load_json(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def repo_root_from_this_file() -> Path:
    # <repo>/scripts/build/generate_content_index.py -> parents[2] == <repo>
    return Path(__file__).resolve().parents[2]


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def extract_page_ids(node_obj: Dict[str, Any]) -> List[str]:
    ids: List[str] = []
    pages = node_obj.get("pages", [])
    if not isinstance(pages, list):
        return ids
    for p in pages:
        if not isinstance(p, dict):
            continue
        contents = p.get("contents", {})
        if not isinstance(contents, dict):
            continue
        pid = contents.get("pageID")
        if isinstance(pid, str) and pid:
            ids.append(pid)
    return ids


def infer_media_dir(version_root: Path, page_ids: List[str]) -> Optional[str]:
    """
    If the first pageID looks like 'P001-1', infer media/P001 if it exists.
    """
    if not page_ids:
        return None

    first = page_ids[0].strip()
    # Expecting "P###-X" or "P###"
    prefix = first.split("-")[0]
    if not prefix.startswith("P"):
        return None

    candidate_rel = f"media/{prefix}"
    candidate_abs = version_root / candidate_rel
    if candidate_abs.exists() and candidate_abs.is_dir():
        return candidate_rel
    return None


def find_node_files(version_root: Path) -> List[Path]:
    nodes_dir = version_root / "nodes"
    if not nodes_dir.exists():
        return []
    return sorted([p for p in nodes_dir.glob("*.json") if p.is_file()])


def parse_node_file(node_path: Path) -> Tuple[int, str, List[str]]:
    node_obj = load_json(node_path)

    node_num = node_obj.get("node")
    if not isinstance(node_num, int) or node_num < 1:
        raise ValueError(f"Invalid or missing 'node' in {node_path.name}")

    tag_ref = node_obj.get("tagRef", {})
    if not isinstance(tag_ref, dict):
        raise ValueError(f"Invalid or missing 'tagRef' in {node_path.name}")

    tag_id = tag_ref.get("tagID")
    if not isinstance(tag_id, str) or not tag_id:
        raise ValueError(f"Invalid or missing tagRef.tagID in {node_path.name}")

    page_ids = extract_page_ids(node_obj)

    return node_num, tag_id, page_ids


def build_index(
    game_name: str,
    game_version: str,
    version_root: Path,
    generated_by: str,
    locale: str,
) -> Dict[str, Any]:
    node_files = find_node_files(version_root)
    if not node_files:
        raise FileNotFoundError(f"No node files found under: {version_root / 'nodes'}")

    entries: List[Dict[str, Any]] = []

    for node_path in node_files:
        node_num, tag_id, page_ids = parse_node_file(node_path)

        node_file_rel = f"nodes/{node_path.name}"
        media_dir = infer_media_dir(version_root, page_ids)

        entry: Dict[str, Any] = {
            "node": node_num,
            "tagID": tag_id,
            "nodeFile": node_file_rel,
        }

        if page_ids:
            entry["pageIDs"] = page_ids

        if media_dir:
            entry["mediaDir"] = media_dir

        entries.append(entry)

    # Deterministic ordering: by node number, then tagID
    entries.sort(key=lambda e: (int(e["node"]), str(e["tagID"])))

    tag_to_node = {e["tagID"]: e["node"] for e in entries}

    index_obj: Dict[str, Any] = {
        "indexFormatVersion": INDEX_FORMAT_VERSION,
        "game": {
            "gameName": game_name,
            "gameVersion": game_version,
        },
        "generated": {
            "generatedAt": utc_now_iso(),
            "generatedBy": generated_by,
            "sourceRoot": "data",
        },
        "defaults": {
            "locale": locale,
        },
        "nodes": entries,
        "tagToNode": tag_to_node,
    }

    return index_obj


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate content-index.json from bundled nodes."
    )
    parser.add_argument(
        "--bundle-root",
        help="BundledContent root (default: ios-app/Resources/BundledContent)",
    )
    parser.add_argument(
        "--game", required=True, help="Game name folder (e.g., FamilyHunt2026)"
    )
    parser.add_argument(
        "--version", required=True, help="Game version folder (e.g., 260113.01)"
    )
    parser.add_argument(
        "--generated-by",
        default="scripts/build/generate_content_index.py",
        help="Identifier for generatedBy field",
    )
    parser.add_argument("--locale", default="en-US", help="Default locale value")
    args = parser.parse_args()

    repo_root = repo_root_from_this_file()
    bundle_root = (
        Path(args.bundle_root).expanduser().resolve()
        if args.bundle_root
        else (repo_root / "ios-app" / "Resources" / "BundledContent").resolve()
    )

    version_root = bundle_root / "games" / args.game / args.version
    if not version_root.exists():
        raise FileNotFoundError(f"Game/version folder not found: {version_root}")

    index_path = version_root / "indexes" / "content-index.json"

    index_obj = build_index(
        game_name=args.game,
        game_version=args.version,
        version_root=version_root,
        generated_by=args.generated_by,
        locale=args.locale,
    )

    write_json(index_path, index_obj)
    print(f"✅ Wrote: {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
