import numpy as np
import scipy.io.wavfile as wav

# Generates a sine wave with the given parameters.
# Parameters:
# - sample_rate (int): Number of samples per second
# - frequency (float): Frequency of the sine wave in Hz
# - duration (float): Duration of the sine wave in seconds
# - amplitude (int): Amplitude of the sine wave (max value for 16-bit signed integer is 32767)

def create_sine_wave(sample_rate, frequency, duration, amplitude):

    # Generate time values
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Generate sine wave sample
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)
    
    # Convert the samples from float to 16-bit signed int
    sine_wave_int16 = sine_wave.astype(np.int16)
    
    # Return sine wave as a numpy array of 16-bit integers
    return sine_wave_int16

# Create and save the normal sine wave
sine_wave = create_sine_wave(48000, 440, 1, 8192)
wav.write("sine.wav", 48000, sine_wave)
print("Sine wave written to sine.wav")

# Create and save the clipped sine wave
sine_wave_half_amplitude = create_sine_wave(48000, 440, 1, 16384)
sine_wave_clipped = np.clip(sine_wave_half_amplitude, -8192, 8192)
wav.write("clipped.wav", 48000, sine_wave_clipped)
print("Clipped sine wave written to clipped.wav")

