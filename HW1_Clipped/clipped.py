import numpy as np
import scipy.io.wavfile

# Sine Wave Specifications - hardcoded for now.
sample_rate = 48000
frequency = 440
duration = 1
amplitude = 8192

# Generate time values
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# Generate the sine wave sample
sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)

# Convert from float to 16-bit signed int
sine_wave_int16 = sine_wave.astype(np.int16)

# Write sine wave to WAV file
scipy.io.wavfile.write("sine.wav", sample_rate, sine_wave_int16)

print("File written to sine.wav")
