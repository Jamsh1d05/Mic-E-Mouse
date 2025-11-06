import librosa, librosa.display, matplotlib.pyplot as plt
import numpy as np

y, sr = librosa.load("mouse_sound.wav", sr=None)
S = librosa.amplitude_to_db(abs(librosa.stft(y)), ref=np.max)

plt.figure(figsize=(12, 6))
librosa.display.specshow(S, sr=sr, x_axis='time', y_axis='hz')
plt.ylim(0, 5000)
plt.colorbar(format="%+2.0f dB")    
plt.title("Spectrogram of Mouse Sound")
plt.show()
