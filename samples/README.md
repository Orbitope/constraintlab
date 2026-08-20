# PO-33 Chiptune Sample Pack

Chip-accurate material rendered for a Teenage Engineering PO-33 K.O!, laid out so
**the file number is the slot number**. Files 01–08 go in the melodic slots,
09–15 in the drum slots, and slot 16 is deliberately left empty for whatever you
sample yourself.

Regenerate or tweak with `python3 make_po33_pack.py` (stdlib only, no deps).

## Why it's split this way

The two halves of the PO-33 keyboard behave differently, and that dictates what is
worth putting where:

- **Melodic slots (keys 1–8)** play the *whole* sound, pitched across the keyboard.
  Pitch and length are linked, so playing low makes the sample longer and heavier.
  Worth spending memory on **sustained chords and long tones** — the things you
  want to pitch-shift.
- **Drum slots (keys 9–16)** slice *one* sound into 16 equal parts, one per key,
  each playing at its recorded pitch. So a bank of 16 evenly-spaced notes becomes a
  **16-note playable instrument for the price of one sample.** That is where all the
  staccato notes, arps and drums live.

Every bank below is rendered as exactly 16 equal slices with each sound landing on
its slice boundary and decaying before the next one, so the machine's even slicing
lines up with the notes.

## Memory

PO-33 memory is **40 seconds total** (per Teenage Engineering's guide — you
mentioned 30, you have more room than you thought).

| Pack | Length | Free after |
|---|---|---|
| Core, files 01–13 | 27.5 s | 12.5 s |
| Full, files 01–15 | 34.2 s | 5.8 s |

If you want maximum room for your own sampling, skip 14 and 15.

## Slot map

### Melodic slots — one sound each, played chromatically

| Slot | File | Sound | Len |
|---|---|---|---|
| 1 | `01_chord_major.wav` | C major triad, detuned pulse stack, soft swell | 1.6 s |
| 2 | `02_chord_minor.wav` | C minor triad | 1.6 s |
| 3 | `03_chord_maj7.wav` | C major 7th | 1.6 s |
| 4 | `04_chord_min7.wav` | C minor 7th | 1.6 s |
| 5 | `05_lead_square_25.wav` | C4 square lead, 25% duty, late vibrato | 1.4 s |
| 6 | `06_wave_triangle.wav` | C3 4-bit stepped triangle, round and soft | 1.4 s |
| 7 | `07_pad_pwm.wav` | C4 pad, duty breathing 12.5%→50% | 1.6 s |
| 8 | `08_bass_sub.wav` | C2 sub bass, 50% duty, tight tail | 1.2 s |

All chords are rooted on **C4**, so the middle of the keyboard is C and you can
transpose to any key. Pitch them **down** for pads and bass, **up** for stabs.

### Drum slots — 16 slices, one per key

| Slot | File | Bank | Len |
|---|---|---|---|
| 9 | `09_stab_bright_C4.wav` | Chromatic staccato, 25% duty, **C4 → D#5** | 2.7 s |
| 10 | `10_stab_fat_C3.wav` | Chromatic staccato, 50% duty, **C3 → D#4** | 2.7 s |
| 11 | `11_arps_maj_min.wav` | Quick arpeggios — 8 major, then 8 minor | 3.5 s |
| 12 | `12_drumkit.wav` | Chip drum kit | 3.0 s |
| 13 | `13_sfx.wav` | Blips and SFX | 3.5 s |
| 14 | `14_bass_bank_C2.wav` | Chromatic bass, 50% duty, **C2 → D#3** *(optional)* | 3.2 s |
| 15 | `15_chord_stabs.wav` | Chord stabs — 8 major, then 8 minor *(optional)* | 3.5 s |
| 16 | — | left free for your own sampling | — |

#### Chromatic banks (9, 10, 14)

Keys ascend one semitone at a time over 16 keys — an octave plus a major third:

| key | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| note | C | C# | D | D# | E | F | F# | G | G# | A | A# | B | C | C# | D | D# |

Slot 9 starts at C4, slot 10 at C3, slot 14 at C2.

#### Arps (11) and chord stabs (15)

Same root layout in both, so the two banks are playable interchangeably:

| key | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| **major** | C | D | E | F | G | A | A# | D# |

| key | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|
| **minor** | C | D | E | F | G | A | A# | D# |

Those roots cover a key properly. In C major: **C**(1) **Dm**(10) **Em**(11)
**F**(4) **G**(5) **Am**(14), plus **A#**(7) for the bVII and **D#**(8) for the bIII.

#### Drum kit (12)

| key | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
|  | kick | kick tight | snare | snare bright | closed hat | open hat | clap | rim |

| key | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|
|  | tom low | tom mid | tom high | cymbal | cowbell | shaker | zap perc | reverse swell |

#### SFX (13)

| key | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
|  | coin | power-up | laser | jump | explosion | blip | alarm | zap down |

| key | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|
|  | select | error | warp | impact | bubble | teleport | fall | chime |

## Recording into the PO-33

1. **Cable:** 3.5 mm male-to-male from your phone or laptop headphone out into the
   PO-33's **line in**. With a cable inserted the machine records line in instead of
   the mic, automatically.
2. **Level:** start around 70–80% source volume. Everything is normalised to
   −1.5 dBFS, so if one file is clean they all will be. Too hot distorts on the way
   in and you cannot undo it.
3. **Record:** cue the file paused at the start, then **hold `record` + the target
   key** and start playback at the same moment. Keep holding until the sound
   finishes, then release. Record slightly long — trimming is free, re-recording is not.
4. **Trim:** knob **A** sets the start, knob **B** sets the length. Pull the start
   onto the first transient and the length in to the end of the last sound.
5. **For the 16-slice banks this trim is the whole game.** Slices are even divisions
   of the trimmed length, so getting start and length right is what makes key 1 play
   note 1. Each sound decays well before its slice ends, so you have some tolerance —
   but check keys 1, 8 and 16 after trimming, not just key 1.

Work through the files in order and the slot numbers take care of themselves.

## Rebuilding this in Furnace

Nothing here needs Furnace to use, but if you want to re-render with a specific
chip's character, the recipes are plain:

- **Chords** — three or four pulse channels, 25–50% duty, detuned ±6 cents against
  each other, volume macro `4 7 10 12 13 14 15` at macro speed 3.
- **Staccato banks** — one pulse channel, volume macro `15 15 13 10 7 4 2 0` at
  speed 1, one note per pattern row, `ECxx` to keep them tight.
- **Arps** — same instrument plus effect `0047` (major) or `0037` (minor).
- **Drums** — noise channel with fast decay macros; kick is a pulse note with a
  steep pitch macro drop.

The important part is the **timing**: for a drum-slot bank every note must occupy
exactly 1/16 of the total, so set your speed and row count to divide evenly.
