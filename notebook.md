#### Jesse M. Ellis - Engineering Notebook

#### Computers, Music and Sound - PSU Fall Term 2024

###### Note: Most recent items are first.

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
