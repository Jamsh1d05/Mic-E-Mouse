import json
import matplotlib.pyplot as plt

with open("mouse_data_20251030_113713.json", "r") as f:
    data = json.load(f)

x = []
y = []
time = []

for pkt in data["raw_data"]:
    t = pkt["t"]
    b = bytes.fromhex(pkt["bytes"])
    # assume bytes[2:4] = dx, bytes[4:6] = dy (this varies per mouse)
    dx = int.from_bytes(b[2:4], byteorder='little', signed=True)
    dy = int.from_bytes(b[4:6], byteorder='little', signed=True)
    time.append(t)
    x.append(dx)
    y.append(dy)

plt.plot(time, x, label="X movement")
plt.plot(time, y, label="Y movement")
plt.legend()
plt.show()
