import ctypes
import time
import warnings
import threading
import tkinter as tk
from tkinter import ttk
import numpy as np
import soundcard as sc

#Fjerner errorer som kommer fra at det kan være forskjellig runtime
warnings.filterwarnings("ignore", category=sc.SoundcardRuntimeWarning)

# Xinput
try:
    xinput = ctypes.windll.xinput1_4
except Exception:
    xinput = ctypes.windll.xinput1_3


class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]


def set_rumble(left, right, player_index=0):
    if xinput is not None:
        l_speed = int(min(max(left, 0.0), 0.9) * 65535)
        r_speed = int(min(max(right, 0.0), 0.9) * 65535)
        vibration = XINPUT_VIBRATION(l_speed, r_speed)
        xinput.XInputSetState(player_index, ctypes.byref(vibration))


# Tkinter som frondend
class RumbleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lyd til Vibrasjon. Xbox kontroller")
        self.root.geometry("340x440")
        self.root.resizable(False, False)

        self.running = False
        self.thread = None

        # Tittel
        title_label = ttk.Label(root, text="Lyd til vibrasjon. Xbox kontroller", font=("Arial", 12, "bold"))
        title_label.pack(pady=10)

        # Modus-valg
        self.modus_var = tk.StringVar(value="1")

        frame_moduser = ttk.LabelFrame(root, text=" Velg Modus ", padding=10)
        frame_moduser.pack(fill="x", padx=15, pady=5)

        ttk.Radiobutton(frame_moduser, text="1. Spesialisert (Bass-fokus)", variable=self.modus_var, value="1").pack(
            anchor="w", pady=2)
        ttk.Radiobutton(frame_moduser, text="2. Alt-inkludert (Fullt spektrum)", variable=self.modus_var,
                        value="2").pack(anchor="w", pady=2)
        ttk.Radiobutton(frame_moduser, text="3. Rytme-Fokus (Ren taktfølelse)", variable=self.modus_var,
                        value="3").pack(anchor="w", pady=2)

        # Styrke / Volum-glidebryter
        frame_styrke = ttk.LabelFrame(root, text=" Vibrasjonsstyrke ", padding=10)
        frame_styrke.pack(fill="x", padx=15, pady=5)

        self.strength_slider = ttk.Scale(frame_styrke, from_=0.2, to=2.0, value=1.0, orient="horizontal",
                                         command=self.update_strength_label)
        self.strength_slider.pack(fill="x", pady=2)

        self.strength_label = ttk.Label(frame_styrke, text="Styrke: 1.0x", font=("Arial", 9))
        self.strength_label.pack(pady=2)

        # Statusfelt
        self.status_label = ttk.Label(root, text="Status: Avstengt", font=("Arial", 10), foreground="gray")
        self.status_label.pack(pady=8)

        # Start / Stopp-knapper
        self.btn_start = ttk.Button(root, text="Start Lytter", command=self.start_app)
        self.btn_start.pack(fill="x", padx=20, pady=2)

        self.btn_stop = ttk.Button(root, text="Stopp", command=self.stop_app, state="disabled")
        self.btn_stop.pack(fill="x", padx=20, pady=2)

    def update_strength_label(self, val):
        val_float = float(val)
        self.strength_label.config(text=f"Styrke: {val_float:.1f}x")

    def start_app(self):
        if not self.running:
            self.running = True
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.status_label.config(text="Status: Kjører...", foreground="green")

            self.thread = threading.Thread(target=self.audio_loop, daemon=True)
            self.thread.start()

    def stop_app(self):
        self.running = False
        set_rumble(0.0, 0.0, 0)
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.status_label.config(text="Status: Avstengt", foreground="gray")

    def audio_loop(self):
        try:
            speaker = sc.default_speaker()
            mic = sc.get_microphone(id=speaker.name, include_loopback=True)
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Feil: Kunne ikke hente lyd", foreground="red"))
            self.stop_app()
            return

        samplerate = 44100
        blocksize = 256

        left_env = 0.0
        right_env = 0.0
        left_baseline = 0.0
        right_baseline = 0.0

        try:
            with mic.recorder(samplerate=samplerate, channels=2) as recorder:
                while self.running:
                    data = recorder.record(numframes=blocksize)
                    left_raw = data[:, 0]
                    right_raw = data[:, 1]

                    valg = self.modus_var.get()
                    master_strength = float(self.strength_slider.get())  # Hent verdien fra glidebryteren

                    if valg == "1":
                        kernel_size = 150
                        if len(left_raw) >= kernel_size:
                            filter_kernel = np.ones(kernel_size) / kernel_size
                            left_bass = np.convolve(left_raw, filter_kernel, mode='same')
                            right_bass = np.convolve(right_raw, filter_kernel, mode='same')
                        else:
                            left_bass, right_bass = left_raw, right_raw

                        left_power = np.sqrt(np.mean(left_bass ** 2))
                        right_power = np.sqrt(np.mean(right_bass ** 2))

                        if left_power < 0.03: left_power = 0.0
                        if right_power < 0.03: right_power = 0.0

                        l_final = np.tanh(left_power * 10.0)
                        r_final = np.tanh(right_power * 10.0)

                    elif valg == "3":
                        left_power = np.sqrt(np.mean(left_raw ** 2))
                        right_power = np.sqrt(np.mean(right_raw ** 2))

                        left_baseline = (left_baseline * 0.90) + (left_power * 0.10)
                        right_baseline = (right_baseline * 0.90) + (right_power * 0.10)

                        left_diff = max(0.0, left_power - left_baseline)
                        right_diff = max(0.0, right_power - right_baseline)

                        RHYTHM_THRESHOLD = 0.008
                        if left_diff < RHYTHM_THRESHOLD: left_diff = 0.0
                        if right_diff < RHYTHM_THRESHOLD: right_diff = 0.0

                        l_final = np.tanh(left_diff * 220.0)
                        r_final = np.tanh(right_diff * 220.0)

                    else:
                        left_power = np.sqrt(np.mean(left_raw ** 2))
                        right_power = np.sqrt(np.mean(right_raw ** 2))

                        if left_power > left_env:
                            left_env = (left_env * 0.2) + (left_power * 0.8)
                        else:
                            left_env = (left_env * 0.5) + (left_power * 0.5)

                        if right_power > right_env:
                            right_env = (right_env * 0.2) + (right_power * 0.8)
                        else:
                            right_env = (right_env * 0.5) + (right_power * 0.5)

                        l_final = np.tanh(left_env * 12.0)
                        r_final = np.tanh(right_env * 12.0)

                    # Bryter for å justere styrke
                    l_final = min(1.0, l_final * master_strength)
                    r_final = min(1.0, r_final * master_strength)

                    set_rumble(l_final, r_final, 0)

        except Exception:
            pass

        set_rumble(0.0, 0.0, 0)


if __name__ == "__main__":
    root = tk.Tk()
    app = RumbleApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_app(), root.destroy()))
    root.mainloop()