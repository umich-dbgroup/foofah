# Use an official Python runtime as a parent image
FROM python:2.7-slim

# Set the working directory to /app
WORKDIR .

# Copy the current directory contents into the container at /app
ADD . .

# Install any needed packages specified in requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc musl-dev \
       build-essential \
       libboost-all-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r requirements.txt \
    && python boost_setup.py install \
    && apt-get purge -y --auto-remove gcc \ 
       musl-dev \
       build-essential

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
# ENV NAME Foofah

# Run app.py when the container launches
CMD ["python", "foofah_server.py"]