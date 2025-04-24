from PIL import Image
import os

input_dir = "property_dataset"
output_dir = "converted_dataset"

os.makedirs(output_dir, exist_ok=True)

for subdir in os.listdir(input_dir):
    subfolder_path = os.path.join(input_dir, subdir)
    output_subdir = os.path.join(output_dir, subdir)
    os.makedirs(output_subdir, exist_ok=True)

    for file in os.listdir(subfolder_path):
        if file.lower().endswith(".avif"):
            try:
                img_path = os.path.join(subfolder_path, file)
                img = Image.open(img_path)
                new_file = file.replace(".avif", ".jpg")
                img.save(os.path.join(output_subdir, new_file), "JPEG")
                print(f"Converted: {file}")
            except Exception as e:
                print(f"Failed to convert {file}: {e}")
        else:
            # Copy other files
            img_path = os.path.join(subfolder_path, file)
            os.system(f'copy "{img_path}" "{output_subdir}\\{file}"')
