import hid
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import json

matplotlib.use('TkAgg')


class MouseVibrationAnalyzer:
    def __init__(self, sample_rate=1000):
        self.sample_rate = sample_rate
        self.device = None
        self.vendor_id = None
        self.product_id = None
        self.usage_page = None
        self.usage = None
        self.path = None
        self.raw_data = []
        self.movements = []
        self.recording = False

    def find_mouse(self):
        print("Searching mouse...")
        mice = []

        for dev in hid.enumerate():
            vendor_id = dev["vendor_id"]
            product_id = dev["product_id"]
            usage_page = dev.get("usage_page", 0)
            usage = dev.get("usage", 0)
            product = str(dev.get("product_string", "")).strip()
            interface_number = dev.get("interface_number", -1)
            path = dev["path"].decode() if isinstance(dev["path"], bytes) else dev["path"]

            # Match your specific VGN F1 MOBA
            if vendor_id == 0x3554 and product_id == 0xf506 and dev.get("interface_number") == 2:
                mice.append({
                    "path": path,
                    "usage_page": usage_page,
                    "usage": usage,
                    "interface_number": interface_number,
                    "product": product
                })

        if not mice:
            print("No compatible mouse interface found.")
            return False

        preferred = next((m for m in mice if m["interface_number"] in [1, 2]), mice[0])

        self.path = preferred["path"]
        self.vendor_id = 0x3554
        self.product_id = 0xf506
        self.usage_page = preferred["usage_page"]
        self.usage = preferred["usage"]

        print(f"Mouse found: {preferred['product']}")
        print(f"   Interface: {preferred['interface_number']}, Path: {preferred['path']}")
        return True


    def connect(self):
        if not self.path:
            print("Нет пути к устройству HID")
            return False
        try:
            self.device = hid.device()
            self.device.open_path(self.path.encode() if isinstance(self.path, str) else self.path)
            self.device.set_nonblocking(True)
            print("Connected to HID device")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def record_raw(self, duration=10):
        if not self.device:
            print("No active device")
            return False

        print(f"Starting record for {duration} seconds...")
        self.raw_data = []
        start_time = time.time()
        packet_count = 0

        try:
            while time.time() - start_time < duration:
                data = self.device.read(128) 
                if data:
                    ts = time.time() - start_time
                    self.raw_data.append((ts, bytes(data)))
                    packet_count += 1
                time.sleep(1 / self.sample_rate)

            print(f"Record finished! Captured packets: {packet_count}")
            return True

        except KeyboardInterrupt:
            print("Stopped by user")
            return False
        except Exception as e:
            print(f"Recording error : {e}")
            return False

    def decode(self):
        if not self.raw_data:
            print("No data for decode")
            return

        print("Decoding data...")
        self.movements = []
        for ts, raw in self.raw_data:
            if len(raw) < 3:
                continue
            x = raw[1] - 256 if raw[1] > 127 else raw[1]
            y = raw[2] - 256 if raw[2] > 127 else raw[2]
            self.movements.append((ts, x, y))
        print(f"Decoded {len(self.movements)} movements")

    def analyze(self):
        if not self.movements:
            print("No data for analyze")
            return

        print("Analyzing data...")
        timestamps = np.array([m[0] for m in self.movements])
        xs = np.array([m[1] for m in self.movements])
        ys = np.array([m[2] for m in self.movements])
        magnitude = np.sqrt(xs**2 + ys**2)

        mean_mag = np.mean(magnitude)
        std_mag = np.std(magnitude)
        threshold = mean_mag + 0.3 * std_mag
        vib_count = np.sum(magnitude > threshold)

        print(f"Средняя амплитуда: {mean_mag:.3f}")
        print(f"Стд. отклонение: {std_mag:.3f}")
        print(f"Порог вибраций: {threshold:.3f}")
        print(f"Обнаружено пиков: {vib_count}")

        plt.figure(figsize=(15, 10))

        plt.subplot(3, 1, 1)
        plt.plot(timestamps, xs, label="X", alpha=0.7)
        plt.plot(timestamps, ys, label="Y", alpha=0.7)
        plt.title("Изменения X/Y")
        plt.legend()
        plt.grid(True)

        plt.subplot(3, 1, 2)
        plt.plot(timestamps, magnitude, color="green", alpha=0.8)
        plt.title("Магнитуда движений")
        plt.grid(True)

        fft_result = np.fft.fft(magnitude)
        freqs = np.fft.fftfreq(len(fft_result), d=(timestamps[1]-timestamps[0]))
        plt.subplot(3, 1, 3)
        plt.plot(freqs[freqs > 0], np.abs(fft_result)[freqs > 0])
        plt.title("Частотный спектр вибраций")
        plt.xlabel("Частота (Гц)")
        plt.ylabel("Амплитуда")
        plt.grid(True)

        plt.tight_layout()
        plt.show()

    def save(self):
        if not self.raw_data:
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mouse_data_{ts}.json"
        with open(filename, "w") as f:
            json.dump({
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "packets": len(self.raw_data),
                    "vendor_id": self.vendor_id,
                    "product_id": self.product_id,
                    "usage_page": self.usage_page,
                    "usage": self.usage,
                },
                "raw_data": [
                    {"t": t, "bytes": raw.hex()} for t, raw in self.raw_data
                ]
            }, f, indent=2)
        print(f"Data saved: {filename}")

    def run(self, duration=10):
        if not self.find_mouse(): return
        if not self.connect(): return
        if not self.record_raw(duration): return
        self.decode()
        self.analyze()
        self.save()
        print("Finished successfully!")


if __name__ == "__main__":
    analyzer = MouseVibrationAnalyzer()
    try:
        analyzer.run(duration=10)
    except KeyboardInterrupt:
        print("\n Stopped by user")
    finally:
        print("\n Done")
