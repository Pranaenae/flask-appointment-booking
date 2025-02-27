FROM python:3.13-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of application code
COPY . .

# Expose port 5000
EXPOSE 5000

# Run Flask 
CMD ["flask","--app", "app/main" , "run", "--host", "0.0.0.0"]
