import mlflow
from .model import load_model
from pathlib import Path


def log_model_run(name: str, model_path: str, metrics: dict):
    mlflow.set_experiment(name)
    with mlflow.start_run() as run:
        mlflow.log_metrics(metrics or {})
        # log model artifact (file or directory)
        p = Path(model_path)
        if p.exists():
            if p.is_dir():
                mlflow.log_artifacts(str(p))
            else:
                mlflow.log_artifact(str(p))
        return run.info.run_id


def log_current_model_metrics(metrics: dict):
    # utility to log metrics for currently loaded model path if available
    model = load_model()
    # cannot introspect path reliably; user should pass path
    mlflow.log_metrics(metrics)
