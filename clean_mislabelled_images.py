import os
from PIL import Image, UnidentifiedImageError

dataset_path = "property_dataset"

image_extensions = (".jpg", ".jpeg", ".png")

for root, dirs, files in os.walk(dataset_path):
    for file in files:
        if file.lower().endswith(image_extensions):
            file_path = os.path.join(root, file)
            try:
                print(f"✅ Loading {file_path} ...", end=" ")
                with Image.open(file_path) as img:
                    img.convert("RGB")  # Fully decode it
                print("OK")
            except (UnidentifiedImageError, OSError, ValueError) as e:
                print("❌ FAILED!")
                print(f"   Error: {e}")
