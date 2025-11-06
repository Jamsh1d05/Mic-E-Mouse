import json
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from pathlib import Path
import argparse

def load_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def decode_packets(raw_packets):
    """
    raw_packets: list of dicts with keys 't' and 'bytes' (hex string)
    returns: times (np.array), dx (np.array), dy (np.array)
    NOTE: HID format differs per device. This function uses common mouse layout:
      bytes[0] = buttons, bytes[1] = dx (signed 8-bit), bytes[2] = dy (signed 8-bit)
    If your packets differ, adjust parsing accordingly.
    """
    times = []
    dx = []
    dy = []
    for pkt in raw_packets:
        t = float(pkt['t'])
        b = bytes.fromhex(pkt['bytes'])
        if len(b) < 3:
            continue
        x = b[1] - 256 if b[1] > 127 else b[1]
        y = b[2] - 256 if b[2] > 127 else b[2]
        times.append(t)
        dx.append(x)
        dy.append(y)
    return np.array(times), np.array(dx), np.array(dy)

def build_magnitude(dx, dy):
    return np.sqrt(dx.astype(float)**2 + dy.astype(float)**2)

def to_uniform(times, signal_array, fs_target=1000.0):

    if len(times) < 2:
        return np.array([]), np.array([])
    t0 = times[0]
    t1 = times[-1]
    n_samples = max(2, int(np.ceil((t1 - t0) * fs_target)))
    t_uniform = np.linspace(t0, t1, n_samples)
    sig_uniform = np.interp(t_uniform, times, signal_array)
    return t_uniform, sig_uniform

def bandpass(sig, fs, low_hz=50.0, high_hz=1000.0, order=4):
    nyq = 0.5 * fs
    low = low_hz / nyq
    high = high_hz / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return signal.filtfilt(b, a, sig)

def plot_time_and_spectrogram(t, sig, fs, title_prefix=""):
    plt.figure(figsize=(12, 8))

    plt.subplot(2,1,1)
    plt.plot(t - t[0], sig)
    plt.xlabel("Time (s)")
    plt.ylabel("Magnitude (arb)")
    plt.title(f"{title_prefix} - Waveform (magnitude)")

    plt.subplot(2,1,2)
    f, t_spec, Sxx = signal.spectrogram(sig, fs=fs, nperseg=256, noverlap=192, scaling='spectrum')
    plt.pcolormesh(t_spec, f, 10 * np.log10(Sxx + 1e-12), shading='gouraud')
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.title(f"{title_prefix} - Spectrogram (dB)")
    plt.ylim(0, fs/2)
    plt.colorbar(label='Power (dB)')
    plt.tight_layout()
    plt.show()

def save_prepared(t_uniform, sig_uniform, out_prefix):
    np.savez_compressed(f"{out_prefix}.npz", t=t_uniform, x=sig_uniform)

def main(path_json, out_prefix="prepared", fs_target=1000):
    data = load_json(path_json)
    raw_packets = data.get("raw_data", [])
    times, dx, dy = decode_packets(raw_packets)
    if len(times) == 0:
        print("No valid packets decoded.")
        return

    magnitude = build_magnitude(dx, dy)
    print(f"Decoded {len(times)} packets, duration {times[-1]-times[0]:.3f}s")

    t_u, mag_u = to_uniform(times, magnitude, fs_target=fs_target)
    if len(t_u) == 0:
        print("Uniform resampling failed.")
        return

    try:
        mag_bp = bandpass(mag_u, fs=fs_target, low_hz=30.0, high_hz=500.0, order=4)
    except Exception as e:
        print("Bandpass filtering failed (maybe too few samples). Using raw uniform signal.")
        mag_bp = mag_u

    plot_time_and_spectrogram(t_u, mag_bp, fs_target, title_prefix=Path(path_json).stem)

    save_prepared(t_u, mag_bp, out_prefix)
    print(f"Prepared data saved to {out_prefix}.npz")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare mouse HID JSON into uniform vibrational signal")
    parser.add_argument("jsonfile", help="Path to mouse JSON file")
    parser.add_argument("--out", default="prepared", help="Output prefix (.npz)")
    parser.add_argument("--fs", type=float, default=1000.0, help="Target sampling rate in Hz for interpolation")
    args = parser.parse_args()
    main(args.jsonfile, out_prefix=args.out, fs_target=args.fs)
