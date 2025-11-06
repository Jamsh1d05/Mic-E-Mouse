import librosa.display, matplotlib.pyplot as plt
y, sr = librosa.load("enhanced.wav")
librosa.display.specshow(librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max), sr=sr)
plt.show()