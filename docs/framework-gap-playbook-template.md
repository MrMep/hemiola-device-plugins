# Framework Gap Playbook Template

Use this template when a plugin requirement cannot be implemented with the current plugin schema/runtime.

Audience:
- master project maintainers
- plugin runtime and schema maintainers

Goal:
- request a focused framework enhancement before extending plugin JSON drafts

## 1. Gap summary

- Plugin/device context:
- Missing capability name:
- Why it is needed:
- User-visible impact if missing:

## 2. Evidence and reproduction

- Source documents (MIDI chart/spec references):
- Packet captures or logs:
- Minimal scenario that fails with current framework:

## 3. Current framework limitation

- Current supported fields/commands involved:
- Exact point where schema/runtime blocks implementation:
- Why existing constructs cannot be reused safely:

## 4. Proposed schema changes

- New field(s) or type(s):
- JSON shape examples:
- Validation constraints:
- Migration/compatibility notes:

Example JSON snippet:

```json
{
  "TODO": "replace with minimal proposed shape"
}
```

## 5. Proposed runtime changes

- Parser/model changes:
- Mapper/engine behavior changes:
- Ordering/precedence rules:
- Error handling behavior:
- No-op/fallback behavior when unsupported data is present:

## 6. Backward compatibility

- Existing plugins affected:
- Behavior for plugins not using the new feature:
- Feature-flag or versioning needs:

## 7. Security and robustness checks

- Input validation concerns:
- Bounds/range checks:
- Malformed payload handling:
- Performance considerations:

## 8. Test plan

- Unit tests to add:
- Schema validation tests:
- Integration tests:
- Regression tests:
- Manual hardware validation checklist:

## 9. Acceptance criteria

- Criteria 1:
- Criteria 2:
- Criteria 3:

## 10. Rollout notes

- Documentation updates required:
- Release notes entry:
- Any follow-up plugin updates expected:

## 11. Final handoff block

- Proposed owner:
- Priority:
- Dependencies:
- Links to related issues/PRs:
