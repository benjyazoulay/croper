import streamlit as st
from PIL import Image
import numpy as np
import os
import zipfile
import io
import math

def crop_image_with_overlap(image, size=1024):
    width, height = image.size
    crops = []

    # Calcul de l'overlap nécessaire pour chaque dimension
    overlap_x = (width % size) if width % size != 0 else 0
    overlap_y = (height % size) if height % size != 0 else 0

    # Itération pour découper l'image en blocs carrés de 1024x1024 avec chevauchement si nécessaire
    for top in range(0, height, size - overlap_y):
        for left in range(0, width, size - overlap_x):
            box = (left, top, min(left + size, width), min(top + size, height))
            cropped_img = image.crop(box)
            
            # Redimensionnement si la tuile n'est pas exactement de 1024x1024
            if cropped_img.size != (size, size):
                cropped_img = cropped_img.resize((size, size), Image.ANTIALIAS)
                
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
    st.title("Découper une image en haute résolution en tuiles de 1024x1024 avec chevauchement")

    uploaded_file = st.file_uploader("Choisissez une image en haute résolution", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Image originale", use_column_width=True)

        if st.button("Découper l'image"):
            crops = crop_image_with_overlap(image, size=1024)
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
