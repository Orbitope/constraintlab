#!/usr/bin/env python3
"""
Render a chiptune sample pack sized for a Teenage Engineering PO-33 K.O!

Two slot types, two kinds of sample:

  MELODIC slots (keys 1-8)  one sound per slot, played chromatically across
                            the keyboard. Worth spending memory on sustained
                            chords and long tones you intend to pitch-shift.

  DRUM slots (keys 9-16)    one sound sliced into 16 equal parts, one per key.
                            A bank of exactly 16 evenly-spaced notes therefore
                            becomes a 16-note playable instrument for the price
                            of a single sample.

Everything is synthesised with stdlib Python only: naive (aliasing, like real
hardware) pulse waves, a 4-bit stepped triangle, an LFSR noise generator, and
volume envelopes quantised to 16 levels and stepped at 60 Hz, the way a chip
tracker's macros behave.
"""

import math, os, struct, wave

SR = 44100
TICK = 1.0 / 60.0            # macro step, as on an NTSC chip
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wav")
PEAK_DBFS = -1.5             # leave headroom so the PO-33's input never clips

NOTES = {'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,
         'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}


def freq(name):
    """'C4' / 'Eb3' -> Hz, A4 = 440."""
    i = 1
    while i < len(name) and not (name[i].isdigit() or name[i] == '-'):
        i += 1
    midi = (int(name[i:]) + 1) * 12 + NOTES[name[:i]]
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def env_at(macro, t, speed=1):
    """Volume macro value (0-15) at time t: stepped, holds its final value."""
    step = int(t / (TICK * speed))
    return macro[min(step, len(macro) - 1)] / 15.0


def tone(f, dur, wave_type='pulse', duty=0.5, macro=(15,), speed=1,
         detune=0.0, vib=0.0, vib_rate=5.5, vib_delay=0.0,
         slide_to=None, duty_sweep=None, arp=None, arp_speed=1):
    """One chip voice. Returns a list of floats."""
    n = int(dur * SR)
    out = [0.0] * n
    phase = 0.0
    f = f * (2 ** (detune / 1200.0))
    for i in range(n):
        t = i / SR
        fr = f
        if slide_to is not None:                       # exponential pitch slide
            fr = f * (slide_to / f) ** min(1.0, t / dur)
        if arp:                                        # tracker-style 0xy arp
            fr = fr * 2 ** (arp[int(t / (TICK * arp_speed)) % len(arp)] / 12.0)
        if vib and t > vib_delay:
            fr *= 2 ** (vib * math.sin(2 * math.pi * vib_rate * (t - vib_delay)) / 1200.0)
        phase += fr / SR
        phase -= int(phase)
        d = duty
        if duty_sweep:
            lo, hi, rate = duty_sweep
            d = lo + (hi - lo) * (0.5 - 0.5 * math.cos(2 * math.pi * rate * t))
        if wave_type == 'pulse':
            s = 1.0 if phase < d else -1.0
        elif wave_type == 'triangle':                  # 4-bit stepped, NES-style
            tri = 4 * abs(phase - 0.5) - 1
            s = round(tri * 7.5) / 7.5
        else:
            s = 0.0
        v = env_at(macro, t, speed)
        v = round(v * 15) / 15.0                       # 16 amplitude levels
        out[i] = s * v
    return out


_lfsr = 0x7FFF
def noise(dur, macro=(15,), speed=1, period=32, short=False, pitch_drop=None):
    """LFSR noise, as on NES/GB. `short` gives the metallic periodic mode."""
    global _lfsr
    n = int(dur * SR)
    out = [0.0] * n
    val, cnt = 1.0, 0.0
    for i in range(n):
        t = i / SR
        p = period
        if pitch_drop:
            p = period * (pitch_drop ** (t / dur))
        cnt += 1
        if cnt >= p:
            cnt = 0
            bit = (_lfsr ^ (_lfsr >> (6 if short else 1))) & 1
            _lfsr = (_lfsr >> 1) | (bit << 14)
            val = 1.0 if (_lfsr & 1) else -1.0
        v = env_at(macro, t, speed)
        out[i] = val * (round(v * 15) / 15.0)
    return out


def mix(*voices, gains=None):
    n = max(len(v) for v in voices)
    out = [0.0] * n
    for k, v in enumerate(voices):
        g = 1.0 if gains is None else gains[k]
        for i, s in enumerate(v):
            out[i] += s * g
    return out


def lowpass(buf, cutoff):
    a = math.exp(-2 * math.pi * cutoff / SR)
    y, out = 0.0, []
    for s in buf:
        y = (1 - a) * s + a * y
        out.append(y)
    return out


def dc_block(buf):
    """Non-50% duty pulses carry DC; remove it so it doesn't eat headroom."""
    a, out, xp, yp = 0.999, [], 0.0, 0.0
    for s in buf:
        yp = s - xp + a * yp
        xp = s
        out.append(yp)
    return out


def fade(buf, ms_in=2.0, ms_out=4.0):
    ni, no = int(ms_in * SR / 1000), int(ms_out * SR / 1000)
    for i in range(min(ni, len(buf))):
        buf[i] *= i / ni
    for i in range(min(no, len(buf))):
        buf[len(buf) - 1 - i] *= i / no
    return buf


def pad_to(buf, n):
    """Place a sound at the start of a fixed-length slot."""
    if len(buf) >= n:
        return buf[:n]
    return buf + [0.0] * (n - len(buf))


def normalize(buf, dbfs=PEAK_DBFS):
    peak = max(abs(s) for s in buf) or 1.0
    target = 10 ** (dbfs / 20.0)
    g = target / peak
    return [s * g for s in buf]


def write_wav(name, buf):
    os.makedirs(OUT, exist_ok=True)
    buf = normalize(dc_block(buf))
    path = os.path.join(OUT, name)
    with wave.open(path, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, s)) * 32767)) for s in buf))
    return path, len(buf) / SR


