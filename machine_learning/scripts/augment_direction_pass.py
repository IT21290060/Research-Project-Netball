import os
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array, save_img

# Path to direction_pass images
input_dir = "../data/direction_pass"
output_dir = "../data/direction_pass"

# Create augmentation generator
datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Get list of existing images
existing_files = os.listdir(input_dir)
existing_images = [f for f in existing_files if f.endswith(('.jpg', '.jpeg', '.png'))]
print(f"Found {len(existing_images)} existing images")

# Calculate how many augmented images to generate
target_count = 90  # Approximately balance with start_restart
images_to_generate = target_count - len(existing_images)
print(f"Will generate {images_to_generate} new images")

# Track used filenames to avoid duplicates
used_names = set(existing_images)

# Generate augmented images
generated_count = 0
for image_file in existing_images:
    if generated_count >= images_to_generate:
        break
        
    image_path = os.path.join(input_dir, image_file)
    img = load_img(image_path)
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)
    
    # Generate 3 variations of each image
    variations_per_image = min(3, images_to_generate - generated_count)
    i = 0
    for batch in datagen.flow(x, batch_size=1):
        base_name, ext = os.path.splitext(image_file)
        new_name = f"{base_name}_aug_{i}{ext}"
        
        # Avoid name conflicts
        while new_name in used_names:
            i += 1
            new_name = f"{base_name}_aug_{i}{ext}"
        
        used_names.add(new_name)
        save_path = os.path.join(output_dir, new_name)
        save_img(save_path, batch[0])
        
        generated_count += 1
        i += 1
        
        print(f"Generated {generated_count}/{images_to_generate}: {new_name}")
        
        if generated_count >= images_to_generate or i >= variations_per_image:
            break

print(f"Augmentation complete. Total direction_pass images: {len(existing_images) + generated_count}")