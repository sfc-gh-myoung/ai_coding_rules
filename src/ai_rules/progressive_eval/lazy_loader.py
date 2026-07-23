"""Lazy rule loader for progressive loading architecture.

Intercepts model tool calls and loads full rule content just-in-time
when a trigger matches. Triggers fire on:
1. File extension match from tool call input (primary)
2. Keyword match against user request (secondary)

Includes a fail-safe: if no trigger fires within 2 turns, loads all
remaining unloaded manifest rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from ai_rules.progressive_eval.manifest_generator import ManifestEntry, ProgressiveManifest


@dataclass
class LoadEvent:
    """Record of a rule being lazily loaded."""

    rule_path: str
    trigger_type: str  # "ext_match", "kw_match", "fail_safe"
    trigger_detail: str
    turn_number: int


@dataclass
class LazyLoader:
    """Stateful lazy loader that tracks which rules have been loaded and when.

    Usage:
        loader = LazyLoader(manifest, rules_dir)
        # On each tool call:
        newly_loaded = loader.on_tool_call(tool_name, tool_input, turn)
        # On turn end without trigger:
        loader.on_turn_end(turn)
        # Check fail-safe:
        if loader.should_fail_safe():
            loader.fail_safe_load(turn)
    """

    manifest: ProgressiveManifest
    rules_dir: Path
    loaded_rules: dict[str, str] = field(default_factory=dict)
    load_events: list[LoadEvent] = field(default_factory=list)
    turns_without_load: int = 0
    _fail_safe_fired: bool = False

    @property
    def loaded_paths(self) -> set[str]:
        return set(self.loaded_rules.keys())

    @property
    def unloaded_entries(self) -> list[ManifestEntry]:
        return [e for e in self.manifest.entries if e.rule_path not in self.loaded_rules]

    def on_tool_call(self, tool_name: str, tool_input: dict, turn: int) -> list[str]:
        """Process a tool call and load matching rules. Returns list of newly loaded rule paths."""
        newly_loaded = []

        # Extract file path from tool input (handles Read, Edit, Write, Bash)
        file_path = self._extract_file_path(tool_name, tool_input)
        if file_path:
            ext = Path(file_path).suffix.lower()
            if ext:
                for entry in self.unloaded_entries:
                    if ext in entry.triggers_ext or ext.lstrip(".") in (
                        e.lstrip(".") for e in entry.triggers_ext
                    ):
                        content = self._load_rule(entry.rule_path)
                        if content:
                            newly_loaded.append(entry.rule_path)
                            self.load_events.append(
                                LoadEvent(
                                    rule_path=entry.rule_path,
                                    trigger_type="ext_match",
                                    trigger_detail=f"{tool_name}({file_path}) → ext={ext}",
                                    turn_number=turn,
                                )
                            )

        if newly_loaded:
            self.turns_without_load = 0
        return newly_loaded

    def on_turn_end(self, turn: int) -> None:
        """Called at end of each turn. Tracks turns without loading."""
        if not any(e.turn_number == turn for e in self.load_events):
            self.turns_without_load += 1
        else:
            self.turns_without_load = 0

    def should_fail_safe(self) -> bool:
        """Return True if fail-safe should trigger (2 turns without any load)."""
        return (
            self.turns_without_load >= 2
            and not self._fail_safe_fired
            and bool(self.unloaded_entries)
        )

    def fail_safe_load(self, turn: int) -> list[str]:
        """Load all remaining unloaded rules (fail-safe). Returns loaded paths."""
        self._fail_safe_fired = True
        newly_loaded = []
        for entry in list(self.unloaded_entries):
            content = self._load_rule(entry.rule_path)
            if content:
                newly_loaded.append(entry.rule_path)
                self.load_events.append(
                    LoadEvent(
                        rule_path=entry.rule_path,
                        trigger_type="fail_safe",
                        trigger_detail=f"2 turns without trigger, loading remaining {len(self.unloaded_entries)} rules",
                        turn_number=turn,
                    )
                )
        return newly_loaded

    def get_loaded_content(self, rule_path: str) -> str | None:
        """Get the full content of a loaded rule."""
        return self.loaded_rules.get(rule_path)

    def get_all_loaded_content(self) -> str:
        """Get concatenated content of all loaded rules."""
        return "\n\n".join(self.loaded_rules.values())

    def _load_rule(self, rule_path: str) -> str | None:
        """Read a rule file and cache it."""
        if rule_path in self.loaded_rules:
            return self.loaded_rules[rule_path]
        full_path = self.rules_dir / rule_path.removeprefix("rules/")
        if not full_path.exists():
            return None
        content = full_path.read_text(encoding="utf-8")
        self.loaded_rules[rule_path] = content
        return content

    def _extract_file_path(self, tool_name: str, tool_input: dict) -> str | None:
        """Extract the file path from a tool call's input."""
        # Direct file path tools
        if tool_name in ("Read", "Edit", "Write"):
            return tool_input.get("file_path") or tool_input.get("path")
        # Bash: try to extract file references from command
        if tool_name == "Bash":
            cmd = tool_input.get("command", "")
            # Match common file patterns in bash commands
            file_match = re.search(r"[\w./\-]+\.\w{1,5}", cmd)
            if file_match:
                return file_match.group()
        # Glob: pattern may reveal extension
        if tool_name == "Glob":
            pattern = tool_input.get("pattern", "")
            ext_match = re.search(r"\*(\.\w+)", pattern)
            if ext_match:
                return f"file{ext_match.group(1)}"
        return None
