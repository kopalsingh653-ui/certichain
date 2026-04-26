import qrcode
import os

def generate_qr(data, filename):
    folder = "static/qr"
    os.makedirs(folder, exist_ok=True)

    path = f"{folder}/{filename}.png"
    img = qrcode.make(data)
    img.save(path)

    return path