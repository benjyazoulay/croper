import streamlit as st
from PIL import Image
import numpy as np
import os
import zipfile
import io

def calculate_overlap(dimension, tile_size):
    n_tiles = (dimension + tile_size - 1) // tile_size
    if n_tiles > 1:
        overlap = (tile_size * n_tiles - dimension) / (n_tiles - 1)
    else:
        overlap = 0
    return int(overlap), n_tiles

def crop_image(image, size=1024):
    width, height = image.size

    # Calcul des overlaps pour la largeur et la hauteur
    overlap_x, n_tiles_x = calculate_overlap(width, size)
    overlap_y, n_tiles_y = calculate_overlap(height, size)

    crops = []
    for i in range(n_tiles_y):
        for j in range(n_tiles_x):
            left = j * (size - overlap_x)
            top = i * (size - overlap_y)
            box = (left, top, min(left + size, width), min(top + size, height))
            cropped_img = image.crop(box)
            crops.append(cropped_img)
    return crops

def save_crops_as_zip(crops):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for i, crop in enumerate(crops):
            img_buffer = io.BytesIO()
            crop.save(img_buffer, format="PNG")
            zip_file.writestr(f"crop_{i+1}.png", img_buffer.getvalue())
    return zip_buffer

def main():
    st.title("Découper une image en haute résolution en tuiles de 1024x1024")

    uploaded_file = st.file_uploader("Choisissez une image en haute résolution", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Image originale", use_column_width=True)

        if st.button("Découper l'image"):
            crops = crop_image(image, size=1024)
            st.write(f"Nombre d'images générées : {len(crops)}")

            zip_buffer = save_crops_as_zip(crops)
            zip_buffer.seek(0)

            st.download_button(
                label="Télécharger les images découpées en ZIP",
                data=zip_buffer,
                file_name="images_crops.zip",
                mime="application/zip"
            )

if __name__ == "__main__":
    main()
