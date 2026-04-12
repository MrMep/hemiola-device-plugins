# Plugin JSON Reference

This file documents the JSON format supported by the current Hemiola runtime.

It is a behavioral reference, not just a shape reference.

## Top-level object

```json
{
  "slug": "mydevice",
  "name": "My Device",
  "manufacturer": "My Manufacturer",
  "version": "1.0.0",
  "enabled": true,
  "triggers": ["My Device"],
  "requiresLandscape": false,
  "protocol": { ... },
  "parameters": [ ... ],
  "presets": [ ... ],
  "ui": { ... },
  "help": [ ... ]
}
```

## Top-level fields

### `slug: string`

Required. Stable plugin identifier.

### `name: string`

Required. User-facing device name.

### `manufacturer: string`

Required. Manufacturer name used by runtime disclaimer UI.

### `version: string`

Optional. Defaults to `1.0.0`.

### `enabled: boolean`

Optional. Defaults to `true`.

If `false`, the loader parses the file but skips registration.

### `triggers: string[]`

Required. Substrings matched against MIDI device names.

### `requiresLandscape: boolean`

Optional. Defaults to `false`.

### `protocol: object`

Required. See protocol reference below.

### `parameters: object[]`

Required. List of editable or observable parameters.

### `presets: object[]`

Optional. Built-in presets. If omitted, a single `Default` preset is synthesized from parameter defaults.

### `ui: object`

Required. Complete UI definition.

### `help: object[]`

Optional. Help sections displayed inside the app help UI.

## Protocol object

```json
"protocol": {
  "type": "mixed",
  "channel": 0,
  "autoWrite": false,
  "onConnect": [ ... ],
  "responses": [ ... ]
}
```

### `type`

Required. One of:

- `cc`
- `sysex`
- `mixed`

### `channel`

Optional. Default MIDI channel, zero-based.

### `autoWrite`

Optional. Defaults to `false`.

Meaningful mainly for `sysex` plugins.

### `onConnect`

Optional list of raw MIDI command objects:

```json
{ "bytes": "F0 47 7F 6D 40 00 00 F7" }
```

### `responses`

Optional list of SysEx response descriptors.

## Response object

```json
{
  "id": "bank0",
  "match": "F0 47 00 6D 00 00 06",
  "writePrefix": "F0 47 7F 6D 00 00 06",
  "checksumType": "robkoo_xor",
  "writeLength": 44,
  "role": "battery",
  "byteIndex": 10
}
```

### `id: string`

Required. Referenced by parameters and advanced controls.

### `match: string`

Required. Space-separated hex header prefix.

### `writePrefix: string`

Optional. Replaces the first bytes of the outgoing write buffer during `writeAll`.

### `checksumType: string`

Optional. Currently supported in write-buffer rewrite:

- `robkoo_xor`

### `writeLength: integer`

Optional. Truncates or pads the outgoing buffer before write.

### `role: string`

Optional. Known roles:

- `battery`
- `patch_list`

### `byteIndex: integer`

Optional. Used for role-based value extraction such as battery percentage.

### Patch-list fields

Used only when `role` is `patch_list`:

- `pcByteIndex`
- `internalIdByteIndex`
- `versionByteIndex`
- `typeMap`
- `nameMap`

### `container` object

Optional. Describes the geometry of a fixed-stride record container inside
the response frame. Use this when a single SysEx response carries multiple
records (e.g. a full preset dump) and each parameter should be decoded from
a specific record slot.

```json
{
  "id": "fullDump",
  "match": "F0 04 0B 01",
  "container": {
    "type": "fixed_stride_records",
    "headerBytes": 23,
    "recordCount": 32,
    "recordStride": 190,
    "recordPayloadBytes": 183,
    "recordSeparator": "00 00 00 00 00 00 01"
  }
}
```

#### Container fields

