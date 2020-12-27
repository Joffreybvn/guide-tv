FROM python:3.8-slim-buster

# Install the security updates.
RUN apt-get update
RUN apt-get -y upgrade

# Install the required dependencies.
RUN apt-get install -y xmltv

# Remove all cached file. Get a smaller image.
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Copy the application.
COPY . /opt/app
WORKDIR /opt/app

# Install python dependencies.
RUN pip install -r requirements.txt

# Configure the TV grabber
RUN echo "all" | ./assets/tv_grab_fr_telerama --configure

# Start the app.
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]