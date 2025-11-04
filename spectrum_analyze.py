import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

fs, data = wavfile.read("mouse_sound.wav")
data = data / np.max(np.abs(data))
plt.specgram(data, Fs=fs, NFFT=512, noverlap=256, cmap="magma")
plt.xlabel("Time (s)")
plt.ylabel("Frequency (Hz)")
plt.title("Mouse vibration spectrogram")
plt.colorbar(label="Power (dB)")
plt.show()
