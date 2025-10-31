import torch
import torchaudio
import numpy as np

data = np.load("prepared.npz")
signal = torch.tensor(data["x"], dtype=torch.float32).unsqueeze(0)

model = torch.load("models/VCTK_filter_model.model", map_location="cpu")
model.eval()

with torch.no_grad():
    output = model(signal)

torchaudio.save("filtered_output.wav", output, 16000)
print("✅filtered_output.wav SAVED!")
