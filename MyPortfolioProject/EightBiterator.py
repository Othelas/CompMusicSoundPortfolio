import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

"""
Jesse M. Ellis - EightBiterator

A retro game music generator - (work in progress)
"""

# define settings for  8-bit sound
SAMPLE_RATE = 16000  # lower sample rate for retro sound (16 kHz)
DURATION = 1.0       # duration of each note in seconds

# Generate 8-bit square wave
def generate_wave(freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))
    
    # Convert to 8-bit integer range [0, 255]
    waveform = ((waveform + 1) * 127.5).astype(np.uint8)
    return waveform

# Tessting 
frequency = 440
waveform = generate_wave(frequency, DURATION, SAMPLE_RATE)
sd.play(waveform.astype(np.float32) / 255.0 * 2 - 1, samplerate=SAMPLE_RATE)
sd.wait()
write("eightbit_sqwave.wav", SAMPLE_RATE, waveform)