# ----------------------------------------------------------------------------
# envelopes, written the way you would type them into a Furnace volume macro
# ----------------------------------------------------------------------------
SUSTAIN   = [15]
PAD       = [4, 7, 10, 12, 13, 14, 15]          # soft swell, then hold
PLUCK     = [15, 14, 12, 10, 8, 6, 5, 4, 3, 2, 1, 0]
STAB      = [15, 15, 13, 10, 7, 4, 2, 0]
CLICK     = [15, 8, 3, 0]
LONGDECAY = [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]


def chord(root, intervals, dur, duty=0.5, macro=PAD, speed=3, spread=6.0):
    """Chip chord: one detuned pulse voice per note, mixed."""
    voices = []
    for k, iv in enumerate(intervals):
        det = spread * (k - (len(intervals) - 1) / 2.0)
        voices.append(tone(freq(root) * 2 ** (iv / 12.0), dur, 'pulse',
                           duty=duty, macro=macro, speed=speed, detune=det))
    return mix(*voices, gains=[0.9 / len(intervals) ** 0.5] * len(intervals))


def bank(slices, slice_dur):
    """Concatenate exactly 16 equal-length slots -> one PO-33 drum slot."""
    assert len(slices) == 16, "a drum slot slices into exactly 16"
    n = int(slice_dur * SR)
    out = []
    for s in slices:
        out.extend(fade(pad_to(s, n), ms_in=1.5, ms_out=6.0))
    return out


# ============================================================================
# THE PACK
# ============================================================================

