import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import time
import random
from datetime import datetime
import math

"""
Jesse M. Ellis - EightBiterator

A retro game music generator - (work in progress)
"""

# define settings for  8-bit sound
SAMPLE_RATE = 16000  # lower sample rate for retro sound (16 kHz)
BPM = 120       # duration of each note in seconds
BAR = 8
SHIFT1 = 0
SHIFT2 = -3
KEY1 = "gsharp_minor"
KEY2 = "gsharp_minor"
LOOPS = 4
NPB1 = 7
NPB2 = 4

# Chromatic scale from C4 - we will generate keys from this.
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
    ('B4', 493.88)
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
        if root_note in note:
            root_index = idx
            break
    
    # Generate the scale using the major or minor pattern
    scale_notes = []
    current_index = root_index
    root_frequency = CHROMATIC_SCALE[current_index][1]
    for step in pattern:
        # double frequency for notes beyond the original range (go to next octave)
        if (current_index == root_index):
            scale_notes.append(CHROMATIC_SCALE[current_index][1])
        else:
            if (root_frequency >= CHROMATIC_SCALE[current_index][1]):
                scale_notes.append(CHROMATIC_SCALE[current_index][1] * 2)
            else:
                scale_notes.append(CHROMATIC_SCALE[current_index][1]) 
                 
        current_index = (current_index + step) % len(CHROMATIC_SCALE)
        
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
            shifted_key += [math.trunc(note*100)/100]
        return shifted_key
    return current_key

def calculate_note_length(bpm):
    return 60/bpm

# Generate 8-bit square wave
def generate_wave(freq, duration, sample_rate):
    # rest note
    if freq == 0:
        return np.zeros(int(sample_rate * duration), dtype=np.uint8)
    # tonal note
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.2 * np.sign(np.sin(2 * np.pi * freq * t))
    
    # Convert to 8-bit integer range [0, 255]
    waveform = ((waveform + 1) * 127.5).astype(np.uint8)
    return waveform

def create_melody_waveform(key, duration, sample_rate, loops):
    full_wave = np.array([], dtype=np.uint8)
    for note in key:
        wave = generate_wave(note, duration, sample_rate)
        full_wave = np.concatenate((full_wave, wave))
        time.sleep(0.1)
    
    # repeat the melody over loops
    full_wave = np.tile(full_wave, loops)
    return full_wave

def play_wave(waveform, sample_rate):
    sd.play(waveform.astype(np.float32) / 255.0 * 2 - 1, samplerate=sample_rate)
    sd.wait()
    return


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

def add_waves(wave1, wave2):
    # convert waves to prevent overflow
    added_wave = wave1.astype(np.int16) + wave2.astype(np.int16)
    # Normalize to the 8-bit range [0, 255]
    min_val = added_wave.min()
    max_val = added_wave.max()
    normalized_wave = (added_wave - min_val) / (max_val - min_val) * 255
    return normalized_wave.astype(np.uint8)

def save_wave(key, shift, sample_rate, waveform):
    octave = str(4 + shift)
    date = str(datetime.now())
    file_name = key + octave + "_melody_" + date + ".wav"
    write(file_name, sample_rate, waveform)

# Validate that NPB is less than or equal to BAR
if NPB1 > BAR:
    raise ValueError(f"NPB (Notes Per Bar) cannot be greater than BAR. Got NPB={NPB1} and BAR={BAR}.")

if NPB2 > BAR:
    raise ValueError(f"NPB (Notes Per Bar) cannot be greater than BAR. Got NPB={NPB2} and BAR={BAR}.")

# Generate melody 1
key_scale1 = generate_scale(KEY1)
shifted_key_scale1 = octave_shift(key_scale1, SHIFT1)
melody1 = generate_random_melody(shifted_key_scale1, BAR, NPB1)
duration1 = calculate_note_length(BPM)
wave1 = create_melody_waveform(melody1, duration1, SAMPLE_RATE, LOOPS)
play_wave(wave1, SAMPLE_RATE)
sd.wait()

# Generate melody 2
key_scale2 = generate_scale(KEY2)
shifted_key_scale2 = octave_shift(key_scale2, SHIFT2)
melody2 = generate_random_melody(shifted_key_scale2, BAR, NPB2)
duration2 = calculate_note_length(BPM)
wave2 = create_melody_waveform(melody2, duration2, SAMPLE_RATE, LOOPS)
play_wave(wave2, SAMPLE_RATE)
sd.wait()

# Combine melodies
waveform = add_waves(wave1, wave2)
play_wave(waveform, SAMPLE_RATE)

# Save
save_wave(KEY1, SHIFT1, SAMPLE_RATE, waveform)



