# Use an official Python base image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code and CSV
COPY app.py .
COPY animals.csv .

# Expose Flask's default port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]