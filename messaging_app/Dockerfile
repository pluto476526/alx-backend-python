# Use Python 3.10 as base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /messaging_app

# Install dependencies
COPY Requirements.txt /messaging_app/
RUN pip install --upgrade pip
RUN pip install -r Requirements.txt

# Copy project code
COPY . /messaging_app/

# Expose port 8000
EXPOSE 8000

# Default command to run Django dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

