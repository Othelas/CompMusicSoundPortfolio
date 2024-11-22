import argparse
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import time
import random
from datetime import datetime
import math

"""
Jesse M. Ellis - EightBiterator

A retro game music melody generator.

Computers, Music and Sound - PSU FALL 2024
"""

SAMPLE_RATE = 16000

# valid keys
VALID_KEYS = {
    "C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", 
    "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B", "Cm", 
    "C#m", "Dbm", "Dm", "D#m", "Ebm", "Em", "Fm", "F#m", 
    "Gbm", "Gm", "G#m", "Abm", "Am", "A#m", "Bbm", "Bm"
}

# Chromatic scale from C4 - we will generate keys from this.
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

MAJOR_PATTERN = [2, 2, 1, 2, 2, 2, 1]
MINOR_PATTERN = [2, 1, 2, 2, 1, 2, 2]

def generate_scale(key_name):
    is_minor = key_name[-1].lower() == 'm'
    root_note = key_name[:-1] if is_minor else key_name

    pattern = MINOR_PATTERN if is_minor else MAJOR_PATTERN
    
    root_index = None
    for idx, (note, _) in enumerate(CHROMATIC_SCALE):
        if root_note in note:
            root_index = idx
            break
    
    scale_notes = []
    current_index = root_index
    root_frequency = CHROMATIC_SCALE[current_index][1]
    for step in pattern:
        if current_index == root_index:
            scale_notes.append(CHROMATIC_SCALE[current_index][1])
        else:
            if root_frequency >= CHROMATIC_SCALE[current_index][1]:
                scale_notes.append(CHROMATIC_SCALE[current_index][1] * 2)
            else:
                scale_notes.append(CHROMATIC_SCALE[current_index][1]) 
        current_index = (current_index + step) % len(CHROMATIC_SCALE)
    return scale_notes

def octave_shift(current_key, shift):
    shift_factor = 2 * abs(shift)
    shifted_key = []
    if shift > 0:
        for note in current_key:
            note *= shift_factor
            shifted_key.append(note)
    elif shift < 0:
        for note in current_key:
            note /= shift_factor
            shifted_key.append(math.trunc(note * 100) / 100)
    else:
        shifted_key = current_key
    return shifted_key

def calculate_note_length(bpm):
    return 60 / bpm

def generate_wave(freq, duration):
    if freq == 0:
        return np.zeros(int(SAMPLE_RATE * duration), dtype=np.uint8)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    waveform = 0.2 * np.sign(np.sin(2 * np.pi * freq * t))
    waveform = ((waveform + 1) * 127.5).astype(np.uint8)
    return waveform

def create_melody_waveform(key, duration, loops):
    full_wave = np.array([], dtype=np.uint8)
    for note in key:
        wave = generate_wave(note, duration)
        full_wave = np.concatenate((full_wave, wave))
        time.sleep(0.1)
    full_wave = np.tile(full_wave, loops)
    return full_wave

def play_wave(waveform):
    sd.play(waveform.astype(np.float32) / 255.0 * 2 - 1, samplerate=SAMPLE_RATE)
    sd.wait()

def generate_random_melody(key, length, npb):
    rest_notes = length - npb
    melody = [random.choice(key) for _ in range(npb - 1)]
    melody += [0] * rest_notes
    random.shuffle(melody)
    melody.insert(0, key[0])
    return melody

def add_waves(wave1, wave2):
    added_wave = wave1.astype(np.int16) + wave2.astype(np.int16)
    min_val, max_val = added_wave.min(), added_wave.max()
    normalized_wave = (added_wave - min_val) / (max_val - min_val) * 255
    return normalized_wave.astype(np.uint8)

def get_attributes(args):
    attributes = "\n".join([f"{key}: {value}" for key, value in vars(args).items()])
    return f"Attributes used in your melody:\n\n{attributes}"