| Field | Type | Default | Description |
|---|---|---|---|
| `type` | string | *required* | Container layout algorithm. Currently only `"fixed_stride_records"`. |
| `headerBytes` | integer | *required* | Number of bytes before the first record (SysEx header, device header, etc.). |
| `recordCount` | integer | *required* | Number of records in the container. |
| `recordStride` | integer | *required* | Total byte length of each record slot (payload + separator). |
| `recordPayloadBytes` | integer | *required* | Number of payload bytes at the start of each record slot. |
| `recordSeparator` | string | — | Optional space-separated hex bytes expected between records (after payload, within each stride). Mismatches are logged but do not prevent decode. |

#### Container geometry validation

On receive, the runtime verifies:

1. Frame length ≥ `headerBytes + recordCount × recordStride`
2. `recordPayloadBytes ≤ recordStride`

If either check fails, **all parameters sourced from this response are
skipped** — no values are updated from a malformed frame.

## Parameter object

Minimal shape:

```json
{
  "id": "volume",
  "min": 0,
  "max": 127,
  "default": 100
}
```

### Core fields

- `id`
- `min`
- `max`
- `default`

### Legacy SysEx fields

- `source`
- `byteIndex`

### Legacy CC fields

- `cc`
- `channel`

### Mixed protocol field

- `sendCommand`

### Feedback field

- `receiveCC`

### SysEx decode field

- `receiveDecode`

### Record container field

- `sourceRecordSelectorParam`

When the parameter's `source` response has a `container`, this field
names another parameter whose current value selects the record slot
(0-based). If omitted, the runtime defaults to record slot 0.

If the selector value is out of range (negative or ≥ `recordCount`),
the parameter update is skipped.

Example:

```json
{
  "id": "presetSlot",
  "min": 0,
  "max": 31,
  "default": 0
},
{
  "id": "pitch",
  "min": 0,
  "max": 1000,
  "source": "fullDump",
  "sourceRecordSelectorParam": "presetSlot",
  "receiveDecode": {
    "type": "moogPackedTriplet16",
    "byteIndex": 3,
    "output": "logical"
  }
}
```

### Value conversion fields

- `valueOffset`
- `valueInvert`
- `sendValueMap`
- `receiveValueMap`

### Side effects

- `onSet`
- `onSetByValue`

Runtime ordering when setting a parameter:

- first, the parameter own `sendCommand` is emitted
- then `onSet` rules are applied in declaration order
- finally, `onSetByValue[currentValue]` rules are applied in declaration order (if present)

Example:

```json
"onSet": [
  { "param": "liveKeysStream" },
  { "param": "padMute", "value": 1 }
]
```

Value-keyed example:

```json
"onSetByValue": {
  "0": [{ "param": "padMute", "value": 0 }],
  "1": [{ "param": "padMute", "value": 1 }]
}
```

### String parameters

Set `"valueType": "string"` to declare a text parameter. String parameters have no
immediate MIDI output — they are used as inputs to `"sequence"` actions via
`{{paramId:encoding}}` placeholders in `sysex_template` steps.

The optional `"initialString"` field sets the default text value (analogous to
`"default"` for int parameters).

Use a `"text_input"` control to let the user edit the value.

```json
{
  "id": "patchName",
  "valueType": "string",
  "stringRules": {
    "maxLength": 13,
    "ascii": true,
    "uppercase": true,
    "rightPadChar": " "
  },
  "initialString": ""
}
```

#### `stringRules` object

| Field | Type | Default | Description |
|---|---|---|---|
| `maxLength` | integer | 64 | Maximum number of characters allowed. |
| `ascii` | boolean | `true` | Strip any character outside the printable ASCII range (0x20–0x7E) before storing. |
| `uppercase` | boolean | `false` | Convert all characters to uppercase before storing. |
| `rightPadChar` | string | `" "` | Single ASCII character used to pad the value to the required length in a `sysex_template`. |

## `sendCommand` object

### Common fields

- `type`
- `channel`
- `transform`

### Type: `cc`

```json
"sendCommand": {
  "type": "cc",
  "cc": 7
}
```

