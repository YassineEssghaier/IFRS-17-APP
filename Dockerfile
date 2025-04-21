FROM python:3.11-slim
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y && pip install --upgrade pip && pip install -r requirements.txt
WORKDIR dashboard/
COPY app.py app.py
COPY assets/ assets/
COPY .streamlit/ .streamlit/
EXPOSE 8000
CMD streamlit run app.py --server.port 8000 --server.address '0.0.0.0'
