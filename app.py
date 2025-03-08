from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import io
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# Load the trained model
model = None
try:
    model = load_model("brain_tumor_model.keras")
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# Define class labels
CLASS_LABELS = ["glioma_tumor", "meningioma_tumor_tumor", "no_tumor", "pituitary_tumor"]

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Check if file is present
        if "file" not in request.files:
            print("❌ No file part in request")
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            print("❌ No selected file")
            return jsonify({"error": "No file selected"}), 400

        print(f"📂 File received: {file.filename}")

        # Convert file to image
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
        print("🖼️ Image opened successfully")

        image = image.resize((224, 224))  # Resize to model input size
        print("🔍 Image resized to 224x224")

        # Convert image to numpy array
        img_array = np.array(image) / 255.0  # Normalize
        print(f"📊 Image shape: {img_array.shape}")

        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        print(f"📊 Image shape after expansion: {img_array.shape}")

        # Ensure model is loaded
        if model is None:
            print("❌ Model not loaded")
            return jsonify({"error": "Model not available"}), 500

        # Make prediction
        prediction = model.predict(img_array)
        print(f"🔮 Model prediction: {prediction}")

        predicted_class = np.argmax(prediction)
        confidence = float(prediction[0][predicted_class])

        print(f"✅ Predicted: {CLASS_LABELS[predicted_class]}, Confidence: {confidence:.4f}")

        return jsonify({
            "prediction": CLASS_LABELS[predicted_class], 
            "confidence": confidence
        })

    except Exception as e:
        print(f"❌ Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
