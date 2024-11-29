import argparse
import numpy as np
from numpy.fft import fft, ifft
import sounddevice as sd
from scipy.io.wavfile import write
import time
import random
import math
from scipy.signal import butter, filtfilt


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
# valid style names
VALID_STYLES = {
    "random", "linear", "ascending", "descending", "mountain"
}

# Chromatic scale from C4 - we will generate keys from this.
CHROMATIC_SCALE = [
    ('C3', 130.81),
    ('C#3/Db3', 138.59),
    ('D3', 146.83),
    ('D#3/Eb3', 155.56),
    ('E3', 164.81),
    ('F3', 174.61),
    ('F#3/Gb3', 184.99),
    ('G3', 196.00),
    ('G#3/Ab3', 207.65),
    ('A3', 220.00),
    ('A#3/Bb3', 233.08),
    ('B3', 246.94)
]

MAJOR_CHORD_PATTERN = [4,3,5]
MINOR_CHORD_PATTERN = [3,4,5]
MAJOR_PATTERN = [2, 2, 1, 2, 2, 2, 1]
MINOR_PATTERN = [2, 1, 2, 2, 1, 2, 2]

def generate_scale(key_name, chord):
    is_minor = key_name[-1].lower() == 'm'
    root_note = key_name[:-1] if is_minor else key_name

    if chord:
        pattern = MINOR_CHORD_PATTERN if is_minor else MAJOR_CHORD_PATTERN
    else:
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

def generate_wave(freq, duration, smooth):
    if freq == 0:
        return np.zeros(int(SAMPLE_RATE * duration), dtype=np.uint8)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    if smooth:
        waveform = 0.5 * (np.sin(2 * np.pi * freq * t) + 1) * 255  # Sine wave scaled to [0, 255]
    else:
        waveform = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))
        waveform = ((waveform + 1) * 127.5).astype(np.uint8)  # Square wave scaled to [0, 255]
    return waveform.astype(np.uint8)

def create_melody_waveform(key, duration, loops, smooth):
    full_wave = np.array([], dtype=np.uint8)
    for note in key:
        wave = generate_wave(note, duration, smooth)
        full_wave = np.concatenate((full_wave, wave))
        time.sleep(0.1)
    full_wave = np.tile(full_wave, loops)
    return apply_low_pass_filter(full_wave)

def apply_low_pass_filter(waveform, cutoff=5000):
    nyquist = 0.5 * SAMPLE_RATE
    normal_cutoff = cutoff / nyquist
    b, a = butter(5, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, waveform)

def play_wave(waveform, singular_wave):
    # create a reduced amplitude wave for playback
    # to match combined waveform amplitude
    if singular_wave:
        amplitude = 0.5
        scaled_waveform = waveform.astype(np.float32) / 255.0 * 2 - 1
        scaled_waveform *= amplitude
    else:
        scaled_waveform = waveform
    sd.play(scaled_waveform, samplerate=SAMPLE_RATE)
    sd.wait()

def generate_melody(key, length, npb, style, chord):
    rest_notes = length - npb
    melody = []
    current_index = 0
    double_octave_key = key + octave_shift(key, 1)
    double_octave_key_reverse = double_octave_key[::-1]
    if chord:
        melody_key = double_octave_key
    else:
        melody_key = key

    if style == "random":
        melody = [random.choice(melody_key) for _ in range(npb - 1)]
    
    elif style == "linear":
        root_note_occurence = math.trunc(npb*0.75)
        melody = [random.choice(melody_key) for _ in range(npb - root_note_occurence)]
        melody += [melody_key[0]] * root_note_occurence
        random.shuffle(melody)
        if len(melody) == npb:
            melody = melody[:-1]
    
    elif style == "ascending":
        for i in range(npb - 1):
            if i % 2 == 0:
                melody.append(double_octave_key[current_index % len(double_octave_key)])
                current_index += 1
            else:
                melody.append(random.choice(key))
    
    elif style == "descending":
        for i in range(npb - 1):
            if i % 2 == 0:
                melody.append(double_octave_key_reverse[current_index % len(double_octave_key_reverse)])
                current_index += 1
            else:
                melody.append(random.choice(key))
    
    elif style == "mountain":
        half_a_npb = math.trunc(npb*0.5)
        half_b_npb = npb - half_a_npb
        for i in range(half_a_npb):
            if i % 2 == 0:
                melody.append(double_octave_key[current_index % len(double_octave_key)])
                current_index += 1
            else:
                melody.append(random.choice(key))
        key_reversed = key[::-1]
        current_index = 0
        for i in range(half_b_npb):
            if i % 2 == 0:
                melody.append(double_octave_key_reverse[current_index % len(double_octave_key_reverse)])
                current_index += 1
            else:
                melody.append(random.choice(key))
        if len(melody) == npb:
            melody = melody[:-1]
    
    # randomly insert rests
    tonal_notes = melody[:]
    melody = tonal_notes
    for _ in range(rest_notes):
        insert_pos = random.randint(0, len(melody))
        melody.insert(insert_pos, 0)

    # insert root
    melody.insert(0, key[0])
    return melody

