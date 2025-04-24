import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

# Load the trained model
model = tf.keras.models.load_model('property_classifier_model.h5')

# Path to the test image
img_path = 'property_dataset/fake/fake_49.jpg'  

# Load and preprocess the image
img = image.load_img(img_path, target_size=(128, 128))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array /= 255.0  # Same normalization as training

# Predict
prediction = model.predict(img_array)[0][0]
print(prediction)
# Interpret prediction
if prediction < 0.5:
    confidence = prediction * 100
    print(f"This looks like a **FAKE** image with {100*confidence:.4f}% confidence.")
else:
    confidence = (1 - prediction) * 100
    print(f"This looks like a **REAL** image with {100*confidence:.4f}% confidence.")
