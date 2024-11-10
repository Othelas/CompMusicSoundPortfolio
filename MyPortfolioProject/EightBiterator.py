import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import time


"""
Jesse M. Ellis - EightBiterator

A retro game music generator - (work in progress)
"""

# define settings for  8-bit sound
SAMPLE_RATE = 16000  # lower sample rate for retro sound (16 kHz)
DURATION = 1.0       # duration of each note in seconds

# Keys
C_MAJOR = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
C_SHARP_MAJOR = [277.18, 311.13, 349.23, 369.99, 415.30, 466.16, 523.25, 554.37]
D_MAJOR = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37, 587.33]
E_FLAT_MAJOR = [311.13, 349.23, 392.00, 415.30, 466.16, 523.25, 587.33, 622.25]
E_MAJOR = [329.63, 369.99, 415.30, 440.00, 493.88, 554.37, 622.25, 659.26]
F_MAJOR = [349.23, 392.00, 440.00, 466.16, 523.25, 587.33, 659.26, 698.46]
F_SHARP_MAJOR = [369.99, 415.30, 466.16, 493.88, 554.37, 622.25, 698.46, 739.99]
G_MAJOR = [392.00, 440.00, 493.88, 523.25, 587.33, 659.26, 739.99, 783.99]
A_FLAT_MAJOR = [415.30, 466.16, 523.25, 554.37, 622.25, 698.46, 783.99, 830.61]
A_MAJOR = [440.00, 493.88, 554.37, 587.33, 659.26, 739.99, 830.61, 880.00]
B_FLAT_MAJOR = [466.16, 523.25, 587.33, 622.25, 698.46, 783.99, 880.00, 932.33]
B_MAJOR = [493.88, 554.37, 622.25, 659.26, 739.99, 830.61, 932.33, 987.77]

# Generate 8-bit square wave
def generate_wave(freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))
    
    # Convert to 8-bit integer range [0, 255]
    waveform = ((waveform + 1) * 127.5).astype(np.uint8)
    return waveform

def play_notes(key, duration, sample_rate):
    full_wave = np.array([], dtype=np.uint8)
    for note in key:
        wave = generate_wave(note, duration, sample_rate)
        full_wave = np.concatenate((full_wave, wave))
        sd.play(wave.astype(np.float32) / 255.0 * 2 - 1, samplerate=sample_rate)
        time.sleep(0.1)
        sd.wait()
    return full_wave

# Testing 
waveform = play_notes(E_MAJOR, DURATION, SAMPLE_RATE)
sd.wait()
write("e_major.wav", SAMPLE_RATE, waveform)
