#!/usr/bin/env python3
"""
validate_pages.py

Validates bundled scavenger hunt content for the iOS app.

What it validates:
- JSON Schema validation for each node file (nfc-hunt-page.schema.json)
- content-index.json existence + structural sanity
- file existence for nodes and optional media directories
- consistency checks:
  - tagID matches node filename
  - node numbers unique and contiguous (1..N)
  - required age tracks exist (kiddos, tweens, youths, adults)
  - pageIDs (if present in index) match the node's pages

Exit codes:
- 0: all validations passed
- 1: validation failures found
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import jsonschema
except ImportError:  # pragma: no cover
    print("ERROR: Missing dependency 'jsonschema'. Install with:")
    print("  pip install jsonschema")
    sys.exit(1)


REQUIRED_TRACK_LABELS = ["kiddos", "tweens", "youths", "adults"]


@dataclass
class ValidationError:
    where: str
    message: str


def load_json(path: Path) -> Dict[str, Any]:
    try:
        text: str = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")


def repo_root_from_this_file() -> Path:
    """
    Assumes this file lives at:
      <repo>/scripts/validate-content/validate_pages.py
    """
    return Path(__file__).resolve().parents[2]


def find_bundle_root(repo_root: Path, bundle_root_arg: Optional[str]) -> Path:
    if bundle_root_arg:
        return Path(bundle_root_arg).expanduser().resolve()
    return (repo_root / "ios-app" / "Resources" / "BundledContent").resolve()


def load_schema(bundle_root: Path, schema_arg: Optional[str]) -> Dict[str, Any]:
    if schema_arg:
        schema_path = Path(schema_arg).expanduser().resolve()
    else:
        schema_path = bundle_root / "schemas" / "nfc-hunt-page.schema.json"
    return load_json(schema_path)


def list_game_versions(
    bundle_root: Path, game: Optional[str], version: Optional[str]
) -> List[Tuple[str, str, Path]]:
    games_dir = bundle_root / "games"
    if not games_dir.exists():
        return []

    results: List[Tuple[str, str, Path]] = []
    for game_dir in sorted(games_dir.iterdir()):
        if not game_dir.is_dir():
            continue
        if game and game_dir.name != game:
            continue

        for ver_dir in sorted(game_dir.iterdir()):
            if not ver_dir.is_dir():
                continue
            if version and ver_dir.name != version:
                continue

            results.append((game_dir.name, ver_dir.name, ver_dir))
    return results


def validate_index(index: Dict[str, Any], where: str) -> List[ValidationError]:
    errs: List[ValidationError] = []

    # Minimal structural checks (do not over-police; schema for index can come later)
    if "game" not in index or not isinstance(index["game"], dict):
        errs.append(
            ValidationError(where, "Missing or invalid 'game' object in content index.")
        )
        return errs

    if (
        "nodes" not in index
        or not isinstance(index["nodes"], list)
        or len(index["nodes"]) == 0
    ):
        errs.append(
            ValidationError(where, "Missing or empty 'nodes' list in content index.")
        )
        return errs

    # Validate node entries
    seen_tags: set[str] = set()
    seen_nodes: set[int] = set()
    node_numbers: List[int] = []

    for i, entry in enumerate(index["nodes"]):
        entry_where = f"{where}::nodes[{i}]"
        if not isinstance(entry, dict):
            errs.append(ValidationError(entry_where, "Node entry must be an object."))
            continue

        node_num = entry.get("node")
        tag_id = entry.get("tagID")
        node_file = entry.get("nodeFile")

        if not isinstance(node_num, int) or node_num < 1:
            errs.append(
                ValidationError(
                    entry_where, "Missing/invalid 'node' (must be integer >= 1)."
                )
            )
        else:
            if node_num in seen_nodes:
                errs.append(
                    ValidationError(entry_where, f"Duplicate node number: {node_num}")
                )
            seen_nodes.add(node_num)
            node_numbers.append(node_num)

        if not isinstance(tag_id, str) or not tag_id:
            errs.append(
                ValidationError(
                    entry_where, "Missing/invalid 'tagID' (must be non-empty string)."
                )
            )
        else:
            if tag_id in seen_tags:
                errs.append(ValidationError(entry_where, f"Duplicate tagID: {tag_id}"))
            seen_tags.add(tag_id)

        if not isinstance(node_file, str) or not node_file:
            errs.append(
                ValidationError(
                    entry_where,
                    "Missing/invalid 'nodeFile' (must be non-empty string).",
                )
            )

    # Contiguous node check (1..N)
    if node_numbers:
        sorted_nodes = sorted(node_numbers)
        expected = list(range(1, len(sorted_nodes) + 1))
        if sorted_nodes != expected:
            errs.append(
                ValidationError(
                    where,
                    f"Node numbers must be contiguous 1..N. Found: {sorted_nodes} (expected {expected}).",
                )
            )

    # tagToNode map consistency (if present)
    tag_to_node = index.get("tagToNode")
    if tag_to_node is not None:
        if not isinstance(tag_to_node, dict):
            errs.append(
                ValidationError(where, "If present, 'tagToNode' must be an object/map.")
            )
        else:
            # verify all tags in nodes exist in map and map points back correctly
            for entry in index["nodes"]:
                if (
                    isinstance(entry, dict)
                    and isinstance(entry.get("tagID"), str)
                    and isinstance(entry.get("node"), int)
                ):
                    t = entry["tagID"]
                    n = entry["node"]
                    mapped = tag_to_node.get(t)
                    if mapped != n:
                        errs.append(
                            ValidationError(
                                where,
                                f"tagToNode mismatch for {t}: index nodes says {n}, tagToNode says {mapped}.",
                            )
                        )

    return errs


def extract_page_ids_from_node(node_obj: Dict[str, Any]) -> List[str]:
    ids: List[str] = []
    pages = node_obj.get("pages", [])
    if not isinstance(pages, list):
        return ids
    for p in pages:
        if not isinstance(p, dict):
            continue
        contents = p.get("contents")
        if not isinstance(contents, dict):
            continue
        pid = contents.get("pageID")
        if isinstance(pid, str) and pid:
            ids.append(pid)
    return ids


def extract_track_labels_from_node(node_obj: Dict[str, Any]) -> List[str]:
    labels: List[str] = []
    pages = node_obj.get("pages", [])
    if not isinstance(pages, list):
        return labels
    for p in pages:
        if not isinstance(p, dict):
            continue
        characteristics = p.get("characteristics")
        if not isinstance(characteristics, dict):
            continue
        label = characteristics.get("label")
        if isinstance(label, str) and label:
            labels.append(label.strip().lower())
    return labels


def validate_node_extras(
    node_obj: Dict[str, Any],
    node_path: Path,
    index_entry: Dict[str, Any],
    game_name: str,
    game_version: str,
) -> List[ValidationError]:
    errs: List[ValidationError] = []
    where = str(node_path)

    # tagRef.tagID matches filename + index
    filename_tag = node_path.stem.split(".")[0]  # TAG001 from TAG001.node.json
    tag_ref = node_obj.get("tagRef", {})
    if not isinstance(tag_ref, dict):
        errs.append(ValidationError(where, "tagRef must be an object."))
        return errs

    node_tag = tag_ref.get("tagID")
    if node_tag != filename_tag:
        errs.append(
            ValidationError(
                where,
                f"tagRef.tagID '{node_tag}' does not match filename tag '{filename_tag}'.",
            )
        )

    idx_tag = index_entry.get("tagID")
    if idx_tag != filename_tag:
        errs.append(
            ValidationError(
                where,
                f"Index tagID '{idx_tag}' does not match filename tag '{filename_tag}'.",
            )
        )

    # node number matches index
    idx_node_num = index_entry.get("node")
    node_num = node_obj.get("node")
    if idx_node_num != node_num:
        errs.append(
            ValidationError(
                where,
                f"Node number mismatch: index says {idx_node_num}, node file says {node_num}.",
            )
        )

    # gameName/version matches current folder
    game_obj = node_obj.get("game", {})
    if isinstance(game_obj, dict):
        if game_obj.get("gameName") != game_name:
            errs.append(
                ValidationError(
                    where,
                    f"game.gameName mismatch: expected '{game_name}', found '{game_obj.get('gameName')}'.",
                )
            )
        if game_obj.get("gameVersion") != game_version:
            errs.append(
                ValidationError(
                    where,
                    f"game.gameVersion mismatch: expected '{game_version}', found '{game_obj.get('gameVersion')}'.",
                )
            )

    # required tracks exist
    labels = extract_track_labels_from_node(node_obj)
    missing = [t for t in REQUIRED_TRACK_LABELS if t not in labels]
    if missing:
        errs.append(
            ValidationError(
                where,
                f"Missing required age track pages: {missing}. Found labels: {sorted(set(labels))}.",
            )
        )

    # pageIDs match (if index provides them)
    index_page_ids = index_entry.get("pageIDs")
    if isinstance(index_page_ids, list) and index_page_ids:
        node_page_ids = extract_page_ids_from_node(node_obj)
        if sorted(index_page_ids) != sorted(node_page_ids):
            errs.append(
                ValidationError(
                    where,
                    f"pageIDs mismatch. Index: {index_page_ids} | Node: {node_page_ids}",
                )
            )

    return errs


def validate_bundle(
    bundle_root: Path,
    schema: Dict[str, Any],
    game_name: str,
    game_version: str,
    version_root: Path,
) -> List[ValidationError]:
    errs: List[ValidationError] = []

    index_path = version_root / "indexes" / "content-index.json"
    if not index_path.exists():
        errs.append(ValidationError(str(index_path), "Missing content-index.json"))
        return errs

    try:
        index_obj = load_json(index_path)
    except Exception as e:
        errs.append(ValidationError(str(index_path), str(e)))
        return errs

    errs.extend(validate_index(index_obj, str(index_path)))

    # If index structure is badly broken, stop early
    if any("Missing or empty 'nodes'" in e.message for e in errs):
        return errs

    validator = jsonschema.Draft202012Validator(schema)

    nodes_list = index_obj.get("nodes", [])
    if not isinstance(nodes_list, list):
        return errs

    for i, entry in enumerate(nodes_list):
        if not isinstance(entry, dict):
            continue

        node_file_rel = entry.get("nodeFile")
        if not isinstance(node_file_rel, str) or not node_file_rel:
            continue

        node_path = (version_root / node_file_rel).resolve()
        if not node_path.exists():
            errs.append(
                ValidationError(
                    str(node_path), f"Node file missing (from index): {node_file_rel}"
                )
            )
            continue

        # Validate JSON parses
        try:
            node_obj = load_json(node_path)
        except Exception as e:
            errs.append(ValidationError(str(node_path), str(e)))
            continue

        # JSON Schema validation
        schema_errors = sorted(
            validator.iter_errors(node_obj), key=lambda e: list(e.path)
        )
        for se in schema_errors:
            path_str = ".".join([str(p) for p in se.path]) if se.path else "<root>"
            errs.append(
                ValidationError(
                    str(node_path), f"Schema error at {path_str}: {se.message}"
                )
            )

        # Extra validations
        errs.extend(
            validate_node_extras(node_obj, node_path, entry, game_name, game_version)
        )

        # Media dir existence (if present)
        media_dir_rel = entry.get("mediaDir")
        if isinstance(media_dir_rel, str) and media_dir_rel.strip():
            media_dir_path = (version_root / media_dir_rel).resolve()
            if not media_dir_path.exists():
                errs.append(
                    ValidationError(
                        str(media_dir_path),
                        f"mediaDir missing (from index): {media_dir_rel}",
                    )
                )

    return errs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate bundled scavenger hunt content."
    )
    parser.add_argument(
        "--bundle-root",
        help="Path to BundledContent root (defaults to repo ios-app/Resources/BundledContent).",
    )
    parser.add_argument(
        "--schema",
        help="Path to node JSON schema (defaults to BundledContent/schemas/nfc-hunt-page.schema.json).",
    )
    parser.add_argument(
        "--game", help="Validate only a specific gameName (folder under games/)."
    )
    parser.add_argument(
        "--version",
        help="Validate only a specific gameVersion (folder under the game).",
    )
    args = parser.parse_args()

    repo_root = repo_root_from_this_file()
    bundle_root = find_bundle_root(repo_root, args.bundle_root)

    if not bundle_root.exists():
        print(f"ERROR: BundledContent root not found: {bundle_root}")
        return 1

    # Load schema
    try:
        schema = load_schema(bundle_root, args.schema)
    except Exception as e:
        print(f"ERROR: Unable to load schema: {e}")
        return 1

    targets = list_game_versions(bundle_root, args.game, args.version)
    if not targets:
        print("ERROR: No game/version folders found to validate.")
        print(f"Checked under: {bundle_root / 'games'}")
        return 1

    all_errs: List[ValidationError] = []

    for game_name, game_version, version_root in targets:
        print(f"\n== Validating bundle: {game_name}/{game_version} ==")
        errs = validate_bundle(
            bundle_root, schema, game_name, game_version, version_root
        )
        if errs:
            print(f"❌ Found {len(errs)} issue(s) in {game_name}/{game_version}")
        else:
            print(f"✅ OK: {game_name}/{game_version}")
        all_errs.extend(errs)

    if all_errs:
        print("\n====================")
        print(f"VALIDATION FAILED: {len(all_errs)} total issue(s)\n")
        for e in all_errs:
            print(f"- {e.where}\n  -> {e.message}")
        print("\nFix the content or index, then re-run validation.")
        return 1

    print("\n====================")
    print("VALIDATION PASSED: All bundles OK ✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
