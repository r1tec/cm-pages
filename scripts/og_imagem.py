"""Gera a imagem de compartilhamento 1200x630 (WhatsApp/Facebook/Google) de uma página.

Uso: python3 scripts/og_imagem.py <slug> <imagem de origem>
Saída: <slug>/assets/og-<slug>.jpg. Imagem larga é recortada; alta ou quadrada fica
inteira no centro, sobre um fundo desfocado dela mesma.
"""
import os
import sys

from PIL import Image, ImageEnhance, ImageFilter

L, A = 1200, 630


def gerar(origem, destino, fundo_liso='#2b211b'):
    img = Image.open(origem)
    if img.mode in ('RGBA', 'LA', 'P'):
        # Recorte com fundo transparente (capa, mockup): fica inteiro sobre um fundo liso.
        img = img.convert('RGBA')
        final = Image.new('RGB', (L, A), fundo_liso)
        escala = min((L - 60) / img.width, (A - 60) / img.height)
        frente = img.resize((round(img.width * escala), round(img.height * escala)), Image.LANCZOS)
        final.paste(frente, ((L - frente.width) // 2, (A - frente.height) // 2), frente)
        final.save(destino, quality=84, optimize=True, progressive=True)
        return
    img = img.convert('RGB')
    if img.width / img.height >= 1.5:
        escala = max(L / img.width, A / img.height)
        img = img.resize((round(img.width * escala), round(img.height * escala)), Image.LANCZOS)
        x, y = (img.width - L) // 2, (img.height - A) // 2
        final = img.crop((x, y, x + L, y + A))
    else:
        escala = max(L / img.width, A / img.height)
        fundo = img.resize((round(img.width * escala), round(img.height * escala)), Image.LANCZOS)
        x, y = (fundo.width - L) // 2, (fundo.height - A) // 2
        final = ImageEnhance.Brightness(fundo.crop((x, y, x + L, y + A)).filter(ImageFilter.GaussianBlur(28))).enhance(0.55)
        escala = min((L - 40) / img.width, (A - 40) / img.height)
        frente = img.resize((round(img.width * escala), round(img.height * escala)), Image.LANCZOS)
        final.paste(frente, ((L - frente.width) // 2, (A - frente.height) // 2))
    final.save(destino, quality=84, optimize=True, progressive=True)


if __name__ == '__main__':
    slug, origem = sys.argv[1], sys.argv[2]
    destino = os.path.join(slug, 'assets', f'og-{slug}.jpg')
    gerar(origem, destino)
    print(destino, os.path.getsize(destino))
