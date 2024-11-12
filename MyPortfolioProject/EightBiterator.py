import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import time
import random

"""
Jesse M. Ellis - EightBiterator

A retro game music generator - (work in progress)
"""

# define settings for  8-bit sound
SAMPLE_RATE = 16000  # lower sample rate for retro sound (16 kHz)
DURATION = 0.5       # duration of each note in seconds

# Keys
C_MAJOR = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]
C_SHARP_MAJOR = [277.18, 311.13, 349.23, 369.99, 415.30, 466.16, 523.25]
D_MAJOR = [293.66, 329.63, 369.99, 392.00, 440.00, 493.88, 554.37]
E_FLAT_MAJOR = [311.13, 349.23, 392.00, 415.30, 466.16, 523.25, 587.33]
E_MAJOR = [329.63, 369.99, 415.30, 440.00, 493.88, 554.37, 622.25]
F_MAJOR = [349.23, 392.00, 440.00, 466.16, 523.25, 587.33, 659.26]
F_SHARP_MAJOR = [369.99, 415.30, 466.16, 493.88, 554.37, 622.25, 698.46]
G_MAJOR = [392.00, 440.00, 493.88, 523.25, 587.33, 659.26, 739.99]
A_FLAT_MAJOR = [415.30, 466.16, 523.25, 554.37, 622.25, 698.46, 783.99]
A_MAJOR = [440.00, 493.88, 554.37, 587.33, 659.26, 739.99, 830.61]
B_FLAT_MAJOR = [466.16, 523.25, 587.33, 622.25, 698.46, 783.99, 880.00]
B_MAJOR = [493.88, 554.37, 622.25, 659.26, 739.99, 830.61, 932.33]

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
        sd.wait()
        time.sleep(0.1)
    return full_wave

def generate_random_melody(key, length):
    # return melody note list starting with the first note in the list
    # this preserves the "tone" of the key.
    melody = [key[0]]
    # randomize the rest of the notes
    melody += [random.choice(key) for _ in range(length - 1)]
    return melody

def relative_minor_scale(major_scale):
    # The relative minor starts from the 6th note of the major scale
    minor_start_index = 5
    # generate the relative minor scale by shifting notes
    minor_scale = major_scale[minor_start_index:] + [freq * 2 for freq in major_scale[:minor_start_index]]
    return minor_scale

# Testing 
# A_MINOR = relative_minor_scale(C_MAJOR)
# melody = generate_random_melody(A_MINOR, 16)

melody = generate_random_melody(C_MAJOR, 16)

waveform = play_notes(melody, DURATION, SAMPLE_RATE)
sd.wait()
#write("a_minor_melody.wav", SAMPLE_RATE, waveform)
write("c_major_melody.wav", SAMPLE_RATE, waveform)

