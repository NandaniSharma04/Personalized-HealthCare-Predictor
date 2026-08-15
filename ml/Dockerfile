FROM python:3.11-slim
WORKDIR /ml
COPY ml/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ml/ .
CMD ["uvicorn", "inference.server:app", "--host", "0.0.0.0", "--port", "8500"]
