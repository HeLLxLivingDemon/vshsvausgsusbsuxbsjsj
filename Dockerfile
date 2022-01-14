FROM debian:latest
RUN apt-get update && apt-get upgrade -y
RUN apt-get install ffmpeg -y
RUN curl -sL https://deb.nodesource.com/setup_15.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g npm@7.22.0
COPY . /app/
WORKDIR /app/
RUN pip3 install -U pip
RUN pip3 install -U -r requirements.txt
CMD python3 -m oda
