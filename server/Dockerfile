# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /server

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server.py file and the lib folder into the container
COPY server.py .
COPY lib ./lib

# Expose the port the server runs on
EXPOSE 8080

# Set PYTHONPATH to include the /server directory
ENV PYTHONPATH=/server

# Command to run the server using uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]