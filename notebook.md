#### Jesse M. Ellis - Engineering Notebook

#### Computers, Music and Sound - PSU Fall Term 2024

###### Note: Most recent items are first.

---

### 11-21-2024

**Portfolio Project - Adding waves**

Ultimately we want to create two melodies and add them. First let's start with a straight add..

```
def add_waves(wave1, wave2):
    added_wave = wave1 + wave2
    return added_wave
```

This is resulting in a lot of clipping when notes from each waveform overlap.. we needs some way to adjust the waveform for this.

The reason this sounds crunchy is because we are adding to uint8 waves which can cause overflow. We can convert each to uint16 while we add and then normalize the waves once combined. The following has a little crunch still but is waayyyy better.

```
def add_waves(wave1, wave2):
    # convert waves to prevent overflow
    added_wave = wave1.astype(np.int16) + wave2.astype(np.int16)
    # Normalize to the 8-bit range [0, 255]
    min_val = added_wave.min()
    max_val = added_wave.max()
    normalized_wave = (added_wave - min_val) / (max_val - min_val) * 255
    return normalized_wave.astype(np.uint8)
```

**Portfolio Project - More params**

These are the hard ones.. **Style** and **Notes per Bar (npb)**. Let's figure out npb first.

To accomplish this we can create "rest" notes in place of "tonal" notes. Say if we have 16 beats in a bar and we want 8 notes per bar then our melody generator should generate 8 tonal notes and 8 rest notes.

How do we generate a rest note? We need to be able to add it to the final waveform so it should still be a waverform but what does a rest waveform look like?

**Rest Note** Easy enough... generate a zero frequency note

```
if freq == 0:
    return np.zeros(int(sample_rate * duration), dtype=np.uint8)
```

**npb** A little trickier but essentially we need to calculat ethe difference between the number of note per bar and the bar length to find the number of rests. Once we have this we create an array of length npb with notes from the key and add an array of 0 frequencies. Then randomize the total array.

```

* Edited: The last version was calculating the reversing the number of tonal notes and rests. This is the refactored method that does it right.

def generate_random_melody(key, length, npb):
    # Calculate tonal notes and rests and build note list
    rest_notes = length - npb
    # Randomize the rest of the tonal notes
    melody = [random.choice(key) for _ in range(npb - 1)]
    # shuffle in rest notes
    melody += [0] * rest_notes
    random.shuffle(melody)
    # insert root
    melody.insert(0, key[0])
    return melody
```

---

### 11-19-2024

**Portfolio Project - Melody Parameters**

We should give the user some parameters to choose when creating their melody.

- **key1**: Specify the key for the first melody.
  Our code is already set up for this. :thumbs_up:
- **key2**: Specify the key for the second melody.
  The second key should be selected to compliment the first. Or not if you want something discordent.
- **shift1**: Specify the octave shift for the first melody. Our app calculates key frequencies starting at C4 (middle C) chromatic scale.
  Shift the melody up or down octaves. e.g. -2 goes down two octaves. 3 goes up three octaves.
- **shift2**: Specify the octave shift for the second melody.
  It is nice to choose octaves that are spaced apart.
- **style1**: Specify the style of the first melody.
  For now I think we will do mountain, ascending, descending or random.
  - Mountain: Notes make their way up and then back down the scale.
  - Ascending: Notes make their way up the scale.
  - Descending: Notes make their way down the scale.
  - Random: Notes are randomized over the key scale.
- **style2**: Specify the style of the second melody.
  If we choose ascending for the first melody it might sound cool to choose descending for the second.
  **bar**: Number of beats in a bar.
  This will control the number of beats in one bar.
  E.g. bar = 16 will be a melody generated with 16 notes.
  If the melody is set to loop, the bar is what will be looped.
- **bpm**: Specify the number of beats per minute.
  This will control how fast the melody is played by setting the note length. All notes will be of the same length. Longer notes are created by repeating the same note over a number of beats.
- **npb1**: Specify the number of notes per bar for the first melody.
  How many notes should the melody have within the bar. Beats that do not have a note will use "blank note" that has a zero amplitude and frequncy.
- **npb2**: Specify the number of notes per bar for the second melody.
  We could specify a bass melody with a ow number of notes and treble melody with a lot of notes.
- **loops**: Specify the number of times the melody should loop.
  How many times would you like the melody to repeat?

---

### 11-14-2024

**Portfolio Project - Octave Shifter**

Let's give the user the ability to shift keys up or down by octaves. The difference between the current octave and the next is double (or half depending on direction) of the current octave.

