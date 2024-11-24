FROM python:latest
EXPOSE 5000
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Create a virtual environment
RUN python -m venv .venv

# Install dependencies
RUN   pip install -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Set the entrypoint to run the Flask app
CMD [ "flask","run", "--debug", "--host", "0.0.0.0"]