### Type: `program_change`

```json
"sendCommand": {
  "type": "program_change"
}
```

### Type: `nrpn`

```json
"sendCommand": {
  "type": "nrpn",
  "nrpnMsb": 1,
  "nrpnLsb": 8
}
```

### Type: `sysex`

```json
"sendCommand": {
  "type": "sysex",
  "bytes": "F0 41 10 00 00 00 5A 12 00 27 34 13 $V $CS F7",
  "checksum": "ae01"
}
```

Supported `sysex` fields:

- `bytes`
- `checksum`
- `postChecksumBytes`
- `nibbleScale`
- `transform`

Supported checksum values:

- `ae01`
- `robkoo_xor`

Supported placeholders inside `bytes`:

- `$V`
- `$CS`
- `$N0`
- `$N1`
- `$N2`
- `$N3`
- `$P0`, `$P1`, ... in `multi_sysex`

### Type: `multi_sysex`

```json
"sendCommand": {
  "type": "multi_sysex",
  "channelByteIndex": 6,
  "channelByteBase": 16,
  "bytes": "F0 41 00 42 12 40 10 40 $V $P0 $P1 00 F7",
  "paramRefs": ["otherA", "otherB"]
}
```

### Type: `cc_pair`

```json
"sendCommand": {
  "type": "cc_pair",
  "cc1": 104,
  "cc1Value": 61,
  "cc2": 105
}
```

### Type: `cc_pair_14bit`

```json
"sendCommand": {
  "type": "cc_pair_14bit",
  "cc1": 104,
  "cc1ValueLsb": 85,
  "cc1ValueMsb": 88,
  "cc2": 105,
  "min": 0,
  "max": 16383
}
```

Behavior:

- Encodes a 14-bit parameter value across two `cc_pair` consecutive messages (LSB, then MSB).
- First message: `cc1 = cc1ValueLsb`, `cc2 = value & 0x7F`.
- Second message: `cc1 = cc1ValueMsb`, `cc2 = (value >> 7) & 0x7F`.
- `cc1`, `cc1ValueLsb`, `cc1ValueMsb`, and `cc2` are required fields (each in range `0..127`).
- `min` and `max` must bound the total 14-bit range (max 16383) to limit user input prior to sending.

### Type: `cc_index_toggle`

```json
"sendCommand": {
  "type": "cc_index_toggle",
  "cc": 106,
  "baseIndexOn": 20,
  "baseIndexOff": 30,
  "bitCount": 9
}
```

Behavior:

- Handles up to 32 bits (array of toggles, typically bound to a `pressed_keys` UI control).
- For each bit set to `1` in the `value` integer, it emits a single message with CC `(baseIndexOn + bitPosition)` and data byte `0`.
- For each bit set to `0`, it emits a single message with CC `(baseIndexOff + bitPosition)` and data byte `0`.
- Requires `cc`, `baseIndexOn`, `baseIndexOff`, and `bitCount`. 
- No value is written to a secondary "data CC"—the identity of the target CC itself indicates the action.

### Type: `cc_sequence`

```json
"sendCommand": {
  "type": "cc_sequence",
  "messages": [
    { "cc": 102, "value": 30 },
    { "cc": 102, "useParam": true }
  ]
}
```

### Type: `cc14`

```json
"sendCommand": {
  "type": "cc14",
  "ccMsb": 9,
  "ccLsb": 41,
  "exactPairs": {
    "12": { "msb": 12, "lsb": 102 },
    "32": { "msb": 32, "lsb": 98 }
  }
}
```

Behavior:

- `ccMsb` is required and must be in range `0..31`
- `ccLsb` is optional; if omitted, runtime derives it as `ccMsb + 32`
- `exactPairs` is optional and maps logical values (`"0".."127"`) to exact `{ msb, lsb }` output bytes
- when `exactPairs` contains the current value, runtime sends that exact pair
- when `exactPairs` has no matching key, runtime falls back to scaled conversion
- fallback conversion is `value14 = round(value7 * 16383 / 127)`
- runtime sends exactly two CC messages in this order: MSB first, then LSB
- `channel` and `transform` behave like other send commands

