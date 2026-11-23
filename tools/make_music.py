#!/usr/bin/env python3
"""Generate an ORIGINAL 24 s tune for the post-x video (pure Python, no
samples, nothing copied). C major pentatonic, 126 BPM: a bright pluck
melody over a soft triangle bass and a light hat. Written for this video,
never used anywhere else.

Usage: python3 tools/make_music.py  ->  tools/music.wav (24.0 s, 44.1 kHz mono)
"""
import math
import struct
import wave

SR = 44100
DUR = 24.0
BPM = 126
BEAT = 60.0 / BPM

# C major pentatonic pluck melody (one note per 8th note), 16 bars of 2 beats
# each bar: 4 eighth notes. Notes as (midi, length_in_beats).
MELODY = [
    # bar 1-2: rising motif
    72, 76, 79, 76,  72, 76, 79, 84,
    # bar 3-4: answer
    79, 76, 72, 76,  67, 72, 76, 72,
    # bar 5-6: lift
    72, 76, 79, 81,  79, 76, 72, 76,
    # bar 7-8: resolve
    84, 79, 76, 72,  67, 0, 72, 0,
    # bar 9-10: repeat motif higher
    76, 79, 84, 79,  76, 79, 84, 88,
    # bar 11-12: answer
    84, 79, 76, 79,  72, 76, 79, 76,
    # bar 13-14: lift
    76, 79, 81, 84,  83, 81, 79, 76,
    # bar 15-16: final resolve
    79, 76, 72, 76,  72, 0, 0, 0,
]
# bass: one note per bar (2 beats each), C - F - G - C progression
BASS = [48, 48, 41, 43, 48, 48, 41, 43, 48, 48, 41, 43, 48, 43, 41, 48]


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def pluck(freq, t, dur):
    # sine + 2nd harmonic, fast attack, exponential decay
    if t >= dur:
        return 0.0
    env = math.exp(-4.0 * t / dur)
    return (math.sin(2 * math.pi * freq * t) + 0.35 * math.sin(2 * math.pi * freq * 2 * t)) * env


def bass_note(freq, t, dur):
    if t >= dur:
        return 0.0
    # triangle-ish: sine + soft 3rd harmonic, slow decay
    env = min(1.0, t / 0.02) * math.exp(-1.2 * t / dur)
    return (math.sin(2 * math.pi * freq * t) + 0.2 * math.sin(2 * math.pi * freq * 3 * t)) * env


def hat(t):
    # tiny noise tick at the start of each beat (deterministic pseudo-noise)
    if t < 0.03:
        x = math.sin(t * 9000.0) * math.sin(t * 13000.0)
        return x * (1.0 - t / 0.03) * 0.25
    return 0.0


def main():
    n = int(SR * DUR)
    out = [0.0] * n
    eighth = BEAT / 2.0
    # melody
    for i, m in enumerate(MELODY):
        if m == 0:
            continue
        start = int(i * eighth * SR)
        dur = eighth * 0.95
        freq = midi_to_freq(m)
        for j in range(int(dur * SR)):
            idx = start + j
            if idx >= n:
                break
            out[idx] += 0.5 * pluck(freq, j / SR, dur)
    # bass (one note per 2 beats = 4 eighths)
    for b, m in enumerate(BASS):
        start = int(b * 4 * eighth * SR)
        dur = 4 * eighth * 0.95
        freq = midi_to_freq(m)
        for j in range(int(dur * SR)):
            idx = start + j
            if idx >= n:
                break
            out[idx] += 0.45 * bass_note(freq, j / SR, dur)
    # hats on each beat
    n_beats = int(DUR / BEAT)
    for b in range(n_beats):
        start = int(b * BEAT * SR)
        for j in range(int(0.03 * SR)):
            idx = start + j
            if idx >= n:
                break
            out[idx] += hat(j / SR)
    # fade in/out
    fade = int(0.5 * SR)
    for i in range(fade):
        out[i] *= i / fade
        out[n - 1 - i] *= i / fade
    # normalize and write
    peak = max(abs(v) for v in out) or 1.0
    scale = 0.85 / peak
    with wave.open("tools/music.wav", "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v * scale)) * 32767)) for v in out)
        w.writeframes(frames)
    print("wrote tools/music.wav: %.1f s, %d samples" % (DUR, n))


if __name__ == "__main__":
    main()
