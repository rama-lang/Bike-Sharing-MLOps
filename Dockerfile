FROM python:3.9-slim
WORKDIR /app
# మెయిన్ ఫోల్డర్ లోనే requirements.txt ఉండాలి
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]