# Course Recommendation System — Production Dockerfile
# Streamlit app on port 7860 | Cosine Similarity only
FROM python:3.10-slim

WORKDIR /app

# Install curl (needed for health check) and clean up
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache-friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application source code ──
COPY src/ ./src/

# ── Only the files the app actually needs at runtime ──
# course_data_original.pkl  ~38 MB   (display data)
# similarity_topk.pkl       ~11 MB   (recommendation index)
# tfidf_vectorizer.pkl      ~0.2 MB  (search engine)
# tfidf_matrix.pkl          ~20 MB   (search engine)
# NOT included: combined_features.pkl (~619 MB, training only)
COPY data/processed/course_data_original.pkl  ./data/processed/
COPY data/processed/similarity_topk.pkl       ./data/processed/
COPY data/processed/tfidf_vectorizer.pkl      ./data/processed/
COPY data/processed/tfidf_matrix.pkl          ./data/processed/

# ── Streamlit config ──
# Disable telemetry and usage stats collection
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV PYTHONUNBUFFERED=1

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "src/app/streamlit_app.py", \
    "--server.port=7860", \
    "--server.address=0.0.0.0"]