### Type: `sysex_map`

```json
"sendCommand": {
  "type": "sysex_map",
  "options": {
    "0": "F0 7D 10 00 F7",
    "1": "F0 7D 10 01 F7"
  }
}
```

Behavior:

- `options` maps integer logical/raw values (as string keys) to full SysEx frames
- when a matching key exists, runtime sends the mapped frame verbatim
- when no key matches, runtime sends nothing for that command

## Transform object

```json
{
  "inputMin": 0,
  "inputMax": 10,
  "outputMin": 0,
  "outputMax": 127
}
```

The runtime applies linear interpolation with rounding.

## `receiveDecode` object

Optional object on a parameter that tells the runtime how to decode a
multi-byte packed value from an incoming SysEx response.

When `receiveDecode` is present, the usual single-byte `byteIndex` path
is skipped for that parameter.

### Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `type` | string | *required* | Decode algorithm. Currently only `"moogPackedTriplet16"`. |
| `tripletIndex` | integer | — | Zero-based ordinal index of the 3-byte triplet, starting at `tripletStartByte`. |
| `tripletStartByte` | integer | `0` | Byte offset in the full SysEx frame where triplet counting begins. |
| `byteIndex` | integer | — | Byte offset of the first byte of the triplet. When the parameter's response has a `container`, this is relative to the start of the record payload (not the full SysEx frame). Takes priority over `tripletIndex`. |
| `output` | string | — | When `"logical"`, the decoded value is scaled linearly from 0..65535 into the parameter's `min`..`max` range. |

Either `byteIndex` **or** `tripletIndex` must be provided.

### Type: `moogPackedTriplet16`

Decodes 3 consecutive bytes as a 16-bit value using a 4+6+6 bit packing
scheme (Moog Theremini style):

- **b0** must be in `0x40..0x4F` (4-bit high nibble)
- **b1** must be in `0x00..0x3F` (6-bit mid)
- **b2** must be in `0x00..0x3F` (6-bit low)
- `value16 = ((b0 - 0x40) << 12) | (b1 << 6) | b2` → range 0..65535

If any byte is out of its valid range the parameter update is silently
skipped (a warning is logged in developer/debug mode).

### Example: byteIndex

```json
{
  "id": "pitch",
  "min": 0,
  "max": 1000,
  "source": "settings",
  "receiveDecode": {
    "type": "moogPackedTriplet16",
    "byteIndex": 3,
    "output": "logical"
  }
}
```

### Example: tripletIndex

```json
{
  "id": "volume",
  "min": 0,
  "max": 100,
  "source": "settings",
  "receiveDecode": {
    "type": "moogPackedTriplet16",
    "tripletIndex": 1,
    "tripletStartByte": 3,
    "output": "logical"
  }
}
```

In the second example the runtime computes
`byteOffset = 3 + 1 × 3 = 6` and reads 3 bytes starting there.

## Built-in presets

```json
"presets": [
  {
    "name": "Default",
    "values": {
      "volume": 100,
      "reverb": 0
    }
  }
]
```

Values are logical values keyed by parameter id.

## UI object

```json
"ui": {
  "keyboardDefinitions": { ... },
  "tabs": [ ... ],
  "actions": [ ... ]
}
```

## Tabs and sections

### Tab object

```json
{
  "label": "Main",
  "enabled": true,
  "sections": [ ... ]
}
```

### Section object

```json
{
  "title": "Sound",
  "helpAnchor": "tab-main",
  "enabled": true,
  "controls": [ ... ]
}
```

Section fields:

- `title`: optional section title
- `helpAnchor`: optional explicit deep-link target for the section `i` icon
- `enabled`: optional, defaults to `true`
- `controls`: required control list

### Section help deep link (the `i` icon)