def build():
    made = []

    # ---- MELODIC SLOTS (keys 1-8): one sound each, played chromatically -----
    # Long-ish and sustained, because these are the ones you pitch-shift.

    made.append(write_wav('01_chord_major.wav',   chord('C4', [0, 4, 7],      1.6)))
    made.append(write_wav('02_chord_minor.wav',   chord('C4', [0, 3, 7],      1.6)))
    made.append(write_wav('03_chord_maj7.wav',    chord('C4', [0, 4, 7, 11],  1.6)))
    made.append(write_wav('04_chord_min7.wav',    chord('C4', [0, 3, 7, 10],  1.6)))

    # square lead: 25% duty, vibrato arriving late so it sounds played
    made.append(write_wav('05_lead_square_25.wav',
        tone(freq('C4'), 1.4, 'pulse', duty=0.25, macro=[15,15,14,14,13,13],
             speed=4, vib=22, vib_rate=5.2, vib_delay=0.35)))

    # wave-channel style: 4-bit stepped triangle, soft and round
    made.append(write_wav('06_wave_triangle.wav',
        tone(freq('C3'), 1.4, 'triangle', macro=PAD, speed=4)))

    # PWM pad: duty breathing 12.5% -> 50% and back
    made.append(write_wav('07_pad_pwm.wav',
        mix(tone(freq('C4'), 1.6, 'pulse', macro=PAD, speed=4,
                 duty_sweep=(0.12, 0.5, 0.45), detune=-5),
            tone(freq('C4'), 1.6, 'pulse', macro=PAD, speed=4,
                 duty_sweep=(0.5, 0.12, 0.45), detune=+5), gains=[0.5, 0.5])))

    # sub bass: 50% duty, flat, tight tail
    made.append(write_wav('08_bass_sub.wav',
        tone(freq('C2'), 1.2, 'pulse', duty=0.5, macro=[15,15,15,15,14,13,11,8,5,2,0], speed=5)))

    # ---- DRUM SLOTS (keys 9-16): 16 equal slices = 16 playable sounds -------

    # 09  chromatic staccato, bright (25% duty), C4 -> D#5
    made.append(write_wav('09_stab_bright_C4.wav', bank(
        [tone(freq('C4') * 2 ** (s / 12.0), 0.12, 'pulse', duty=0.25, macro=STAB, speed=1)
         for s in range(16)], 0.17)))

    # 10  chromatic staccato, fat (50% duty), C3 -> D#4
    made.append(write_wav('10_stab_fat_C3.wav', bank(
        [tone(freq('C3') * 2 ** (s / 12.0), 0.12, 'pulse', duty=0.5, macro=STAB, speed=1)
         for s in range(16)], 0.17)))

    # 11  arpeggio bank: 8 major then 8 minor, on roots that cover a key
    roots = ['C3', 'D3', 'E3', 'F3', 'G3', 'A3', 'A#3', 'D#3']
    arps = []
    for r in roots:
        arps.append(tone(freq(r), 0.17, 'pulse', duty=0.25, macro=[15,15,14,13,11,9,7,5,3,1,0],
                         speed=1, arp=[0, 4, 7]))
    for r in roots:
        arps.append(tone(freq(r), 0.17, 'pulse', duty=0.25, macro=[15,15,14,13,11,9,7,5,3,1,0],
                         speed=1, arp=[0, 3, 7]))
    made.append(write_wav('11_arps_maj_min.wav', bank(arps, 0.22)))

    # 12  chip drum kit
    kit = [
        # kick: pitch drop + noise thump
        mix(tone(220, 0.13, 'pulse', duty=0.5, macro=CLICK, slide_to=42),
            lowpass(noise(0.06, macro=CLICK, period=90), 300), gains=[0.9, 0.35]),
        tone(200, 0.10, 'pulse', duty=0.5, macro=[15, 9, 4, 0], slide_to=45),
        # snares
        mix(noise(0.16, macro=[15,12,9,6,4,2,1,0], period=24),
            tone(190, 0.09, 'pulse', duty=0.5, macro=CLICK), gains=[0.75, 0.4]),
        mix(noise(0.13, macro=[15,11,7,4,2,0], period=14),
            tone(240, 0.07, 'pulse', duty=0.25, macro=CLICK), gains=[0.8, 0.3]),
        noise(0.04, macro=[13, 5, 0], period=8),                    # closed hat
        noise(0.16, macro=[12,10,8,6,4,3,2,1,0], period=8),         # open hat
        mix(noise(0.03, macro=[15, 0], period=12),                  # clap: 3 bursts
            pad_to(noise(0.03, macro=[15, 0], period=12), int(0.02 * SR)) +
            noise(0.09, macro=[15,10,6,3,1,0], period=12), gains=[0.6, 0.9]),
        mix(noise(0.02, macro=[15, 0], period=6),
            tone(900, 0.02, 'pulse', duty=0.125, macro=[15, 0]), gains=[0.5, 0.5]),  # rim
        tone(160, 0.16, 'pulse', duty=0.5, macro=LONGDECAY, speed=1, slide_to=80),   # tom lo
        tone(220, 0.14, 'pulse', duty=0.5, macro=LONGDECAY, speed=1, slide_to=120),  # tom mid
        tone(300, 0.12, 'pulse', duty=0.5, macro=LONGDECAY, speed=1, slide_to=170),  # tom hi
        noise(0.17, macro=[13,12,10,8,6,4,2,0], speed=2, period=5),     # cymbal
        mix(tone(540, 0.10, 'pulse', duty=0.5, macro=STAB),                          # cowbell
            tone(800, 0.10, 'pulse', duty=0.5, macro=STAB), gains=[0.5, 0.5]),
        noise(0.05, macro=[8, 4, 2, 0], period=6),                                   # shaker
        tone(1200, 0.06, 'pulse', duty=0.125, macro=CLICK, slide_to=200),            # zap perc
        noise(0.13, macro=[4, 8, 12, 15, 8, 2, 0], period=10),                       # reverse-ish
    ]
    made.append(write_wav('12_drumkit.wav', bank(kit, 0.19)))

    # 13  SFX and blips
    sfx = [
        tone(freq('B5'), 0.09, 'pulse', duty=0.5, macro=STAB, arp=[0, 5], arp_speed=3),   # coin
        tone(freq('C4'), 0.16, 'pulse', duty=0.25, macro=STAB, arp=[0, 4, 7, 12], arp_speed=1),  # powerup
        tone(1400, 0.12, 'pulse', duty=0.25, macro=PLUCK, slide_to=180),                  # laser
        tone(220, 0.11, 'pulse', duty=0.5, macro=STAB, slide_to=880),                     # jump
        mix(lowpass(noise(0.18, macro=LONGDECAY, speed=1, period=40, pitch_drop=3.0), 2200),
            tone(90, 0.16, 'pulse', duty=0.5, macro=PLUCK, slide_to=40), gains=[0.8, 0.5]),# explosion
        tone(freq('E5'), 0.05, 'pulse', duty=0.125, macro=CLICK),                         # blip
        tone(freq('A4'), 0.16, 'pulse', duty=0.5, macro=[15,15,15,14,12,9,5,0], arp=[0, 7], arp_speed=4),# alarm
        tone(900, 0.10, 'pulse', duty=0.5, macro=PLUCK, slide_to=120),                    # zap down
        tone(freq('G5'), 0.05, 'pulse', duty=0.25, macro=CLICK),                          # select
        mix(tone(70, 0.14, 'pulse', duty=0.5, macro=STAB),
            noise(0.14, macro=STAB, period=60), gains=[0.7, 0.4]),                        # error
        tone(200, 0.18, 'pulse', duty=0.25, macro=[10,13,15,15,13,9,5,2,0], slide_to=1600),  # warp
        mix(tone(120, 0.12, 'pulse', duty=0.5, macro=CLICK, slide_to=60),
            noise(0.10, macro=CLICK, period=20), gains=[0.7, 0.5]),                       # impact
        tone(300, 0.07, 'pulse', duty=0.125, macro=STAB, slide_to=900),                   # bubble
        tone(freq('C4'), 0.14, 'pulse', duty=0.125, macro=PLUCK, arp=[0, 7, 12, 19], arp_speed=1),  # teleport
        tone(freq('C5'), 0.18, 'pulse', duty=0.25, macro=LONGDECAY, speed=1, slide_to=freq('C3')),  # fall
        mix(tone(freq('C6'), 0.18, 'triangle', macro=LONGDECAY, speed=1),
            tone(freq('G6'), 0.18, 'triangle', macro=LONGDECAY, speed=1), gains=[0.6, 0.4]),        # chime
    ]
    made.append(write_wav('13_sfx.wav', bank(sfx, 0.22)))

    # ---- OPTIONAL EXTRAS (drum slots 14-15). Skip these to keep more memory
    # free for your own sampling; slot 16 is deliberately left open.

    # 14  chromatic bass bank, C2 -> D#3: basslines without spending a melodic slot
    made.append(write_wav('14_bass_bank_C2.wav', bank(
        [tone(freq('C2') * 2 ** (s / 12.0), 0.15, 'pulse', duty=0.5,
              macro=[15,15,15,14,13,11,9,7,4,2,0], speed=1)
         for s in range(16)], 0.20)))

    # 15  chord stabs, 8 major then 8 minor on the arp bank's roots
    stabs = []
    for iv in ([0, 4, 7], [0, 3, 7]):
        for r in roots:
            stabs.append(chord(r, iv, 0.18, duty=0.25, macro=STAB, speed=1, spread=8.0))
    made.append(write_wav('15_chord_stabs.wav', bank(stabs, 0.22)))

    total = sum(d for _, d in made)
    print(f"{'file':<26} {'seconds':>8}")
    print('-' * 36)
    for path, d in made:
        print(f"{os.path.basename(path):<26} {d:>8.2f}")
    print('-' * 36)
    core = sum(d for p, d in made if not os.path.basename(p).startswith(('14_', '15_')))
    print(f"{'CORE (files 01-13)':<26} {core:>8.2f}")
    print(f"{'+ optional (14-15)':<26} {total:>8.2f}")
    print()
    print("PO-33 memory is 40 s total (per Teenage Engineering's guide).")
    print(f"  core pack leaves {40 - core:.1f} s free")
    print(f"  full pack leaves {40 - total:.1f} s free")


if __name__ == '__main__':
    build()
