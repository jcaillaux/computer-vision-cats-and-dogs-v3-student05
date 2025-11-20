import tensorflow as tf
import tf2onnx
from pathlib import Path

from config.settings import API_CONFIG, MODEL_CONFIG

image_size = MODEL_CONFIG["image_size"]

# Charger votre modèle Keras
model_path = API_CONFIG["model_path"]
model = tf.keras.models.load_model(model_path)

# Obtenir la signature du modèle
spec = (tf.TensorSpec((None, *image_size, 3), tf.float32, name="input"),)

# Convertir en ONNX
output_path = model_path.parent/ 'onnx' / "cats_dogs_model.onnx"
model_proto, _ = tf2onnx.convert.from_keras(
    model,
    input_signature=spec,
    opset=15,
    output_path=output_path
)

print(f"✅ Modèle converti: {output_path}")
