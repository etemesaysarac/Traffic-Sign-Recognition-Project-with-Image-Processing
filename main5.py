import tkinter as tk
from tkinter import filedialog, Toplevel
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import sys

analiz_sayisi = 1

# EXE için dosya yolu uyumu
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def levhalari_yukle():
    levha_klasoru = resource_path("levhalar")
    levhalar = {}
    for levha_resmi in os.listdir(levha_klasoru):
        if levha_resmi.lower().endswith(('.png', '.jpg', '.jpeg')):
            yol = os.path.join(levha_klasoru, levha_resmi)
            levha_img = cv2.imdecode(np.fromfile(yol, np.uint8), cv2.IMREAD_GRAYSCALE)
            if levha_img is not None:
                levha_ad = os.path.splitext(levha_resmi)[0]
                levhalar[levha_ad] = levha_img
    return levhalar

levhalar = levhalari_yukle()

def detect_sign(image_path):
    test_img_color = cv2.imdecode(np.fromfile(image_path, np.uint8), cv2.IMREAD_COLOR)
    if test_img_color is None:
        return "Görsel okunamadı!", 0

    test_img = cv2.cvtColor(test_img_color, cv2.COLOR_BGR2GRAY)

    max_eslesme = 0
    en_yakin_levha = "Bilinmeyen işaret"

    for levha_ad, levha_img in levhalar.items():
        if levha_img.shape[0] > test_img.shape[0] or levha_img.shape[1] > test_img.shape[1]:
            continue

        res = cv2.matchTemplate(test_img, levha_img, cv2.TM_CCOEFF_NORMED)
        _, eslesme_orani, _, _ = cv2.minMaxLoc(res)

        if eslesme_orani > max_eslesme:
            max_eslesme = eslesme_orani
            en_yakin_levha = levha_ad

    if max_eslesme >= 0.5:
        return f"Tespit edilen levha: '{en_yakin_levha}' (Benzerlik: {max_eslesme:.2f})", max_eslesme
    else:
        return "Bu bir trafik işareti değildir.", max_eslesme

def gorsel_goster_box(yuklenen_resim, sonuc, oran):
    box = Toplevel()
    box.title("Analiz Sonucu")
    box.geometry("400x600")
    box.resizable(False, False)

    if oran == 1.0:
        tk.Label(box, text="🎉 Tebrikler! Mükemmel eşleşme! 🎉", fg="green", font=("Arial", 14, "bold")).pack(pady=10)
    elif "değildir" in sonuc:
        tk.Label(box, text="❌ Hata! Trafik işareti bulunamadı!", fg="red", font=("Arial", 14, "bold")).pack(pady=10)
    else:
        tk.Label(box, text="✅ İşaret başarıyla tespit edildi.", fg="blue", font=("Arial", 14, "bold")).pack(pady=10)

    img_user = Image.open(yuklenen_resim).resize((250, 250))
    box.img_user = ImageTk.PhotoImage(img_user)
    tk.Label(box, image=box.img_user).pack(pady=10)

    tk.Message(box, text=sonuc, width=350, font=("Arial", 12)).pack(pady=10)

    alt_frame = tk.Frame(box)
    alt_frame.pack(pady=10)

    box.img_tasarim = ImageTk.PhotoImage(Image.open(resource_path("Adsız tasarım.png")).resize((80, 80)))
    tk.Label(alt_frame, image=box.img_tasarim).pack(side='left', padx=5)
    tk.Label(alt_frame, text="Bu yazılım KTO Karatay Üniversitesi\nBilgisayar Görmesi dersi için\nEtem SARAÇ tarafından hazırlanmıştır.",
             font=("Arial", 9)).pack(side='left', padx=5)

    box.img_logo = ImageTk.PhotoImage(Image.open(resource_path("KTO.png")).resize((100, 100)))
    tk.Label(box, image=box.img_logo).pack(side='bottom', pady=5)

    box.after(5000, box.destroy)

def analiz_et():
    global analiz_sayisi
    dosya = filedialog.askopenfilename(title="Görsel seçin", filetypes=[("Görseller", "*.jpg *.png *.jpeg")])
    if not dosya:
        return

    sonuc, oran = detect_sign(dosya)

    text_area.config(state='normal')
    text_area.insert(tk.END, f"{analiz_sayisi}) {sonuc}\n")
    text_area.config(state='disabled')
    analiz_sayisi += 1

    gorsel_goster_box(dosya, sonuc, oran)

# Ana Arayüz
root = tk.Tk()
root.title("Trafik İşareti Tanıma Sistemi")
root.geometry("700x750")

tk.Label(root, text="Trafik İşareti Tanıma Sistemi", font=("Arial", 18, "bold"), fg="blue").pack(pady=10)

tk.Button(root, text="Görsel Yükle ve Analiz Et", command=analiz_et, bg="#4CAF50", fg="white").pack(pady=10)
tk.Button(root, text="Uygulamayı Kapat", command=root.quit, bg="red", fg="white").pack(pady=5)

text_area = tk.Text(root, height=15, width=70, state='disabled', font=("Arial", 11))
text_area.pack(pady=10)

alt_frame_ana = tk.Frame(root)
alt_frame_ana.pack(pady=10)

img_foto_ana = Image.open(resource_path("Adsız tasarım.png")).resize((120, 120))
img_foto_ana = ImageTk.PhotoImage(img_foto_ana)
tk.Label(alt_frame_ana, image=img_foto_ana).pack(side='left', padx=5)

tk.Label(alt_frame_ana, text="Bu yazılım KTO Karatay Üniversitesi Tezli Yüksek Lisans Programı\n"
                             "Bilgisayar Görmesi dersi için Etem SARAÇ tarafından tasarlanmıştır.",
         font=("Arial", 10), justify='left').pack(side='left', padx=5)

img_logo_ana = Image.open(resource_path("KTO.png")).resize((150, 150))
img_logo_ana = ImageTk.PhotoImage(img_logo_ana)
tk.Label(root, image=img_logo_ana).pack(side='bottom', pady=5)

root.mainloop()