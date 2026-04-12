#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    schema_path = repo_root / "schema" / "hemiola-plugin.schema.json"
    devices_dir = repo_root / "devices"
    work_dir = repo_root / "workdir"
    templates_dir = repo_root / "templates"

    try:
        import jsonschema
    except ImportError:
        print("Missing dependency: jsonschema", file=sys.stderr)
        print("Install with: python3 -m pip install jsonschema", file=sys.stderr)
        return 2

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    candidate_files = sorted(devices_dir.glob("*.json")) + sorted(templates_dir.glob("*.json")) + sorted(work_dir.glob("*/*.json"))
    if not candidate_files:
        print("No plugin JSON files found.")
        return 0

    failures = []
    warnings = []
    for file_path in candidate_files:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append((file_path, [f"Invalid JSON: {exc}"]))
            continue

        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            rendered = []
            for error in errors:
                path = ".".join(str(part) for part in error.absolute_path)
                rendered.append(f"{path or '<root>'}: {error.message}")
            failures.append((file_path, rendered))
            continue

        # Semantic warnings (non-fatal): send_param references.
        file_warnings = []
        parameters = data.get("parameters") if isinstance(data, dict) else None
        parameter_map = {}
        if isinstance(parameters, list):
            for param in parameters:
                if isinstance(param, dict):
                    pid = param.get("id")
                    if isinstance(pid, str) and pid:
                        parameter_map[pid] = param

        ui = data.get("ui") if isinstance(data, dict) else None
        actions = ui.get("actions") if isinstance(ui, dict) else None
        if isinstance(actions, list):
            for action_idx, action in enumerate(actions):
                if not isinstance(action, dict) or action.get("action") != "sequence":
                    continue
                steps = action.get("steps")
                if not isinstance(steps, list):
                    continue
                for step_idx, step in enumerate(steps):
                    if not isinstance(step, dict) or step.get("type") != "send_param":
                        continue
                    param_id = step.get("param")
                    if not isinstance(param_id, str) or not param_id:
                        continue
                    param_def = parameter_map.get(param_id)
                    if param_def is None:
                        file_warnings.append(
                            f"ui.actions[{action_idx}].steps[{step_idx}]: send_param references unknown parameter '{param_id}'"
                        )
                        continue
                    if not isinstance(param_def, dict) or "sendCommand" not in param_def:
                        file_warnings.append(
                            f"ui.actions[{action_idx}].steps[{step_idx}]: send_param references '{param_id}' with no sendCommand (step is a no-op)"
                        )

        if file_warnings:
            warnings.append((file_path, file_warnings))

    if warnings:
        for file_path, messages in warnings:
            print(f"WARN {file_path.relative_to(repo_root)}")
            for message in messages:
                print(f"  - {message}")

    if failures:
        for file_path, errors in failures:
            print(f"FAIL {file_path.relative_to(repo_root)}")
            for message in errors:
                print(f"  - {message}")
        return 1

    print(f"Validated {len(candidate_files)} plugin file(s) against {schema_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())