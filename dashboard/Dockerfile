FROM python:3.13-slim

# Set the working directory in the container
#WORKDIR /dashboard
COPY . .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501"]