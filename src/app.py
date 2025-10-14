from flask import Flask, request, jsonify, render_template_string
import joblib
import numpy as np
import os

MODEL_PATH = "models/gaussnb_iris.joblib"

app = Flask(__name__)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

data = joblib.load(MODEL_PATH)
model = data["model"]
target_names = data["target_names"]


@app.route("/")
def index():
    return "GaussianNB Iris model server. Go to <a href='/form'>/form</a>"


@app.route("/form")
def form():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Iris Predictor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            input { margin: 5px; padding: 5px; width: 80px; }
            button { margin: 10px; padding: 6px 12px; }
            #result { margin-top: 20px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h2>Iris Species Prediction</h2>
        <form id="predictForm">
            <label>Sepal length: <input type="number" step="0.001" id="sl"></label><br>
            <label>Sepal width: <input type="number" step="0.001" id="sw"></label><br>
            <label>Petal length: <input type="number" step="0.001" id="pl"></label><br>
            <label>Petal width: <input type="number" step="0.001" id="pw"></label><br>
            <button type="submit">Predict</button>
        </form>
        <div id="result"></div>

        <script>
        document.getElementById("predictForm").addEventListener("submit", async (e) => {
            e.preventDefault();
            const features = [
                parseFloat(document.getElementById("sl").value),
                parseFloat(document.getElementById("sw").value),
                parseFloat(document.getElementById("pl").value),
                parseFloat(document.getElementById("pw").value)
            ];

            const res = await fetch("/predict", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({features: features})
            });
            const data = await res.json();

            if (data.error) {
                document.getElementById("result").innerText = "Error: " + data.error;
            } else {
                const pred = data.predictions[0];
                const probs = data.probabilities[0].map(p => p.toFixed(3));
                document.getElementById("result").innerHTML =
                    "Prediction: <b>" + pred + "</b><br>" +
                    "Probabilities: [" + probs.join(", ") + "]";
            }
        });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/predict", methods=["POST"])
def predict():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    if "features" not in payload:
        return jsonify({"error": "JSON must contain 'features' key"}), 400

    X_arr = np.array(payload["features"], dtype=float)
    if X_arr.ndim == 1:
        X_arr = X_arr.reshape(1, -1)

    if X_arr.shape[1] != 4:
        return jsonify({"error": f"Expected 4 features, got {X_arr.shape[1]}"}), 400

    preds_idx = model.predict(X_arr)
    probs = model.predict_proba(X_arr).tolist()
    preds = [target_names[int(i)] for i in preds_idx]

    return jsonify({"predictions": preds, "probabilities": probs})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