When a section can be linked to plugin help, Hemiola renders an `i` icon on that section header.
Pressing the icon opens the in-app Help view and jumps to the matching plugin help section.

How matching works:

- if `section.helpAnchor` is set, it is matched first against `help[].anchor` (preferred) or `help[].title` (exact, case-insensitive)
- if no explicit anchor match is found, the runtime falls back to legacy behavior
- legacy fallback: the app takes the current tab label (for example `Main`) and matches the first `help[].title` that contains it (case-insensitive)

Authoring recommendation:

- for deterministic deep links, define `help[].anchor` and reference it from `section.helpAnchor`
- keep `help[].title` as user-facing text only
- if you do not use anchors, include the tab label in `help[].title` for legacy matching

Example:

```json
{
  "ui": {
    "tabs": [
      {
        "label": "Main",
        "sections": [
          {
            "title": "Sound",
            "helpAnchor": "tab-main",
            "controls": [ ... ]
          }
        ]
      }
    ]
  },
  "help": [
    {
      "anchor": "tab-main",
      "title": "Tab: Main",
      "icon": "info",
      "entries": [
        {
          "type": "para",
          "text": "This section explains the Main tab controls."
        }
      ]
    }
  ]
}
```

## Control types

Supported control `type` values:

- `slider`
- `dropdown`
- `toggle`
- `knob`
- `tile_picker`
- `preset_picker`
- `cc_select`
- `pressed_keys`
- `custom_fingering_manager`
- `text_input`
- `action`

### Common control fields

- `type`
- `param`
- `label`
- `inline`
- `min`
- `max`
- `enabled`

`inline` defaults to `false`.

- `inline: false` (or omitted) starts a new row.
- `inline: true` places the control on the same row as the previous non-knob control in the section.

Row width is shared equally by default. If `size` is set on inline controls, it is used as relative row weight.

Example:

```json
[
  {
    "type": "dropdown",
    "param": "saveTargetSlot",
    "label": "Target Slot"
  },
  {
    "type": "text_input",
    "param": "presetNameToSave",
    "label": "Patch Name",
    "inline": true
  }
]
```

### Shared option fields

- `options`
- `optionLabels`
- `colors`

### `knob`-specific helpers

- `size`
- `color` — accent colour for the knob arc (`"#RRGGBB"` string or `0xAARRGGBB` int)
- `displayOffset`
- `inputOffset`
- `valueFormatter`

### `toggle`-specific helpers

- `color` — accent colour applied to the switch thumb and track outline when on (`"#RRGGBB"` string or `0xAARRGGBB` int). Use a full-saturation colour; the renderer applies reduced opacity automatically for the track outline.

`valueFormatter` is display-only and does not affect parameter values or MIDI output.

Supported formatter type:

- `midi_note`

Example:

```json
{
  "type": "knob",
  "param": "lowNote",
  "label": "Low Note",
  "min": 0,
  "max": 127,
  "valueFormatter": {
    "type": "midi_note",
    "octaveBase": -1,
    "style": "sharp"
  }
}
```

Theremini-style low/high note pair:

```json
[
  {
    "type": "knob",
    "param": "lowNote",
    "label": "Low Note",
    "min": 0,
    "max": 127,
    "valueFormatter": {
      "type": "midi_note",
      "octaveBase": -1,
      "style": "sharp"
    }
  },
  {
    "type": "knob",
    "param": "highNote",
    "label": "High Note",
    "min": 0,
    "max": 127,
    "valueFormatter": {
      "type": "midi_note",
      "octaveBase": -1,
      "style": "sharp"
    }
  }
]
```

### `tile_picker` patch-list fields

- `patchListSource`
- `patchNameMap`

When `patchListSource` is set, the control options are populated dynamically from a `patch_list` response.

### `preset_picker` fields

- `params`
- `presets`
- `valueOffset`

### `pressed_keys` fields

