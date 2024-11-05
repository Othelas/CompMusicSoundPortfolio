import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
from scipy.fft import fft, ifft

def LoadWav(file_path):
    sample_rate, waveform = wav.read(file_path)
    if waveform.dtype != np.float32:
        waveform = waveform / np.max(np.abs(waveform), axis=0)

    if len(waveform.shape) > 1:
        waveform = waveform[:, 0]
    
    return sample_rate, waveform

def AdjustTone(waveform, sample_rate):

    #Get Frequencies and Energies
    fft_result = fft(waveform)
    energies = np.abs(fft_result)
    frequencies = np.fft.fftfreq(len(waveform), 1 / sample_rate)

    # Find average energy in each band
    low_energy = np.average(energies[(frequencies >= 0) & (frequencies < 300)])
    mid_energy = np.average(energies[(frequencies >= 300) & (frequencies < 2000)])
    high_energy = np.average(energies[(frequencies >= 2000)])
    average_energy = (low_energy + mid_energy + high_energy)/3
    
    # Calculate gain factors
    low_gain = average_energy / (high_energy + 1e-10)
    mid_gain = average_energy / (mid_energy + 1e-10)
    high_gain = average_energy / (low_energy + 1e-10)
    
    # Create adjusted waveform from original and apply gain
    adjusted_fft = fft_result.copy()
    adjusted_fft[(frequencies >= 0) & (frequencies < 300)] *= low_gain
    adjusted_fft[(frequencies >= 300) & (frequencies < 2000)] *= mid_gain
    adjusted_fft[(frequencies >= 2000)] *= high_gain
    
    # Reconstruct waveform with adjusted fft
    adjusted_wav = np.real(ifft(adjusted_fft))
    adjusted_wav /= np.max(np.abs(adjusted_wav) + 1e-10)
    return adjusted_wav.astype(np.float32)

# Main program
if __name__ == "__main__":

    file_path = 'LunaLightMusicIdea.wav'
    sample_rate, waveform = LoadWav(file_path)
    
    if len(waveform.shape) > 1:
        waveform = waveform[:, 0]
    
    adjusted_waveform = AdjustTone(waveform, sample_rate)
    wav.write('ToneControlledAudio.wav', sample_rate, (adjusted_waveform * 32767).astype(np.int16))
    print("Playing tone-controlled audio...")
    sd.play(adjusted_waveform, samplerate=sample_rate)
    sd.wait()
    print("Playback finished.")
    