def add_waves(wave1, wave2):
    added_wave = wave1.astype(np.int16) + wave2.astype(np.int16)
    max_amplitude = max(abs(added_wave.min()), abs(added_wave.max()))
    normalized_wave = added_wave / max_amplitude * 0.8
    return normalized_wave.astype(np.float32) 

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
        play_wave(waveform, 0)
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
    parser.add_argument("--chord1", type=bool, default=True, help="Default: True | Set True for chord melody 1.")
    parser.add_argument("--chord2", type=bool, default=False, help="Default: false | Set True for chord melody 2.")
    parser.add_argument("--style1", type=str, default="random", help="Default: random | styles: random, linear, ascending, descending, mountain.")
    parser.add_argument("--style2", type=str, default="random", help="Default: random | Choose melody style.")
    parser.add_argument("--shift1", type=int, default=0, help="Default: 0 | Octave shift up or down for melody 1.")
    parser.add_argument("--shift2", type=int, default=-3, help="Default: -3 | Octave shift up or down for melody 2.")
    parser.add_argument("--bpm", type=int, default=350, help="Default: 350 | Beats per minute.")
    parser.add_argument("--bar", type=int, default=32, help="Default: 32 | Number of beats in a bar.")
    parser.add_argument("--loops", type=int, default=3, help="Default: 3 | Number of times the bar should loop.")
    parser.add_argument("--npb1", type=int, default=24, help="Default: 24 | Notes per bar for melody 1.")
    parser.add_argument("--npb2", type=int, default=16, help="Default: 16 | Notes per bar for melody 2.")
    parser.add_argument("--smooth1", type=bool, default=False, help="Default: false | Set True for a smooth sound on melody 1.")
    parser.add_argument("--smooth2", type=bool, default=False, help="Default: false | Set True for a smooth sound on melody 2.")
    
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
    
    if args.style1 not in VALID_STYLES:
        raise ValueError(f"Invalid style '{args.style1}'. Must be one of these: {', '.join(sorted(VALID_STYLES))}.")
    
    if args.style2 not in VALID_STYLES:
        raise ValueError(f"Invalid style '{args.style2}'. Must be one of these: {', '.join(sorted(VALID_STYLES))}.")
    
    print("\nMelody attributes:")
    print(f"\n     Melody 1 - Key: {args.key1} | Chord: {args.chord1} | Style: {args.style1} | Octave Shift: {args.shift1} | NPB: {args.npb1}")
    print(f"\n     Melody 2 - Key: {args.key2} | Chord: {args.chord2} | Style: {args.style2} | Octave Shift: {args.shift2} | NPB: {args.npb2}")
    print(f"\n     BPM: {args.bpm} | BAR: {args.bar} | Loops: {args.loops}")


    # generate first melody
    key_scale1 = octave_shift(generate_scale(args.key1, args.chord1), args.shift1)
    melody1 = generate_melody(key_scale1, args.bar, args.npb1, args.style1, args.chord1)
    print("\n")
    clear_line_and_print("Preparing melody 1...")
    wave1 = create_melody_waveform(melody1, calculate_note_length(args.bpm), args.loops, args.smooth1)
    clear_line_and_print("Generating melody 1...")
    play_wave(wave1, 1)

    # generate second melody
    key_scale2 = octave_shift(generate_scale(args.key2, args.chord2), args.shift2)
    melody2 = generate_melody(key_scale2, args.bar, args.npb2, args.style2, args.chord2)
    clear_line_and_print("Preparing melody 2...")
    wave2 = create_melody_waveform(melody2, calculate_note_length(args.bpm), args.loops, args.smooth2)
    clear_line_and_print("Generating melody 2...")
    play_wave(wave2, 1)

    # add melodies
    clear_line_and_print("Mixing melodies... ")
    waveform = add_waves(wave1, wave2)
    play_wave(waveform, 0)
    clear_line_and_print("Retro Melody... DONE!\n")

    # prompt save
    attributes = get_attributes(args)
    save_wave(attributes, waveform)
