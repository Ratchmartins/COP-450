FROM python:3.10-slim 
WORKDIR /app 
COPY . .
# Add this before you copy your requirements
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* 
# Force an update to the build tools to get the patched versions
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt 
CMD ["python", "app/app.py"] 

