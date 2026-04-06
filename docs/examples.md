# Examples

This file shows practical plugin patterns.

Copy the smallest example that matches your device, then extend it.

## Which template should I start from?

- If the device is configured only through CC messages, start from `../templates/plugin.cc.template.json`.
- If the device is edited through bank dumps and full-bank writes, start from `../templates/plugin.sysex.template.json`.
- If the device mixes CC, NRPN, SysEx, or Program Change, start from `../templates/plugin.template.json`.

## Example 1: minimal CC-only plugin

```json
{
  "slug": "simple_cc_device",
  "name": "Simple CC Device",
  "version": "1.0.0",
  "enabled": true,
  "triggers": ["SimpleCC"],
  "requiresLandscape": false,
  "protocol": {
    "type": "cc",
    "channel": 0,
    "onConnect": []
  },
  "parameters": [
    { "id": "volume", "cc": 7, "min": 0, "max": 127, "default": 100 },
    { "id": "expression", "cc": 11, "min": 0, "max": 127, "default": 127 },
    { "id": "reverb", "cc": 91, "min": 0, "max": 127, "default": 0 }
  ],
  "ui": {
    "tabs": [
      {
        "label": "Main",
        "sections": [
          {
            "title": "Mix",
            "controls": [
              { "type": "slider", "param": "volume", "label": "Volume" },
              { "type": "slider", "param": "expression", "label": "Expression" },
              { "type": "slider", "param": "reverb", "label": "Reverb" }
            ]
          }
        ]
      }
    ],
    "actions": [
      { "label": "Send All", "action": "writeAll" }
    ]
  }
}
```

## Example 2: bulk SysEx bank plugin

```json
{
  "slug": "bulk_sysex_device",
  "name": "Bulk SysEx Device",
  "version": "1.0.0",
  "enabled": true,
  "triggers": ["BulkSysEx"],
  "requiresLandscape": false,
  "protocol": {
    "type": "sysex",
    "channel": 0,
    "autoWrite": false,
    "onConnect": [
      { "bytes": "F0 47 7F 6D 40 00 00 F7" }
    ],
    "responses": [
      {
        "id": "bank0",
        "match": "F0 47 00 6D 00 00 06",
        "writePrefix": "F0 47 7F 6D 00 00 06"
      }
    ]
  },
  "parameters": [
    { "id": "gain", "source": "bank0", "byteIndex": 7, "min": 0, "max": 127, "default": 64 },
    { "id": "curve", "source": "bank0", "byteIndex": 8, "min": 0, "max": 5, "default": 2 }
  ],
  "ui": {
    "tabs": [
      {
        "label": "Main",
        "sections": [
          {
            "title": "Response",
            "controls": [
              { "type": "knob", "param": "gain", "label": "Gain" },
              {
                "type": "tile_picker",
                "param": "curve",
                "label": "Curve",
                "options": [0, 1, 2, 3, 4, 5],
                "optionLabels": ["1", "2", "3", "4", "5", "Auto"]
              }
            ]
          }
        ]
      }
    ],
    "actions": [
      { "label": "Read", "action": "request" },
      { "label": "Write", "action": "writeAll" }
    ]
  }
}
```

## Example 3: mixed plugin with transforms

```json
{
  "slug": "mixed_device",
  "name": "Mixed Device",
  "version": "1.0.0",
  "enabled": true,
  "triggers": ["Mixed Device"],
  "requiresLandscape": false,
  "protocol": {
    "type": "mixed",
    "channel": 0,
    "onConnect": []
  },
  "parameters": [
    {
      "id": "volume",
      "min": 0,
      "max": 10,
      "default": 5,
      "sendCommand": {
        "type": "cc",
        "cc": 7,
        "transform": { "inputMin": 0, "inputMax": 10, "outputMin": 0, "outputMax": 127 }
      }
    },
    {
      "id": "program",
      "min": 0,
      "max": 127,
      "default": 0,
      "sendCommand": {
        "type": "program_change"
      }
    },
    {
      "id": "vibratoRate",
      "min": 0,
      "max": 127,
      "default": 64,
      "sendCommand": {
        "type": "nrpn",
        "nrpnMsb": 1,
        "nrpnLsb": 8
      }
    }
  ],
  "ui": {
    "tabs": [
      {
        "label": "Main",
        "sections": [
          {
            "controls": [
              { "type": "knob", "param": "volume", "label": "Volume", "min": 0, "max": 10 },
              { "type": "knob", "param": "program", "label": "Program" },
              { "type": "knob", "param": "vibratoRate", "label": "Vibrato Rate" }
            ]
          }
        ]
      }
    ],
    "actions": [
      { "label": "Send All", "action": "writeAll" }
    ]
  }
}
```

## Example 4: patch-list driven tile picker

Response:

```json
{
  "id": "patches",
  "role": "patch_list",
  "match": "F0 00 21 59 00 01 00 02 02 01",
  "pcByteIndex": 10,
  "internalIdByteIndex": 11,
  "versionByteIndex": 20,
  "typeMap": { "16": "Builtin", "17": "Value", "18": "Free" },
  "nameMap": {
    "16": { "2": "Pop Alto Saxophone" },
    "18": { "24": "Clarinet" }
  }
}
```

Control:

```json
{
  "type": "tile_picker",
  "param": "instrument",
  "label": "Instrument",
  "patchListSource": "patches"
}
```

