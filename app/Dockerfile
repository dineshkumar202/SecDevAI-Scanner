FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Do not bake secrets into images. GEMINI_API_KEY is passed as an env var by K8s.
ENV GEMINI_API_KEY=""

# Use gunicorn in production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app", "--workers", "2"]
