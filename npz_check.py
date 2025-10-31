import numpy as np
data = np.load("prepared.npz")
print("Keys:", data.files)
print("Length:", len(data["t"]))
print("Duration:", data["t"][-1] - data["t"][0])
print("First 10 samples:", data["x"][:10])
