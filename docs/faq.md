# FAQ

## Can I build a plugin from only the MIDI implementation chart?

Usually yes for a first draft, especially for CC-only and NRPN-heavy devices.

Usually no for the final production plugin if the device has proprietary SysEx, checksums, patch catalogs, packed bitfields, or custom memory editors.

## When should I choose `mixed` instead of `cc`?

Choose `mixed` as soon as one meaningful parameter uses something other than plain CC, or when you need explicit `sendCommand` control.

## When should I choose `sysex` instead of `mixed`?

Choose `sysex` when the device behavior is fundamentally bank-based:

- request a dump
- edit bytes in the dump
- write the whole dump back

Choose `mixed` when the device behaves more like independent commands per parameter.

## Are `byteIndex` values relative to payload or full frame?

They are absolute indexes in the full SysEx frame, including the initial `F0`.

## Do I need top-level `presets`?

No. If you omit them, the runtime creates one `Default` preset from parameter defaults.

## What is the difference between top-level `presets` and `preset_picker` controls?

Top-level `presets` are device-wide built-in presets.

`preset_picker` is a UI control that writes a fixed list of values to a specific set of parameters.

## Why does my `sysex` plugin load but not write correctly?

Common causes:

- wrong `writePrefix`
- wrong `writeLength`
- wrong checksum rule
- wrong assumption about which incoming frame is writable
- wrong `byteIndex` offsets

## Why does my parameter display the wrong logical value?

Check these fields in order:

1. `transform`
2. `valueOffset`
3. `valueInvert`
4. `receiveValueMap`
5. `sendValueMap`

## Should I expose undocumented bytes as controls?

No, not in a release-facing plugin.

It is acceptable to keep a temporary hidden debug tab while reverse engineering, but do not confuse raw unknown bytes with meaningful user controls.

## How many trigger strings should I add?

Only realistic ones. A few real-world name variants are better than many speculative aliases.

## What if the device exposes per-channel settings?

Use `multi_sysex` if the device really expects a fan-out write across channels or slots and the packet structure fits the supported runtime builder.

If not, create a framework gap analysis and maintainer instructions so the JSON runtime can be extended safely.

## When should I use `pressed_keys`?

Only when you know the live key state source.

Good inputs:

- note-on/note-off echo
- documented bitfield bytes
- captured SysEx packets with verified bit mapping

## When should I use `custom_fingering_manager`?

Only when you have already decoded:

- slot count behavior
- slot payload structure
- write format
- checksum behavior
- any disabled-slot semantics

## Can I include help text in the plugin?

Yes. Use the top-level `help` array.

## I can edit only `workdir/` in public repo mode. How do I propose schema/docs/tool changes?

Use a two-file handoff:

1. gap analysis in `workdir/<plugin slug>/gap-analysis/`
2. maintainer instructions in `workdir/<plugin slug>/instructions/`

Then hand off those files to maintainers for updates in immutable folders.

See `public-repo-contribution-workflow.md` for the full process.

## What if the official editor sends packets I do not understand?

That is expected.

Start by matching only the packets you truly need:

- read current state
- write important parameters
- select programs

Ignore low-value traffic until the core editor works.

## How do I know whether a device fits the current JSON plugin runtime?

Use a JSON plugin when the protocol is declarative and stable enough to describe with the current schema.

Create a framework gap analysis when the device needs:

- stateful protocol negotiation
- streaming protocols outside the current abstractions
- non-trivial parsing logic not expressible as current schema fields
- custom widgets with bespoke behavior beyond existing advanced controls

Then provide maintainer instructions as described in `public-repo-contribution-workflow.md`.