def save_wave(attributes, waveform):
    # Prompt the user for a save stuff
    save_the_file = input("Is this a keeper? (Y/N) or (R)eplay: ").strip()
    if save_the_file.lower() == "y":
        # setup output files
        save_file = input("Enter a file name: ").strip()
        if not save_file.lower().endswith('.wav'):
            save_file += '.wav'
        attribute_file = save_file.rsplit(".wav", 1)[0] + "_attributes.txt"

        # Save the waveform and attributes 
        write(save_file, SAMPLE_RATE, waveform)
        print(f"Dope retro melody saved as: {save_file}")
        with open(attribute_file, "w") as file:
            file.write(attributes)
        print(f"Here's the attributes you used: {attribute_file}")
    elif save_the_file.lower() == "r":
        time.sleep(0.2)
        play_wave(waveform)
        save_wave(attributes, waveform)
    elif save_the_file.lower() == "n":
        save_chatter = random.randint(1,4)
        if save_chatter == 1:
            print("Yea that was trash.. :(")
        elif save_chatter == 2:
            print("I haven't practiced in a while. Let's go again!")
        elif save_chatter == 3:
            print("AY! OH! LET'S GO!  again..")
        elif save_chatter == 4:
            print("It was good-ish, but your call.")
    else:
        print("ummm... what?")
        save_wave(attributes, waveform)
    return

def clear_line_and_print(print_string):
    print("\033[A", end="")
    print("\033[K", end="")
    print(print_string)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
    """     Generate a retro game music counter-point melody sample! 
    Specify the attributes for two melodies.
    The EightBiterator will generate and add the two melodies 
    together to create your retro style game melody!

    NOTE on key input. 
    Input format is \"G#m\" as in G sharp minor, \"Bb\" as in B flat major, etc..
    If you only specify key1 then key2 will be the same hey.
    You can also try the default by not specifying any attributes ;)""" )
    parser.add_argument("--key1", type=str, default="G#m", help="Default: G#m | Key for melody 1.")
    parser.add_argument("--key2", help="Default: G#m | Key for melody 2.")
    parser.add_argument("--shift1", type=int, default=0, help="Default: 0 | Octave shift from middle (4) for melody 1.")
    parser.add_argument("--shift2", type=int, default=-3, help="Default: -3 | Octave shift from middle (4) for melody 2.")
    parser.add_argument("--bpm", type=int, default=240, help="Default: 240 | Beats per minute.")
    parser.add_argument("--bar", type=int, default=32, help="Default: 32 | Number of beats in a bar.")
    parser.add_argument("--loops", type=int, default=2, help="Default: 2 | Number of times the bar should loop.")
    parser.add_argument("--npb1", type=int, default=24, help="Default: 24 | Notes per bar for melody 1.")
    parser.add_argument("--npb2", type=int, default=8, help="Default: 8 | Notes per bar for melody 2.")
    
    args = parser.parse_args()

    # Set key2 to key1 if not provided
    if args.key2 is None:
        args.key2 = args.key1

    # input validation
    if args.npb1 > args.bar or args.npb2 > args.bar:
        raise ValueError(f"NPB cannot be greater than BAR.")
    
    if args.key1 not in VALID_KEYS:
        raise ValueError(f"Invalid key '{args.key1}'. Must be one of these: {', '.join(sorted(VALID_KEYS))}.")
    
    if args.key2 not in VALID_KEYS:
        raise ValueError(f"Invalid key '{args.key2}'. Must be one of these: {', '.join(sorted(VALID_KEYS))}.")

    
    # generate first melody
    key_scale1 = octave_shift(generate_scale(args.key1), args.shift1)
    melody1 = generate_random_melody(key_scale1, args.bar, args.npb1)
    print("\n")
    clear_line_and_print("Baking melody...5")
    wave1 = create_melody_waveform(melody1, calculate_note_length(args.bpm), args.loops)
    clear_line_and_print("Baking melody...4")
    play_wave(wave1)

    # generate second melody
    key_scale2 = octave_shift(generate_scale(args.key2), args.shift2)
    melody2 = generate_random_melody(key_scale2, args.bar, args.npb2)
    clear_line_and_print("Baking melody...3")
    wave2 = create_melody_waveform(melody2, calculate_note_length(args.bpm), args.loops)
    clear_line_and_print("Baking melody...2")
    play_wave(wave2)

    # add melodies
    clear_line_and_print("Baking melody...1")
    waveform = add_waves(wave1, wave2)
    play_wave(waveform)
    clear_line_and_print("Baking melody...DING!\n")

    # prompt save
    attributes = get_attributes(args)
    save_wave(attributes, waveform)
