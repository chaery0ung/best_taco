"""Vertex AI image classification endpoint client.

Calls the deployed AutoML Vision classification endpoint and normalizes the
response into the same shape mock_classifier.classify() returns, so it's a
drop-in replacement once GOOGLE_APPLICATION_CREDENTIALS (a service account
key with the Vertex AI User role) is configured.
"""
import base64
import os

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict

PROJECT = os.environ.get("VERTEX_PROJECT")
ENDPOINT_ID = os.environ.get("VERTEX_ENDPOINT_ID")
LOCATION = os.environ.get("VERTEX_LOCATION", "us-central1")
API_ENDPOINT = f"{LOCATION}-aiplatform.googleapis.com"

# The endpoint returns whatever class names it was trained on; adjust this
# set to match your model's actual label taxonomy.
HIGH_URGENCY_LABELS = {
    "melanoma",
    "basal_cell_carcinoma",
    "bcc",
    "squamous_cell_carcinoma",
    "malignant",
}

_client: aiplatform.gapic.PredictionServiceClient | None = None


def _get_client() -> aiplatform.gapic.PredictionServiceClient:
    global _client
    if _client is None:
        _client = aiplatform.gapic.PredictionServiceClient(
            client_options={"api_endpoint": API_ENDPOINT}
        )
    return _client


def classify(image_bytes: bytes) -> dict:
    """Send image bytes to the deployed Vertex AI endpoint and return the top prediction.

    Returns {"classification": str, "confidence": float, "urgency": "high"|"low"}.
    """
    if not PROJECT or not ENDPOINT_ID:
        raise RuntimeError("VERTEX_PROJECT and VERTEX_ENDPOINT_ID must be set to call the Vertex AI endpoint")

    client = _get_client()
    endpoint = client.endpoint_path(project=PROJECT, location=LOCATION, endpoint=ENDPOINT_ID)

    encoded_content = base64.b64encode(image_bytes).decode("utf-8")
    instance = predict.instance.ImageClassificationPredictionInstance(
        content=encoded_content,
    ).to_value()
    parameters = predict.params.ImageClassificationPredictionParams(
        confidence_threshold=0.0,
        max_predictions=5,
    ).to_value()

    response = client.predict(endpoint=endpoint, instances=[instance], parameters=parameters)

    if not response.predictions:
        raise ValueError("Vertex AI endpoint returned no predictions")

    # Image classification models return one prediction map per instance,
    # holding parallel displayNames/confidences arrays (not guaranteed sorted).
    prediction = dict(response.predictions[0])
    display_names = list(prediction["displayNames"])
    confidences = [float(c) for c in prediction["confidences"]]

    if not display_names:
        raise ValueError("Vertex AI endpoint returned an empty prediction")

    top_index = max(range(len(confidences)), key=lambda i: confidences[i])
    label = display_names[top_index]
    confidence = confidences[top_index]

    return {
        "classification": label,
        "confidence": confidence,
        "urgency": "high" if label.lower() in HIGH_URGENCY_LABELS else "low",
    }
