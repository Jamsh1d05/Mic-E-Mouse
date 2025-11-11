import librosa.display, matplotlib.pyplot as plt
import numpy as np
y, sr = librosa.load("mouse_sound.wav")
librosa.display.specshow(librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max), sr=sr)
plt.show()