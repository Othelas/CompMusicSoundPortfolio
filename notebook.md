#### Jesse M. Ellis

#### Engineering Notebook - PSU Fall Term 2024

---

### 10-08-2024

Created CompMusicSoundPortfolio repository.

### 10-13-2024

**HW1 Clipped:** Using python, scipy.io.wav and numpy to generate and directly play a clipped sin wave.

Setup:

`sudo apt update`
`sudo apt install audacity`
`pip install numpy`
`pip install scipy`
`pip install sounddevice`

Initially pushed clipped.py: Generates and saves a simple sine wav similar to what we did in class.

### 10-15-2024

**Side quest:** Completed introduction in Zulip.

**HW1 Cont.**
Refactored clipped.py to define function:

`create_sine_wave(sample_rate, frequency, duration, amplitude)`.

We can now call this function to generate our sine wave with the desired attributes and then manipulate that wave.

**Useful docs**

- [numpy.linspace](https://numpy.org/doc/stable/reference/generated/numpy.linspace.html)
- [numpy.sin](https://numpy.org/doc/stable/reference/generated/numpy.sin.html)
- [numpy.clip](https://numpy.org/doc/stable/reference/generated/numpy.clip.html)

For the clipped wave I created the sine wave using our defined function and then used np.clip(), a function from the numpy library that clips the values in an array to a specified range.

For the homework we created a half-amplitude sine wave, values in the range -16384 and 16384 for signed 16 bit audio. We can use `np.clip(sine_wave_half_amplitude, -8192, 8192)` to clip our sinewave at -8192 and 8192.

### 10-17-2024

**HW1 Cont.**

Using `sounddevice` we can play the clipped waveform directly to our machines audio ouput.

**Useful Docs**

- [sounddevice.play()](https://python-sounddevice.readthedocs.io/en/0.5.1/api/convenience-functions.html#sounddevice.play)

- [sounddevice.wait()](https://python-sounddevice.readthedocs.io/en/0.5.1/api/convenience-functions.html#sounddevice.wait)

**Note**

If you don’t specify the correct sampling rate to `sounddevice.play()` (either with the samplerate argument or by assigning a value to default.samplerate), the audio data will be played back, but it might be too slow or too fast!