E.g. A4 (440Hz) -> A5 (880Hz) -> A6(1760Hz) .. etc.

Our method to shift the octave can simply double or halve the input frequencies depening on wether the user wants to shift up or down.

```
def octave_shift(current_key, shift):
    # Get shift factor - 0 shift will return original key octave
    shift_factor = 2*abs(shift)
    shifted_key = []
    # Shift note frequencies up
    if shift > 0:
        for note in current_key:
            note *= shift_factor
            shifted_key += [note]
        return shifted_key
    # Shift note frequencies down
    elif shift < 0:
        for note in current_key:
            note /= shift_factor
            shifted_key += [note]
        return shifted_key
    return current_key
```

### 11-12-2024

**Portfolio Project - A better key generator**

At first I decided to hard code all major 4th octave keys and then use a method to find the relative minor to get minor keys. I am thinking a better way to do this would be to generate any major/minor key based n user input from the chromatic scale.

What is the chromatic scale? The chromatic scale consists of all 12 half and whole step notes from a given note. Let's start with middle C (C4) and end an octave higher. We'll define it as a list of (note, frequency) tuples so that we can associate note names with frequencies.

```
CHROMATIC_SCALE = [
    ('C4', 261.63),
    ('C#4/Db4', 277.18),
    ('D4', 293.66),
    ('D#4/Eb4', 311.13),
    ('E4', 329.63),
    ('F4', 349.23),
    ('F#4/Gb4', 369.99),
    ('G4', 392.00),
    ('G#4/Ab4', 415.30),
    ('A4', 440.00),
    ('A#4/Bb4', 466.16),
    ('B4', 493.88),
    ('C5', 523.25)
]

```

From this we can derive all major and minor keys by the step pattern. Let 2 (two notes up) be a whole step and 1 (one note up) be a half step. The final step gets to the next octave.

- Major Key Steps: [ 2, 2, 1, 2, 2, 2, 1 ]
- Minor Key Steps: [ 2, 1, 2, 2, 1, 2, 2 ]

**Example:** Find the Major and Minor keys in C4. Using the pattern and chromatic scale we get:

```
C_MAJOR = {
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25
}

C_MINOR = {
    'C4': 261.63, 'D4': 293.66, 'Eb4': 311.13, 'F4': 349.23,
    'G4': 392.00, 'Ab4': 415.30, 'Bb4': 466.16, 'C5': 523.25
}

```

Now we need a method to get the key based on an input string key name.
(see EightBiterator.py -> generate_scale() )

---

### 11-11-2024

**Portfolio Project - Random Melody**

Given an input key and the number of notes lets create a meldoy from random notes in the key.

```
def generate_random_melody(key, length):
    return [random.choice(key) for _ in range(length)]
```

**Portfolio Project - Relative Minor**

Rather than list out all the frequencies for the minor keys we'll use a mthod to calculate the relative minor to each major. The relative minor to each major starts at the 6th note of the major scale and then ascends to the next notes through the key. sort of like shifting the list of notes such that the 6th note is now at the beginning of the list and the rest have looped around to keep the same sequence.

e.g. A minor (A4,B4,C5,D5,E5,F5,G5) is relative to C major (C4,D4,E4,F4,G4,A4,B4).

To keep the notes ascending we will copy the major notes starting with the 6th and 7th then we will append that list with notes 1 to 5 but double the frequencies such that they are an octave higher.

```
def relative_minor_scale(major_scale):
    # The relative minor starts from the 6th note of the major scale
    minor_start_index = 5
    # Generate the relative minor scale by shifting notes
    minor_scale = major_scale[minor_start_index:] + [freq * 2 for freq in major_scale[:minor_start_index]]
    return minor_scale
```

---

### 11-10-2024

**Portfolio Project - Note Keys**

The user should be able to choose what key to generate melodies in. We'll define all fourth octave major keys and then we can move octaves as needed. We can also use the relative minor of each key, e.g. the relative minor of C major (c,d,e,f,g,a,b) is A minor (a,b,c,d,e,f,g).

**Key Definitions**