- `keyboardRef`
- `noteParams`
- `source`
- `bitByteIndex`
- `bits`
- `bitOrder`
- `sources`
- `groups`
- `noteOnVelocity`

### `custom_fingering_manager` fields

- `keyboardRef`
- `customProfile`
- `slotCount`
- `includeDisabledSlot`
- `slotDataSource`
- `slotDataOffset`
- `disabledDataSource`
- `addressPrefix`
- `slotStride`
- `enabledOffset`
- `highOffset`
- `lowOffset`
- `noteOffset`
- `disabledHighAddress`
- `disabledLowAddress`
- `checksum`
- `listenStreamParam`
- `padModeParam`

### `text_input`

A single-line text field bound to a `"string"` parameter.

```json
{
  "type": "text_input",
  "param": "patchName",
  "label": "Patch Name"
}
```

The input field respects `stringRules` from the bound parameter:
- `maxLength` limits the number of characters the field accepts.
- `uppercase: true` enables keyboard-level uppercasing (`TextCapitalization.characters`).

No MIDI is sent on input — use a `"sequence"` action to send the value to the device.

### `action`

An inline action button declared as a control.

The action payload matches `ui.actions` (same `action` values and fields).

```json
{
  "type": "action",
  "label": "Refresh",
  "action": "request"
}
```

You can also use full action payloads, for example:

```json
{
  "type": "action",
  "label": "Save as...",
  "action": "sequence",
  "confirm": {
    "title": "Confirm Save",
    "text": "Write current values to selected slot?",
    "yesLabel": "Save",
    "noLabel": "Cancel"
  },
  "steps": [
    { "type": "writeAll" },
    { "type": "cc", "cc": 119, "value": 127 }
  ]
}
```

## Keyboard definitions

`ui.keyboardDefinitions` lets multiple controls share the same key map.

Fields:

- `options`
- `optionLabels`
- `noteParams`
- `groups`
- `source`
- `sources`
- `bitByteIndex`
- `bits`
- `bitOrder`
- `keyBits`

## Action objects

```json
{
  "label": "Write",
  "action": "writeAll"
}
```

Actions can be declared in:

- `ui.actions` (global action bar actions)

Supported `action` values:

- `writeAll`
- `request`
- `sysex`
- `cc`
- `sequence`

### `writeAll`

Behavior depends on protocol type.

- `sysex`: writes all bank buffers back out, deduplicated by source bank id
- `cc`: sends all CC-backed parameters
- `mixed`: sends all parameters with either `sendCommand` or legacy `cc`

### `request`

Resends all `protocol.onConnect` messages.

### `sysex`

Sends the raw bytes defined in `action.bytes`.

### `cc`

Sends one raw Control Change using `cc`, optional `value`, and optional `channel`.

### Optional action confirmation

Any action can include an optional `confirm` object. When present, the app
shows a confirmation alert and executes the action only when the user accepts.

```json
{
  "label": "Write",
  "action": "writeAll",
  "confirm": {
    "title": "Confirm Write",
    "text": "Write current values to the device?",
    "yesLabel": "Write",
    "noLabel": "Cancel"
  }
}
```

`confirm` fields:

- `title`
- `text`
- `yesLabel`
- `noLabel`

### Optional action tab scoping

Any action can include an optional `tabs` array with tab labels where the
action should be visible.

```json
{
  "label": "Save as...",
  "action": "sequence",
  "tabs": ["Save"]
}
```

Rules:

- `tabs` omitted or empty: action is visible on all tabs
- one label in `tabs`: action visible on one tab only
- multiple labels in `tabs`: action visible on those tabs only
- matching is done against tab `label` values

### `sequence`

Runs an ordered list of MIDI steps atomically. If any step fails to render,
the entire sequence is aborted and nothing is sent.

