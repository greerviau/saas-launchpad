# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update

# Set the working directory inside the container
WORKDIR /app

RUN pip install uv

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Copy the entire application code to the working directory
COPY . .

EXPOSE 8000

# Copy the startup script
COPY start.sh .
RUN chmod +x start.sh

# Use the startup script as the CMD
CMD ["./start.sh"]
