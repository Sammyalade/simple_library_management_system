# Use Python image
FROM python:3.11

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Run the server
CMD ["gunicorn", "-b", "0.0.0.0:8000", "frontend.wsgi:application"]