- C_MAJOR = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
- C_SHARP_MAJOR = [277.18, 311.13, 349.23, 369.99, 415.30, 466.16, 523.25, 554.37]
- D_MAJOR = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33]
- E_FLAT_MAJOR = [311.13, 349.23, 392.00, 415.30, 466.16, 523.25, 587.33, 622.25]
- E_MAJOR = [329.63, 369.99, 415.30, 440.00, 493.88, 554.37, 622.25, 659.26]
- F_MAJOR = [349.23, 392.00, 440.00, 466.16, 523.25, 587.33, 659.26, 698.46]
- F_SHARP_MAJOR = [369.99, 415.30, 466.16, 493.88, 554.37, 622.25, 698.46, 739.99]
- G_MAJOR = [392.00, 440.00, 493.88, 523.25, 587.33, 659.26, 739.99, 783.99]
- A_FLAT_MAJOR = [415.30, 466.16, 523.25, 554.37, 622.25, 698.46, 783.99, 830.61]
- A_MAJOR = [440.00, 493.88, 554.37, 587.33, 659.26, 739.99, 830.61, 880.00]
- B_FLAT_MAJOR = [466.16, 523.25, 587.33, 622.25, 698.46, 783.99, 880.00, 932.33]
- B_MAJOR = [493.88, 554.37, 622.25, 659.26, 739.99, 830.61, 932.33, 987.77]

**Playing Melodies**

Ultimately we want to play melodies so we should figure out how to play a sequence of notes and add the to the whole output waveform. To start we'll use an array of note fequency values in the Key of C major (middle C).

Key of C major: C D E F G A B C

C_MAJOR = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88 ,523.25]

```
def play_notes(key, duration, sample_rate):
    full_wave = np.array([], dtype=np.uint8)
    for note in key:
        wave = generate_wave(note, duration, sample_rate)
        full_wave = np.concatenate((full_wave, wave))
        sd.play(wave.astype(np.float32) / 255.0 * 2 - 1, samplerate=sample_rate)
        time.sleep(0.1)
        sd.wait()
    return full_wave
```

---

### 11-07-2924

**Portfolio Project - Create a square wave.**

**What?**
We need an 8-bit square wave to create the retro sound of classic game systems.

**How?**
An 8-bit wave carries integer values from 0-255. To simulate the sound of an old system we will use a lower samplel rate, 16k samples per second.

```
import numpy as np
import sounddevice as sd

# define settings for 8-bit sound
SAMPLE_RATE = 16000  # lower sample rate for retro sound (16 kHz)
DURATION = 0.25      # duration of each note in seconds

# Generate a square wave for 8-bit sound
def generate_wave(freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))

    # Convert to 8-bit integer range [0, 255]
    waveform = ((waveform + 1) * 127.5).astype(np.uint8)
    return waveform

```

---

### 11-05-2024

**Portfolio Project Ideation**

Castlevania style melody generator! Using 8-bit style synthesizer (aka Chiptune) code, create an application that generates Castlevania style melodies.

**Theory(?)**

Most retro Castlevania game music uses a musical concept called counter-point melodies. This is very common in Bach, as a classical example, and in fact some Castlevania songs are directly based off Bach compositions.

A very simple explanation of counter-point for our context is to create two melodies in the same key or the same chord and in the same time signature. Then those two melodies are combined to pla over the top of one another.

**Possible inputs:**

- **Key** (melody A, melody B)
- **Chord** (melody A, melody B)
- **Melody Type** (melody A, melody B)

  - ascending, descending, undulating, pendulum, tile, terrace, or cascading.

- **Melody Style** (melody A, melody B)

  - Monotone: A flat melody with one or two notes
  - Legato: Sustained notes that transition smoothly
  - Staccato: Notes that are not sustained and have sudden stops
  - Jumping: Lines with large note gaps
  - Casual: Lines that are sung lazily, slightly off, or with an essence of speaking
  - Call and response: Common in duets or for creating echo effects
  - Chord-based: Melodies based on chord tones
  - Scale-based: Melodies made up of notes within a particular scale or mode
  - Direction: Melodies that don't come back to the same pitch over and over again

---

### 11-02-2024

**HW2 Adaptive Tone Control**

Reference:

