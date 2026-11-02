"""
DEMO ML ADAPTER

This file is a safe placeholder so the frontend/backend can be built before
your teammate's model is ready. It does NOT infer anemia, blood loss, or a
clinical risk score.

When your teammate is ready, agree on:
1. Exact input feature names and units.
2. The preprocessing used during training.
3. Model file/runtime and prediction output schema.
4. How the model was clinically validated.

Then replace get_demo_assessment() with a call to the actual model. Do not
present an unvalidated model output as a medical diagnosis.
"""


def get_demo_assessment(latest_reading: dict) -> dict:
    return {
        "mode": "demo_placeholder",
        "prediction": None,
        "risk_score": None,
        "model_version": "not-connected",
        "message": (
            "The ML model is not connected yet. This demo does not diagnose "
            "anemia or detect blood loss. Use appropriate clinical assessment "
            "and testing for concerns about anemia."
        ),
        "input_reading_id": latest_reading.get("id"),
    }
