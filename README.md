# Constraint Lab — Furnace & PO-33 Technique References

Single-page, offline-friendly references for making music on small machines —
the [Furnace tracker](https://github.com/tildearrow/furnace) and the Teenage
Engineering PO-33 K.O! sampler, switchable from the sidebar. Every technique card
explains the idea, shows a copyable pattern snippet, lists the instrument macro
settings, and plays an in-browser Web Audio demo so you can hear it before you
open the tracker.

**Live site:** https://mwburke.github.io/constraint-lab/

## What's inside

### Furnace

| Section | Contents |
|---|---|
| 1–4. Bass, Articulation, Textures, Timbre | Core pattern-writing techniques: octave pumps, ostinatos, chirps, portamento, arps, pseudo-echo, PWM |
| 5. Tight-Constraint Craft | Getting a full arrangement out of 3–4 voice chips: compound melody, channel sharing, colour without duty control, Game Boy sweep and wave-channel work, hocket |
| 6. FM Synthesis | Algorithms, Genesis bass, brass bloom, feedback percussion, operator detune (OPN/OPM/OPL) |
| 7. Modern & Retro Tricks | Supersaw stacks, fake sidechain ducking, growl/hard-sync leads, Reese bass, legato runs, lo-fi beds |
| 8. Furnace Macro Recipes | How the macro editor really behaves — loop/release points as ADSR, relative vs fixed arps, pitch vs arp macros, wave morphing, macro speed/delay, reusable instrument banks |
| 9. Percussion & Noise | One-channel noise kits, tonal-channel kicks, periodic vs white noise, fills and risers, sample-layering discipline |
| 10. Classic Game OST Audits | 14 composer/game breakdowns — Follin, Kondo, Tanaka, Hubbard, Uematsu, Tel, Yamagishi, Huelsbeck, Sunsoft, González, Wise, Konami, Koshiro |
| 11. Effect Command Reference | Expanded tracker effect table with practical usage notes |
| 12. Chip Channel Cheat Sheet | Voices, timbre palette and composing consequences for 2A03, VRC6, FDS, DMG, SN76489, AY, SID, HuC6280, YM2612, YM2151, SCC, Paula |
| 13. Melodic & Harmonic Craft | Motif transformation, contrary motion, a harmonic palette by mood, walking bass, half-time/double-time and comping |
| 14. Game-Scoring Craft | Composing around SFX channel theft, intro-then-loop cue structure, stingers and jingles, leitmotif variants |
| 15. Composition Playbook | Channel budgeting, loop-friendly form, melody writing, harmony under constraint, groove, mixing, tension, workflow, pre-release checklist |
| 16. Macro Generator | Builds arp/duty macro strings from a chord type and attack transient |
| 17. Tempo, Tick & Groove Calculator | Converts tick rate / speed / rows-per-beat to BPM, and derives matching `ECxx`, `EDxx`, echo-delay and swing values |

Search and the chip-tag filters work across every card; sections with no
matching content collapse automatically.

Audio requires one click on **Initialize Web Chiptune Synthesizer** in the
sidebar (browsers block audio until a user gesture).

## Hosting it on GitHub Pages

The site is a single static `index.html` with no build step.

1. Create a repository (`constraint-lab`) and push this folder:

```bash
git remote add origin https://github.com/mwburke/constraint-lab.git
git branch -M main
git push -u origin main
```

2. In the repository, open **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to *Deploy from a branch*,
   then choose branch `main` and folder `/ (root)`. Save.
4. Wait a minute; the site appears at
   `https://mwburke.github.io/constraint-lab/`.

`.nojekyll` is included so GitHub serves the files as-is.

### Running it locally

Just open `index.html` in a browser — or serve it:

```bash
python3 -m http.server 8000
```

## Notes

* Styling uses the Tailwind CDN, Font Awesome and Google Fonts, so the page
  needs a network connection for its full look (content and audio still work
  offline, unstyled).
* Effect commands numbered `10xx` and above are chip-specific. Furnace's own
  effect list panel for the active chip is always the authority.

### PO-33 K.O!

| Section | Contents |
|---|---|
| 1. Sampling & the 40-Second Budget | Hold-to-record via mic or line in, allocating the shared 40 seconds, trimming with knobs A/B, what material survives a lo-fi sampler |
| 2. Slots: Drum Slicing vs Melodic Keys | Keys 1–8 play a whole sound chromatically; keys 9–16 slice one sound across the pads — plus putting a melody in a drum slot |
| 3. Step Patterns, Chaining & Swing | Step write vs quantized live punch-in, chaining up to 128 patterns into a track, BPM presets and the swing knob |
| 4. Punch-In Effects as Performance | Loop/stutter/retrigger as transitions, reverse and scratch gestures, using effects instead of spending pattern slots |
| 5. Sync, Backup & Workflow | Jam sync and recording takes, and the data-transfer trap that erases the receiving unit |

Operating details are taken from [Teenage Engineering's own PO-33 guide](https://teenage.engineering/guides/po-33/en),
which differs from some retailer copy (TE: keys 1–8 melodic, 9–16 drum).
