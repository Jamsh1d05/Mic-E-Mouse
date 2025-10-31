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
        self.raw_data = []
        self.movements = []
        self.recording = False

    def find_mouse(self):
        """Поиск HID-устройства типа мышь"""
        print("🔍 Поиск мыши...")
        for dev in hid.enumerate():
            product = str(dev.get("product_string", "")).lower()
            usage_page = dev.get("usage_page", 0)
            usage = dev.get("usage", 0)
            if (usage_page == 0x01 and usage == 0x02) or "mouse" in product:
                self.vendor_id = dev["vendor_id"]
                self.product_id = dev["product_id"]
                print(f"✅ Найдена мышь: {product}")
                print(f"   VID: 0x{self.vendor_id:04x}, PID: 0x{self.product_id:04x}")
                return True
        print("❌ Мышь не найдена")
        return False

    def connect(self):
        """Подключение к HID-устройству"""
        if self.vendor_id is None or self.product_id is None:
            print("❌ Устройство не выбрано")
            return False
        try:
            self.device = hid.Device(self.vendor_id, self.product_id)
            self.device.nonblocking = True
            print("✅ Подключено к устройству HID")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

    def record_raw(self, duration=15):
        """Запись данных с мыши"""
        if not self.device:
            print("❌ Нет активного устройства")
            return False

        print(f"🎬 Начало записи на {duration} секунд...")
        self.raw_data = []
        start_time = time.time()
        self.recording = True
        packet_count = 0

        try:
            while time.time() - start_time < duration:
                data = self.device.read(64)
                if data:
                    ts = time.time() - start_time
                    self.raw_data.append((ts, bytes(data)))
                    packet_count += 1
                time.sleep(1 / self.sample_rate)
            print(f"✅ Запись завершена. Получено пакетов: {packet_count}")
            return True
        except KeyboardInterrupt:
            print("⏹️ Прервано пользователем")
            return False
        except Exception as e:
            print(f"❌ Ошибка при записи: {e}")
            return False
        finally:
            self.recording = False

    def decode(self):
        """Преобразование байтов в движения X/Y"""
        if not self.raw_data:
            print("⚠️ Нет данных для декодирования")
            return
        print("🔍 Декодирование данных...")
        self.movements = []
        for ts, raw in self.raw_data:
            if len(raw) < 3:
                continue
            x = raw[1] - 256 if raw[1] > 127 else raw[1]
            y = raw[2] - 256 if raw[2] > 127 else raw[2]
            self.movements.append((ts, x, y))
        print(f"✅ Декодировано {len(self.movements)} движений")

    def analyze(self):
        """Vibration analyze"""
        if not self.movements:
            print("⚠️ Нет данных для анализа")
            return

        print("📊 Анализ данных...")
        timestamps = np.array([m[0] for m in self.movements])
        xs = np.array([m[1] for m in self.movements])
        ys = np.array([m[2] for m in self.movements])
        magnitude = np.sqrt(xs**2 + ys**2)

        # Интерполяция на равномерную сетку для FFT
        t_uniform = np.linspace(timestamps[0], timestamps[-1], len(magnitude))
        mag_uniform = np.interp(t_uniform, timestamps, magnitude)

        fft_result = np.fft.fft(mag_uniform)
        freqs = np.fft.fftfreq(len(fft_result), d=(t_uniform[1]-t_uniform[0]))

        # Статистика
        mean_mag = np.mean(magnitude)
        std_mag = np.std(magnitude)
        threshold = mean_mag + 2 * std_mag
        vib_count = np.sum(magnitude > threshold)

        print(f"📈 Средняя амплитуда: {mean_mag:.3f}")
        print(f"📉 Стд. отклонение: {std_mag:.3f}")
        print(f"⚙️ Порог вибраций: {threshold:.3f}")
        print(f"💥 Обнаружено пиков: {vib_count}")

        # Визуализация
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

        plt.subplot(3, 1, 3)
        plt.plot(freqs[freqs > 0], np.abs(fft_result)[freqs > 0])
        plt.title("Частотный спектр вибраций")
        plt.xlabel("Частота (Гц)")
        plt.ylabel("Амплитуда")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        

    def save(self):
        """Saving to json"""
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
                },
                "raw_data": [
                    {"t": t, "bytes": raw.hex()} for t, raw in self.raw_data
                ]
            }, f, indent=2)
        print(f"💾 Данные сохранены: {filename}")

    def run(self, duration=10):
        """Full cycle"""
        if not self.find_mouse(): return
        if not self.connect(): return
        if not self.record_raw(duration): return
        self.decode()
        self.analyze()
        self.save()
        print("✅ Завершено успешно!")


if __name__ == "__main__":
    analyzer = MouseVibrationAnalyzer()
    try:
        analyzer.run(duration=10)
    except KeyboardInterrupt:
        print("\n⏹️ Остановлено пользователем")
    finally:
        print("\n🔒 Завершено")
