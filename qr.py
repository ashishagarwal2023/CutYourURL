import base64
import io
import os

import qrcode
from PIL import Image


def qr(text, qr_color="orange", back_color="white", logo_path="./static/qrlogo.png"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color=qr_color, back_color=back_color).convert("RGBA")

    if logo_path and os.path.isfile(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_width, logo_height = logo.size
        img_width, img_height = img.size
        scale_factor = min(img_width // 3, img_height // 3, logo_width, logo_height)
        logo.thumbnail((scale_factor, scale_factor))
        logo_pos = ((img_width - logo.width) // 2, (img_height - logo.height) // 2)

        logo_no_alpha = Image.new("RGB", logo.size, (255, 255, 255))
        logo_no_alpha.paste(logo, mask=logo.split()[3])

        img.paste(logo_no_alpha, logo_pos, mask=logo.split()[3])

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    data_uri = f"data:image/png;base64,{img_str}"
    return data_uri