- [scipy.fft](https://docs.scipy.org/doc/scipy/tutorial/fft.html)
- [scipy.ifft](https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.ifft.html)

High level solution design:

1. Read an input audio waveform.
2. Use an FFT to measure the sound energy and frequency components of the waveform.
3. Adjust the energy in each band using filters.
4. Reconstruct adjusted waveform.
5. Save and play the tone controlled output waveform

Define fequency bands to filter:

- Low band: 0-300Hz
- Mid band: 300Hz-2000Hz
- High band: 2000Hz +

For this tone control I have extracted the frequencies across the above bands and calculated the average energy across each band.
I then calculate the average anergy across all bands.

For the gain I intially calculated as such,

```
    low_gain = average_energy / (low_energy + 1e-10)
    mid_gain = average_energy / (mid_energy + 1e-10)
    high_gain = average_energy / (high_energy + 1e-10)
```

This created too low gain for the low band and too high gain hor the high band resulting in tones being adjusted to the extremes rather than "normalizing". To fix this I simply switched the `low_energy` and `high_energy` values as such.

```
    low_gain = average_energy / (high_energy + 1e-10)
    mid_gain = average_energy / (mid_energy + 1e-10)
    high_gain = average_energy / (low_energy + 1e-10)
```

This effectively brings the low band up and the high band down "normalizing" the tone.

**Note on reconstructing the waveform**
I tried a few differeent methods to reconstruct the waveform and ran into quite a few problems. The closest method I tried was by reconstructing the waveform by adding the real component of the adjusted waveform. This resulted in errors with saving the wav file as it was producing mono and expecting stereo.

```

...FFT and gain calculations happen... and then reconstruction:

    adjusted_fft = fft_result.copy()
    adjusted_fft[(frequencies >= 0) & (frequencies < 300)] *= low_gain
    adjusted_fft[(frequencies >= 300) & (frequencies < 2000)] *= mid_gain
    adjusted_fft[(frequencies >= 2000)] *= high_gain

    # reconstruct waveform
    adjusted_waveform = np.sum(
        [np.real(component) for component in adjusted_fft]
    )

    # normalize range
    adjusted_waveform /= np.max(np.abs(adjusted_waveform) + 1e-10)

    return adjusted_waveform.astype(np.float32)
```

Rather than continue to fight with manually reconstructing the waveform I opted to explore the iFFT. This solution worked out of the box so I stuck with it.

```
...Create adjusted_fft as above...

    # Reconstruct waveform with adjusted fft
    adjusted_wav = np.real(ifft(adjusted_fft))
    adjusted_wav /= np.max(np.abs(adjusted_wav) + 1e-10)

    return adjusted_wav.astype(np.float32)
```

**Next steps**
As it is this code reduces the over all volume of the waveform and creates a "far away" sound. Need to add some other parameters to the wave reconstruction such as frequency/energy thresholds and/or filters to get rid of clipping.

---

### 10-17-2024

**HW1 Cont.** - [HW1 Clipped](https://github.com/Othelas/CompMusicSoundPortfolio/tree/main/HW1_Clipped)

Using `sounddevice` we can play the clipped waveform directly to our machines audio ouput.

**Useful Docs**

- [sounddevice.play()](https://python-sounddevice.readthedocs.io/en/0.5.1/api/convenience-functions.html#sounddevice.play)

- [sounddevice.wait()](https://python-sounddevice.readthedocs.io/en/0.5.1/api/convenience-functions.html#sounddevice.wait)

**Note**

If you don’t specify the correct sampling rate to `sounddevice.play()` (either with the samplerate argument or by assigning a value to default.samplerate), the audio data will be played back, but it might be too slow or too fast!

---

### 10-15-2024

**Side quest:** Completed introduction in Zulip.

**HW1 Cont.** - [HW1 Clipped](https://github.com/Othelas/CompMusicSoundPortfolio/tree/main/HW1_Clipped)

Refactored clipped.py to define function:

`create_sine_wave(sample_rate, frequency, duration, amplitude)`.

We can now call this function to generate our sine wave with the desired attributes and then manipulate that wave.

**Useful docs**

- [numpy.linspace](https://numpy.org/doc/stable/reference/generated/numpy.linspace.html)
- [numpy.sin](https://numpy.org/doc/stable/reference/generated/numpy.sin.html)
- [numpy.clip](https://numpy.org/doc/stable/reference/generated/numpy.clip.html)

For the clipped wave I created the sine wave using our defined function and then used np.clip(), a function from the numpy library that clips the values in an array to a specified range.

For the homework we created a half-amplitude sine wave, values in the range -16384 and 16384 for signed 16 bit audio. We can use `np.clip(sine_wave_half_amplitude, -8192, 8192)` to clip our sinewave at -8192 and 8192.

---

### 10-13-2024

**HW1 Clipped:** Using python, scipy.io.wav and numpy to generate and directly play a clipped sin wave. - [HW1 Clipped](https://github.com/Othelas/CompMusicSoundPortfolio/tree/main/HW1_Clipped)

Setup:

`sudo apt update`
`sudo apt install audacity`
`pip install numpy`
`pip install scipy`
`pip install sounddevice`

Initially pushed clipped.py: Generates and saves a simple sine wav similar to what we did in class.

---

### 10-08-2024

Created CompMusicSoundPortfolio repository.