```json
{
  "label": "Store",
  "action": "sequence",
  "steps": [
    {
      "type": "sysex_template",
      "template": "F0 04 26 {{patchName:ascii13}} 00 F7"
    },
    {
      "type": "sysex",
      "bytes": "F0 04 26 44 45 4C 41 59 20 4E 41 4D 45 20 20 20 00 F7"
    },
    { "type": "send_param", "param": "delayTime" },
    { "type": "writeAll" },
    { "type": "program_change", "value": 0 },
    { "type": "cc", "cc": 119, "value": 127 }
  ]
}
```

#### Sequence step types

| Step type | Required fields | Description |
|---|---|---|
| `sysex_template` | `template` | SysEx frame with `{{paramId:encoding}}` placeholders. |
| `sysex` | `bytes` | Fixed SysEx frame (space-separated hex bytes). |
| `writeAll` | — | Emit all buffered int-parameter CC/SysEx messages (same as the standalone `writeAll` action). |
| `send_param` | `param` | Emit the current value of the named parameter using its `sendCommand`. |
| `program_change` | exactly one of `value` or `param` | Send a Program Change on `channel` (or the protocol default). |
| `cc` | `cc`, `value` | Send a Control Change on `channel` (or the protocol default). |
| `expect_cc` | `cc` | Suspend sequence until seeing the specified CC, abiding by `timeoutMs`. |

For `send_param`:

- `param` must name a parameter from `parameters[]`
- runtime uses the parameter's current value at sequence execution time
- if the parameter has no `sendCommand`, the step is a no-op
- if the parameter id does not exist, the sequence is aborted

For `expect_cc`:

- requires `cc`
- supports optional `timeoutMs` (defaults to 1000 ms) and `channel`
- if the specified `cc` event is matched in the bridge inbound stream within the timeout, the sequence continues
- if the timeout is reached without the matching CC arriving, the sequence skips or aborts subsequent dependent steps

For `program_change`:

- `value`: static program number (0..127)
- `param`: parameter id whose current integer value is used as program number
- Exactly one of `value` or `param` must be present
- If `param` does not resolve to an integer parameter, or resolves outside 0..127, the sequence is aborted

#### `sysex_template` placeholders

Format: `{{paramId:encoding}}`

Only `ascii<N>` encoding is currently supported:

- `N` is the exact number of bytes to emit.
- The string value of the named parameter is ASCII-encoded byte-by-byte.
- If the value is shorter than `N`, it is right-padded with `stringRules.rightPadChar` (default space, 0x20).
- If any character is outside the printable ASCII range (0x20–0x7E), the sequence is aborted.
- If the referenced parameter does not exist or has no string value, an empty string is used (all padding).

Example:

```
"F0 04 26 {{patchName:ascii13}} 00 F7"
```

With `patchName = "COOL"` and `rightPadChar = " "`, the 13 bytes emitted are:
`43 4F 4F 4C 20 20 20 20 20 20 20 20 20`

## Help sections

The top-level `help` field is an array of app-native help sections.

Help section fields:

- `anchor` (optional): explicit stable key for section deep-linking
- `id` (optional): legacy alias accepted as anchor
- `title` (required): user-facing title shown in Help UI
- `icon` (required): material icon key
- `entries` (required): list of help entries

Observed entry types in current plugins include:

- `para`
- `note`
- `subtitle`
- `item`

## Runtime behaviors worth knowing

- bundled plugins load from `assets/devices/*.json`
- temporary author testing happens through Hemiola Plugin Developer Mode in the host app
- Developer Mode validates a selected JSON file before rendering it
- Developer Mode renders the plugin in sandbox mode without registering or persisting it
- in sandbox mode, inbound MIDI still reaches the plugin but outbound MIDI is queued until the user presses `Send`
- if a required behavior cannot be modeled with the current schema/runtime, create a gap analysis and maintainer instructions before proposing schema/runtime changes
- a JSON plugin is skipped if `enabled` is `false`
- `setParam()` updates logical state before building outbound MIDI
- `sysex` bank edits are usually buffered until `writeAll`
- advanced widgets such as `pressed_keys` and `custom_fingering_manager` rely on explicit runtime conventions, not arbitrary generic form behavior