### EightBiterator - Retro 8-bit Melody Generator

**Overview**
The EightBiterator is a Python-based retro melody generator that creates 8-bit-style music samples inspired by classic video game soundtracks. It allows you to customize and generate melodies with various styles, keys, chords, and other attributes. These melodies can be played back and saved as .wav files..

**Features**

- Supports custom keys (major and minor) for melody generation.
- Offers various melody styles: `random`, `linear`, `ascending`, `descending`, and `mountain`.
- Enables octave shifting and chord-based melodies.
- Combines two distinct melodies for a unique composition.
- Low-pass filter for retro-style smoothing.
- Save melodies and their attributes for future use.

**Usage Example**

Generate melody with default settings

- `python eightbiterator.py`

Generate melody with custom settings

- `python eightbiterator.py --key1 C#m --style1 ascending --key2 G --style2 descending --shift1 1 --loops 3 --smooth1 true
`

**Arguments**
| Argument | Type | Default | Description |
|-----------|--------|-----------|---------------|
|-h, --help | | |Show help message and exit.
|--key1 | string | G#m | Key for melody 1.
|--key2 | string | G#m | Key for melody 2.
|--chord1 | bool | True | Set True for chord melody 1.
|--chord2 | bool | False | Set True for chord melody 2.
|--style1 | string | mountain | styles: random, linear, ascending, descending, mountain.
|--style2 |string |random | Choose melody style as above.
|--shift1 | int | 0 | Octave shift up or down for melody 1.
|--shift2 | int | -3 | Octave shift up or down for melody 2.
|--bpm | int | 200 | Beats per minute.
|--bar | int | 16 | Number of beats in a bar.
|--loops | int | 3 | Number of times the bar should loop.
|--npb1 | int | 12 | Notes per bar for melody 1.
|--npb2 | int | 8 | Notes per bar for melody 2.
|--smooth1 | bool | False | Set True for a smooth sound on melody 1.
|--smooth2 | bool | False | Set True for a smooth sound on melody 2.
|--double1 | bool | True | Set True to play melody 1 in double time.
|--double2 | bool | False | Set True to play melody 2 in double time.

**Valid Key Inputs:**

```
"C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#",
"Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B", "Cm",
"C#m", "Dbm", "Dm", "D#m", "Ebm", "Em", "Fm", "F#m",
"Gbm", "Gm", "G#m", "Abm", "Am", "A#m", "Bbm", "Bm"
```

**How to Use**

1. Run the script:
   - Use the provided command-line arguments to specify your melody's attributes or stick to defaults.
2. Listen and interact: - After generation, the melody will play.
   You will be prompted to save (Y), replay (R), or discard (N) the melody.
3. Save your melody:
   - If saved, a .wav file and an associated \_attributes.txt file will be created in the working directory.

**Notes**

- The --key1 and --key2 arguments support major (C) and minor (Cm) scales.
- The --style options dictate how notes are ordered:
  - random: Random selection.
  - linear: Root note appears frequently.
  - ascending/descending: Progressively moves up/down the scale.
  - mountain: Ascends, then descends.
- Set --smooth for a more polished tone or leave it off for retro-style chiptune sounds.

**Dependencies**

- Python 3.8+
- Required Libraries:
  - numpy
  - scipy
  - sounddevice

**Install the dependencies using:** `pip install numpy scipy sounddevice
`

**Credits**

Developed by Jesse M. Ellis as part of Computers, Music, and Sound coursework at PSU, Fall 2024.
