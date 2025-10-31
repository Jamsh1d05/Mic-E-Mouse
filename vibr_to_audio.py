import numpy as np
from scipy.io.wavfile import write

data = np.load("prepared.npz")
x = data["x"]
fs = 1000  # такая же частота, как при обработке
# нормализация
x = x / np.max(np.abs(x))
write("mouse_sound.wav", fs, (x * 32767).astype(np.int16))
print("Saved to mouse_sound.wav")
