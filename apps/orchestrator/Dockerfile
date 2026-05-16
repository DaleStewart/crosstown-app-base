FROM python:3.11-slim AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY pyproject.toml ./
RUN pip install --prefix=/install --no-cache-dir \
    "fastapi>=0.110" "uvicorn[standard]>=0.27" "websockets>=12.0" "httpx>=0.27" \
    "pydantic>=2.5" "pydantic-settings>=2.2" "azure-identity>=1.15" \
    "azure-cosmos>=4.6" "openai>=1.30" "azure-cognitiveservices-speech>=1.37" \
    "azure-monitor-opentelemetry>=1.2" "aiohttp>=3.9"

FROM python:3.11-slim
RUN useradd --create-home --uid 10001 app
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . /app
RUN chown -R app:app /app
USER app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
