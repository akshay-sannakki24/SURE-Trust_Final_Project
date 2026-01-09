import tkinter as tk
from tkinter import filedialog
import time
from src.core.encryption import BlowfishEncryptor

enc = BlowfishEncryptor()

# ================= THEME =================
WIN_BG   = "#0f172a"
HEADER   = "#1e3a8a"
CARD_BG  = "#111827"
BTN_ON   = "#2dd4bf"
BTN_OFF  = "#9ca3af"
TEXT     = "#f8fafc"
SUBTEXT  = "#cbd5f5"
SUCCESS  = "#22c55e"
ERROR    = "#ef4444"

FONT_T = ("Segoe UI", 10)
FONT_H = ("Segoe UI Semibold", 10)
FONT_B = ("Segoe UI Semibold", 10)

# ========================================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blowfish File Security Tool")
        self.geometry("900x520")
        self.configure(bg=WIN_BG)
        self.mode = "encrypt"

        # ---------- HEADER ----------
        header = tk.Frame(self, bg=HEADER, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🔒  Blowfish File Security Tool",
            bg=HEADER,
            fg="white",
            font=("Segoe UI Semibold", 16)
        ).pack(pady=14)

        # ---------- TABS ----------
        tabs = tk.Frame(self, bg=WIN_BG)
        tabs.pack(pady=18)

        self.btn_encrypt = tk.Button(
            tabs, text="🔐 Encrypt", width=16, font=FONT_B,
            command=lambda: self.set_mode("encrypt")
        )
        self.btn_decrypt = tk.Button(
            tabs, text="🔓 Decrypt", width=16, font=FONT_B,
            command=lambda: self.set_mode("decrypt")
        )
        self.btn_verify = tk.Button(
            tabs, text="🛡 Integrity", width=16, font=FONT_B,
            command=lambda: self.set_mode("verify")
        )

        for b in (self.btn_encrypt, self.btn_decrypt, self.btn_verify):
            b.pack(side="left", padx=10)

        # ---------- CARD ----------
        card = tk.Frame(self, bg=CARD_BG)
        card.pack(anchor="center", pady=10)

        card.grid_columnconfigure(0, minsize=520)
        card.grid_columnconfigure(1, minsize=120)

        r = 0

        # ---------- FILE ----------
        tk.Label(card, text="1. Select file", bg=CARD_BG, fg=TEXT, font=FONT_H)\
            .grid(row=r, column=0, sticky="w", padx=20, pady=(20, 4))
        r += 1

        self.file_entry = tk.Entry(card, width=55, font=FONT_T)
        self.file_entry.grid(row=r, column=0, padx=(20, 10), sticky="w")

        tk.Button(card, text="Browse", command=self.browse)\
            .grid(row=r, column=1, padx=(0, 20), sticky="w")
        r += 1

        self.file_hint = tk.Label(card, text="No file selected",
                                  bg=CARD_BG, fg=SUBTEXT, font=FONT_T)
        self.file_hint.grid(row=r, column=0, sticky="w", padx=20, pady=(2, 14))
        r += 1

        # ---------- PASSWORD ----------
        self.pass_label = tk.Label(card, text="2. Password",
                                   bg=CARD_BG, fg=TEXT, font=FONT_H)
        self.pass_label.grid(row=r, column=0, sticky="w", padx=20)
        r += 1

        self.pass_entry = tk.Entry(card, show="*", width=60, font=FONT_T)
        self.pass_entry.grid(row=r, column=0, padx=20, pady=(4, 14), sticky="w")
        r += 1

        # ---------- FILENAME ----------
        self.fn_label = tk.Label(card, text="3. Filename handling",
                                 bg=CARD_BG, fg=TEXT, font=FONT_H)
        self.fn_label.grid(row=r, column=0, sticky="w", padx=20)
        r += 1

        self.keep_var = tk.IntVar(value=1)

        self.rb_keep = tk.Radiobutton(
            card, text="Keep original filename",
            variable=self.keep_var, value=1,
            bg=CARD_BG, fg=TEXT,
            selectcolor=CARD_BG,
            activebackground=CARD_BG,
            activeforeground=TEXT,
            font=FONT_T
        )
        self.rb_enc = tk.Radiobutton(
            card, text="Encrypt filename",
            variable=self.keep_var, value=0,
            bg=CARD_BG, fg=TEXT,
            selectcolor=CARD_BG,
            activebackground=CARD_BG,
            activeforeground=TEXT,
            font=FONT_T
        )

        self.rb_keep.grid(row=r, column=0, sticky="w", padx=40)
        r += 1
        self.rb_enc.grid(row=r, column=0, sticky="w", padx=40)
        r += 1

        self.del_var = tk.IntVar()
        self.chk_del = tk.Checkbutton(
            card,
            text="Secure delete source file after operation",
            variable=self.del_var,
            bg=CARD_BG, fg=TEXT,
            selectcolor=CARD_BG,
            activebackground=CARD_BG,
            activeforeground=TEXT,
            font=FONT_T
        )
        self.chk_del.grid(row=r, column=0, sticky="w", padx=20, pady=(8, 16))
        r += 1

        # ---------- ACTION ----------
        self.action_btn = tk.Button(
            card, text="Encrypt File",
            bg=BTN_ON, fg="#022c22",
            font=FONT_B, width=22,
            command=self.run
        )
        self.action_btn.grid(row=r, column=0, columnspan=2, pady=14)
        r += 1

        self.status = tk.Label(card, text="", bg=CARD_BG, fg=SUCCESS, font=FONT_T)
        self.status.grid(row=r, column=0, columnspan=2, pady=(0, 20))

        self.set_mode("encrypt")

    # ---------- MODE ----------
    def set_mode(self, mode):
        self.mode = mode

        for b in (self.btn_encrypt, self.btn_decrypt, self.btn_verify):
            b.config(bg=BTN_OFF)

        {"encrypt": self.btn_encrypt,
         "decrypt": self.btn_decrypt,
         "verify":  self.btn_verify}[mode].config(bg=BTN_ON)

        if mode == "encrypt":
            self.pass_label.grid()
            self.pass_entry.grid()
            self.fn_label.grid()
            self.rb_keep.grid()
            self.rb_enc.grid()
            self.action_btn.config(text="Encrypt File")

        elif mode == "decrypt":
            self.pass_label.grid()
            self.pass_entry.grid()
            self.fn_label.grid_remove()
            self.rb_keep.grid_remove()
            self.rb_enc.grid_remove()
            self.action_btn.config(text="Decrypt File")

        else:
            self.pass_label.grid_remove()
            self.pass_entry.grid_remove()
            self.fn_label.grid_remove()
            self.rb_keep.grid_remove()
            self.rb_enc.grid_remove()
            self.action_btn.config(text="Verify Integrity")

        self.status.config(text="", fg=SUCCESS)

    # ---------- ACTIONS ----------
    def browse(self):
        path = filedialog.askopenfilename()
        if path:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, path)
            self.file_hint.config(text=path.split("/")[-1])

    def run(self):
        path = self.file_entry.get().strip()
        pwd = self.pass_entry.get().encode()
        keep = bool(self.keep_var.get())
        delete = bool(self.del_var.get())

        try:
            if self.mode == "encrypt":
                t = time.perf_counter()
                enc.encrypt_file(path, pwd, keep, delete)
                self.status.config(text=f"Encryption completed in {time.perf_counter()-t:.2f}s")

            elif self.mode == "decrypt":
                t = time.perf_counter()
                enc.decrypt_file(path, pwd, delete)
                self.status.config(text=f"Decryption completed in {time.perf_counter()-t:.2f}s")

            else:
                ok = enc.verify_file(path)
                self.status.config(
                    text="Integrity OK" if ok else "Integrity FAILED",
                    fg=SUCCESS if ok else ERROR
                )

        except Exception as e:
            self.status.config(text=str(e), fg=ERROR)

if __name__ == "__main__":
    App().mainloop()
