FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install auto-po-lyglot

COPY ./src/auto_po_lyglot/po_streamlit.py .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "po_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
