# Start with a standard Python base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your requirements and install them
COPY requirements.txt .

# --- THE NEW FIX IS HERE ---
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --default-timeout=2000 -r requirements.txt
# --------------------------

# Copy ALL your files into the container
COPY . .

# Expose the port FastAPI uses
EXPOSE 8000

# The command to start the API when the container boots up
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]