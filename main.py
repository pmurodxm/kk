import json
import os
import tkinter as tk
from tkinter import messagebox
import requests
from PIL import ImageTk, Image
import datetime
import webbrowser

# GitHub URL'lar
GITHUB_JSON_URL = "https://raw.githubusercontent.com/pmurodxm/kk/main/product.json"
GITHUB_BANNER_URL = "https://raw.githubusercontent.com/pmurodxm/kk/main/banner.jpg"
LOCAL_JSON_PATH = "product.json"
LOCAL_BANNER_PATH = "banner.jpg"
LOCAL_UPDATE_TIME_PATH = "update_time.txt"

# Icon fayli nomi (dastur bilan bir papkada bo'lishi kerak)
ICON_PATH = "app_icon.ico"          # .ico formatida bo'lsa yaxshi
# Agar .png bo'lsa ham ishlatish mumkin, lekin ba'zi Windows versiyalarida muammo chiqishi mumkin

def check_and_update_json():
    try:
        resp = requests.get(GITHUB_JSON_URL, timeout=10)
        resp.raise_for_status()
        remote = resp.json()
        ver_remote = remote.get('version', '0.0')

        ver_local = '0.0'
        local_data = None
        if os.path.exists(LOCAL_JSON_PATH):
            with open(LOCAL_JSON_PATH, encoding='utf-8') as f:
                local_data = json.load(f)
                ver_local = local_data.get('version', '0.0')

        if ver_remote > ver_local:
            with open(LOCAL_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(remote, f, ensure_ascii=False, indent=2)
            with open(LOCAL_UPDATE_TIME_PATH, 'w') as f:
                f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            messagebox.showinfo("Yangilandi", f"Versiya {ver_remote}")
            return remote
        return local_data or remote
    except Exception as e:
        messagebox.showwarning("Xato", f"Yangilash muvaffaqiyatsiz: {e}")
        if os.path.exists(LOCAL_JSON_PATH):
            with open(LOCAL_JSON_PATH, encoding='utf-8') as f:
                return json.load(f)
        return None

def download_banner():
    try:
        resp = requests.get(GITHUB_BANNER_URL, timeout=8)
        resp.raise_for_status()
        with open(LOCAL_BANNER_PATH, 'wb') as f:
            f.write(resp.content)
        return True
    except:
        return False

def get_update_time():
    try:
        with open(LOCAL_UPDATE_TIME_PATH) as f:
            return f.read().strip()
    except:
        return "—"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("KK Kod Qidiruv")
        self.root.geometry("520x580")
        self.root.configure(bg="#0d1117")

        # Oyna o'lchamini o'zgartirib bo'lmaydi
        self.root.resizable(False, False)

        # Icon qo'shish
        if os.path.exists(ICON_PATH):
            try:
                self.root.iconbitmap(ICON_PATH)           # .ico uchun
            except:
                try:
                    img = Image.open(ICON_PATH)
                    photo = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, photo)      # .png uchun
                except:
                    print("Icon yuklanmadi")
        else:
            print("Icon fayli topilmadi:", ICON_PATH)

        # Banner background
        self.bg_photo = None
        self.bg_label = None
        self._load_background()

        self.data = check_and_update_json()
        if not self.data:
            messagebox.showerror("Xato", "Ma'lumotlar yuklanmadi!")
            self.root.destroy()
            return

        self.version = self.data.get('version', '?.?')
        self.update_time = get_update_time()

        # Asosiy konteyner
        container = tk.Frame(root, bg="#111111")
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.94, relheight=0.92)

        tk.Label(container, text="KK Kod Qidiruv", font=("Segoe UI", 16, "bold"),
                 bg="#111111", fg="#00d4ff").pack(pady=(20,10))

        tk.Label(container, text="SPR kod:", font=("Segoe UI", 10),
                 bg="#111111", fg="white").pack(anchor="w", padx=20)
        self.spr_entry = tk.Entry(container, width=48, font=("Consolas", 11),
                                  bg="#0d1117", fg="#c9d1d9", insertbackground="white")
        self.spr_entry.pack(pady=(4,12), padx=20)

        tk.Button(container, text="QIDIRISH (SPR)", command=self.search_spr,
                  bg="#238636", fg="white", activebackground="#2ea043",
                  font=("Segoe UI", 10, "bold")).pack(pady=4)

        tk.Label(container, text="SKP kod:", font=("Segoe UI", 10),
                 bg="#111111", fg="white").pack(anchor="w", padx=20, pady=(12,0))
        self.skp_entry = tk.Entry(container, width=48, font=("Consolas", 11),
                                  bg="#0d1117", fg="#c9d1d9", insertbackground="white")
        self.skp_entry.pack(pady=(4,12), padx=20)

        tk.Button(container, text="QIDIRISH (SKP)", command=self.search_skp,
                  bg="#238636", fg="white", activebackground="#2ea043",
                  font=("Segoe UI", 10, "bold")).pack(pady=4)

        self.result_text = tk.Text(container, height=7, width=55, wrap="word",
                                   font=("Consolas", 10), bg="#161b22", fg="#c9d1d9",
                                   bd=0, highlightthickness=1, highlightbackground="#30363d")
        self.result_text.pack(pady=20, padx=20, fill="both")
        self.result_text.config(state="disabled")

        footer = tk.Frame(container, bg="#111111")
        footer.pack(side="bottom", fill="x", pady=10)

        tk.Label(footer, text=f"Versiya {self.version} • Yangilangan: {self.update_time}",
                 font=("Segoe UI", 8), bg="#111111", fg="#8b949e").pack()
        tk.Label(footer, text="Dasturchi: Primov Murod", font=("Segoe UI", 9),
                 bg="#111111", fg="#8b949e").pack(pady=2)

        tg = tk.Label(footer, text="Telegram: @CodeDrop_py", fg="#58a6ff", cursor="hand2",
                      font=("Segoe UI", 10, "underline"), bg="#111111")
        tg.pack(pady=4)
        tg.bind("<Button-1>", lambda _: webbrowser.open("https://t.me/CodeDrop_py"))

    def _load_background(self):
        download_banner()
        try:
            img = Image.open(LOCAL_BANNER_PATH)
            # Endi resize qilmaymiz — original o'lchamda
            self.bg_photo = ImageTk.PhotoImage(img)
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0)
            self.bg_label.lower()
        except Exception as e:
            print("Banner yuklanmadi:", e)
            self.root.configure(bg="#0d1117")

    def _show_result(self, lines):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)

        for line in lines:
            if line.startswith(("SPR Kod:", "SKP Kod:")):
                tag = "code"
                self.result_text.insert(tk.END, line + "\n", tag)
            else:
                self.result_text.insert(tk.END, line + "\n")

        self.result_text.tag_configure("code", foreground="#79c0ff", underline=True)
        self.result_text.tag_bind("code", "<Button-1>", self._copy_code)
        self.result_text.tag_bind("code", "<Enter>", lambda e: self.result_text.config(cursor="hand2"))
        self.result_text.tag_bind("code", "<Leave>", lambda e: self.result_text.config(cursor=""))

        self.result_text.config(state="disabled")

    def _copy_code(self, event):
        index = self.result_text.index(f"@{event.x},{event.y}")
        line_start = f"{index.split('.')[0]}.0"
        line_end = f"{int(index.split('.')[0])+1}.0"
        text = self.result_text.get(line_start, line_end).strip()

        if ":" in text:
            code_part = text.split(":", 1)[1].strip()
            self.root.clipboard_clear()
            self.root.clipboard_append(code_part)
            self.root.update()
            messagebox.showinfo("Nusxalandi", f"Kod nusxalandi:\n{code_part}")
        return "break"

    def search_spr(self):
        kod = self.spr_entry.get().strip()
        if not kod:
            messagebox.showwarning("Diqqat", "SPR kodini kiriting")
            return

        item = self.data.get('spr_to_skp', {}).get(kod)
        if not item:
            self._show_result(["Topilmadi"])
            return

        lines = [
            f"SPR Nomi:   {item['spr_nomi']}",
            f"SKP Kod:    {item['skp_kod']}",
            f"SKP Nomi:   {item['skp_nomi']}",
            f"Aytilishi:  {item['aytilishi']}"
        ]
        self._show_result(lines)

    def search_skp(self):
        kod = self.skp_entry.get().strip()
        if not kod:
            messagebox.showwarning("Diqqat", "SKP kodini kiriting")
            return

        item = self.data.get('skp_to_spr', {}).get(kod)
        if not item:
            self._show_result(["Topilmadi"])
            return

        lines = [
            f"SPR Kod:    {item['spr_kod']}",
            f"SPR Nomi:   {item['spr_nomi']}",
            f"SKP Nomi:   {item['skp_nomi']}",
            f"Aytilishi:  {item['aytilishi']}"
        ]
        self._show_result(lines)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()