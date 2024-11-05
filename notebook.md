#### Jesse M. Ellis - Engineering Notebook - PSU Fall Term 2024

Note: Most recent items are first.

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
