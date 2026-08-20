FROM python:3.11-slim

WORKDIR /app

# Copy source into temporary location to detect structure
COPY . /tmp/src/

# Handle both root build context and subfolder build context
RUN if [ -d /tmp/src/backend ]; then \
        cp -r /tmp/src/backend/* /app/ ; \
    else \
        cp -r /tmp/src/* /app/ ; \
    fi && \
    rm -rf /tmp/src

RUN pip install --no-cache-dir -r /app/requirements.txt

ENV PYTHONPATH=/app
ENV PORT=5000
EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120"]
