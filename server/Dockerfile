# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /server

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server.py file into the container
COPY server.py .

# Expose the port the server runs on
EXPOSE 8080

# Command to run the server using uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]