## Example 5: pressed-keys from one SysEx bitfield

```json
{
  "type": "pressed_keys",
  "param": "",
  "label": "Pressed Keys",
  "options": [72, 71, 69, 67],
  "optionLabels": ["Key A", "Key B", "Key C", "Key D"],
  "source": "liveKeys",
  "bitByteIndex": 10,
  "bits": [0, 1, 2, 3],
  "bitOrder": "lsb"
}
```

## Example 6: keyboard definitions to avoid duplication

```json
"ui": {
  "keyboardDefinitions": {
    "mainFingering": {
      "options": [72, 63, 61],
      "optionLabels": ["Ok", "Oct Up", "Oct Down"],
      "noteParams": ["padNoteOk", "padNoteUp", "padNoteDown"],
      "groups": [
        { "label": "Buttons", "indices": [0, 1, 2] }
      ],
      "sources": [
        {
          "source": "liveKeys",
          "bitByteIndex": 10,
          "bitOrder": "lsb",
          "bits": [12, 11, 10]
        }
      ]
    }
  }
}
```

## Example 7: custom fingering manager

Clarii-like:

```json
{
  "type": "custom_fingering_manager",
  "param": "",
  "label": "Custom Fingerings",
  "keyboardRef": "mainFingering",
  "customProfile": "clarii",
  "slotCount": 256,
  "includeDisabledSlot": false,
  "slotDataSource": "fingeringCustom",
  "slotDataOffset": 10,
  "listenStreamParam": "liveKeysStream",
  "padModeParam": "padMode",
  "checksum": "robkoo_xor"
}
```

AE-01-like:

```json
{
  "type": "custom_fingering_manager",
  "param": "",
  "label": "Custom Fingerings",
  "keyboardRef": "mainFingering",
  "slotCount": 10,
  "includeDisabledSlot": true,
  "slotDataSource": "fingeringCustom",
  "disabledDataSource": "disabledKeys",
  "checksum": "ae01",
  "addressPrefix": [0, 53, 0],
  "slotStride": 8,
  "enabledOffset": 1,
  "highOffset": 2,
  "lowOffset": 5,
  "noteOffset": 8,
  "disabledHighAddress": [0, 39, 52, 8],
  "disabledLowAddress": [0, 39, 52, 11]
}
```

## Example 8: embedded help

```json
"help": [
  {
    "title": "My Device – Overview",
    "icon": "air",
    "entries": [
      { "type": "para", "text": "This plugin edits the device configuration." },
      { "type": "note", "text": "Use Read before editing if the hardware state may have changed." }
    ]
  }
]
```

## Example 9: recommended incremental build plan

1. identify device and register plugin
2. add one tab and two parameters
3. verify outbound messages
4. add readback support
5. add actions
6. add presets and help

## Example 10: string parameter, text\_input control, and sequence action

Shows how to let the user name a preset patch and store it with a single
button using the `"sequence"` action.

```json
{
  "slug": "store_sequence_demo",
  "name": "Store Sequence Demo",
  "version": "1.0.0",
  "enabled": true,
  "triggers": ["StoreDemo"],
  "protocol": {
    "type": "cc",
    "channel": 0
  },
  "parameters": [
    {
      "id": "patchSlot",
      "cc": 0,
      "min": 0,
      "max": 127,
      "default": 0
    },
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
  ],
  "ui": {
    "tabs": [
      {
        "label": "Store",
        "sections": [
          {
            "title": "Patch",
            "controls": [
              { "type": "dropdown", "param": "patchSlot", "label": "Slot" },
              { "type": "text_input", "param": "patchName", "label": "Name" }
            ]
          }
        ]
      }
    ],
    "actions": [
      {
        "label": "Store",
        "action": "sequence",
        "tabs": ["Store"],
        "confirm": {
          "title": "Confirm Store",
          "text": "Store patch name and settings to the selected slot?",
          "yesLabel": "Store",
          "noLabel": "Cancel"
        },
        "steps": [
          {
            "type": "sysex_template",
            "template": "F0 04 26 {{patchName:ascii13}} 00 F7"
          },
          {
            "type": "sysex",
            "bytes": "F0 04 26 44 45 4C 41 59 20 4E 41 4D 45 20 20 20 00 F7"
          },
          { "type": "send_param", "param": "patchSlot" },
          { "type": "program_change", "param": "patchSlot" },
          { "type": "cc", "cc": 119, "value": 127 }
        ]
      }
    ]
  }
}
```

Key points:
- `patchName` uses `"valueType": "string"` — no MIDI is sent on input; the text is stored in state only.
- The `"text_input"` control renders a labeled text field. `maxLength` and `uppercase` are taken from `stringRules`.
- `confirm` is optional on actions; when present, the action runs only after explicit user confirmation.
- `tabs` is optional on actions; here `"tabs": ["Store"]` keeps the action visible only in the Store tab.
- `send_param` emits one parameter's current value using that parameter's `sendCommand`.
- `program_change` can read its value dynamically from a parameter via `"param"` (here: `patchSlot`).
- The `"sequence"` action fires all steps in order, or aborts entirely if any step cannot be rendered.
- In the `sysex_template` step, `{{patchName:ascii13}}` encodes the stored string as 13 ASCII bytes, right-padded with spaces.

7. only then add advanced controls such as patch lists or pressed-keys