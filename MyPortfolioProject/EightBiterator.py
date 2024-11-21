import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import time
import random
from datetime import datetime

"""
Jesse M. Ellis - EightBiterator

A retro game music generator - (work in progress)
"""

# define settings for  8-bit sound
SAMPLE_RATE = 16000  # lower sample rate for retro sound (16 kHz)
BPM = 60       # duration of each note in seconds
BAR = 4
SHIFT = 1
KEY = "c_major"
LOOPS = 4

# Chromatic scale - we will generate keys from this.
# Define the chromatic scale as a list of tuples in ascending order
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

# Define major and minor scale intervals (W = Whole, H = Half)
MAJOR_PATTERN = [2, 2, 1, 2, 2, 2, 1]
MINOR_PATTERN = [2, 1, 2, 2, 1, 2, 2]

# Method to generate a key based on string key name input, e.g. c_major, c_sharp_minor, b_flat_major
def generate_scale(key_name):
    # Is scale major or minor
    is_minor = 'minor' in key_name.lower()
    pattern = MINOR_PATTERN if is_minor else MAJOR_PATTERN
    
    # get the root note name
    root_note = key_name.split('_')[0].capitalize()
    if 'sharp' in root_note:
        root_note = root_note.replace('sharp', '#')
    elif 'flat' in root_note:
        root_note = root_note.replace('flat', 'b')
    
    # find the root note index in the chromatic scale
    root_index = None
    for idx, (note, _) in enumerate(CHROMATIC_SCALE):
        if note.startswith(root_note):
            root_index = idx
            break
    
    # Generate the scale using the major or minor pattern
    scale_notes = []
    current_index = root_index
    for step in pattern:
        scale_notes.append(CHROMATIC_SCALE[current_index][1])  # Add frequency to the list
        current_index = (current_index + step) % len(CHROMATIC_SCALE)
    
    # double frequency for notes beyond the original range (go to next octave)
    if current_index < root_index:
        scale_notes.append(CHROMATIC_SCALE[current_index][1] * 2)
    else:
        scale_notes.append(CHROMATIC_SCALE[current_index][1])
    
    return scale_notes

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

def calculate_note_length(bpm):
    return 60/bpm

# Generate 8-bit square wave
def generate_wave(freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))
    
    # Convert to 8-bit integer range [0, 255]
    waveform = ((waveform + 1) * 127.5).astype(np.uint8)
    return waveform

def play_notes(key, duration, sample_rate, loops):
    full_wave = np.array([], dtype=np.uint8)
    for note in key:
        wave = generate_wave(note, duration, sample_rate)
        full_wave = np.concatenate((full_wave, wave))
        # sd.play(wave.astype(np.float32) / 255.0 * 2 - 1, samplerate=sample_rate)
        # sd.wait()
        time.sleep(0.1)
    
    # repeat the melody over loops
    full_wave = np.tile(full_wave, loops)
    sd.play(full_wave.astype(np.float32) / 255.0 * 2 - 1, samplerate=sample_rate)
    sd.wait()
    return full_wave


def generate_random_melody(key, length):
    # return melody note list starting with the first note in the list
    # this preserves the "tone" of the key.
    melody = [key[0]]
    # randomize the rest of the notes
    melody += [random.choice(key) for _ in range(length - 1)]
    return melody

def save_wave(key, shift, sample_rate, waveform):
    octave = str(4 + shift)
    date = str(datetime.now())
    file_name = key + octave + "_melody_" + date + ".wav"
    write(file_name, sample_rate, waveform)

# Testing 
key_scale = generate_scale(KEY)
shifted_key_scale = octave_shift(key_scale, SHIFT)
melody = generate_random_melody(shifted_key_scale, BAR)
duration = calculate_note_length(BPM)
waveform = play_notes(melody, duration, SAMPLE_RATE, LOOPS)
sd.wait()
save_wave(KEY, SHIFT, SAMPLE_RATE, waveform)

