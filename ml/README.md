# ML service

This folder contains model training, inference, and evaluation pipelines. The ML service is intentionally independent from the backend API and exposes an inference API (REST/gRPC) for low-latency scoring.

Structure:
- `data/` — raw and processed datasets
- `preprocessing/` — data cleaning scripts
- `features/` — feature engineering
- `recommendation/` — content + CF training code
- `disease_prediction/` — model training scripts
- `inference/` — model wrappers and inference server
- `models/` — saved artifacts
