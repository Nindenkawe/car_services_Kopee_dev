# Use a specific Python version for stability and reproducibility
FROM python:3.11-slim-buster

# Set a clear working directory
WORKDIR /car_services

# Copy requirements.txt first for efficient caching
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Expose the port for external access
EXPOSE 7000

# Specify the user for enhanced security (optional)
# USER non-root-user  # Replace with a non-root user if applicable

# Run the FastAPI app using a more robust command format
CMD ["cd kopee""uvicorn", "--host", "0.0.0.0", "--port", "7000", "main:kopee"]