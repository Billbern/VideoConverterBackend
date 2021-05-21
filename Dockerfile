FROM ubuntu:bionic-20210416

USER root

RUN apt-get update


RUN apt-get -y --no-install-recommends install \
    build-essential \
    pkg-config 


RUN apt-get -y --no-install-recommends install \    
    python3.8 \
    python3-pip \
    python3.8-dev \
    python-dev \
    python3-dev

RUN apt-get -y --no-install-recommends install \ 
    gstreamer-1.0 \
    gstreamer1.0-dev \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-doc \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-pulseaudio \
    python-gst-1.0 \
    libgirepository1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libcairo2-dev \
    gir1.2-gstreamer-1.0 \
    python3-gi \
    python-gi-dev && rm -rf /var/lib/apt/lists/*


WORKDIR /mongconverter

COPY . /mongconverter

RUN python3 -m pip --proxy "http://192.168.1.154:8080" --no-cache-dir install --upgrade pip && \
    python3 -m pip --proxy "http://192.168.1.154:8080" --no-cache-dir install -r requirements.txt


EXPOSE 5000

# ENTRYPOINT [ "python3", "main.py" ]

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]