# The build-stage image:
FROM continuumio/miniconda3 AS build
#TODO: Add env variables to set cpu or gpu? 
#Apparently Docker now supports running gpus, check how run environment properly inside container.
COPY demucs/environment-cpu.yml  .
RUN ["conda" ,"env", "update", "-f", "environment-cpu.yml"]

# Install conda-pack:
RUN conda install -c conda-forge conda-pack

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n demucs -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack


# The runtime-stage image; we use Alpine-based
# base image since the Conda env also includes Python
# for us and is a bit more lightweight than Debian.
FROM python:3.8.7-alpine3.12 AS runtime
ENV RABBITMQ_HOST 127.0.0.1:5672
ENV RABBITMQ_USER guest
ENV RABBITMQ_PASSWORD guest

RUN mkdir -p /app/models/

ENV TRAINED_MODELS_PATH /app/models/

# Copy /venv from the previous stage:
COPY --from=build /venv /venv
COPY demucs/ remote_call_demucs_service.py config.yml separate.sh /app/
#WORKDIR /app/models/
#Downloads pretrained models to avoid using -dl parameter at running time.
#Takes a lot of time and makes a very big image size, hope can find an alternative
#RUN wget --progress=bar:force:noscroll "https://dl.fbaipublicfiles.com/demucs/v2.0/demucs.th" \
#&& wget --progress=bar:force:noscroll "https://dl.fbaipublicfiles.com/demucs/v2.0/demucs.th.gz" \
#&& wget --progress=bar:force:noscroll "https://dl.fbaipublicfiles.com/demucs/v2.0/demucs_extra.th" \
#&& wget --progress=bar:force:noscroll "https://dl.fbaipublicfiles.com/demucs/v2.0/demucs_extra.th.gz" \
#&& wget --progress=bar:force:noscroll "https://dl.fbaipublicfiles.com/demucs/v2.0/light.th" \
#&& wget --progress=bar:force:noscroll "https://dl.fbaipublicfiles.com/demucs/v2.0/light.th.gz" \
#&& wget --progress=bar:force:noscroll "https://dl.fbaipublicfiles.com/demucs/v2.0/light_extra.th" \
#&& wget --progress=bar:force:noscroll "https://dl.fbaipublicfiles.com/demucs/v2.0/light_extra.th.gz" \
#&& wget --progress=bar:force:noscroll "https://dl.fbaipublicfiles.com/demucs/v2.0/tasnet.th" \
#&& wget --progress=bar:force:noscroll "https://dl.fbaipublicfiles.com/demucs/v2.0/tasnet_extra.th"
VOLUME  /data 
WORKDIR /app
RUN apk add zip bash gcc musl-dev g++
SHELL ["/bin/bash", "-c"]
RUN ["pip" ,"install", "nameko"]

ENTRYPOINT source /venv/bin/activate && \
    nameko run remote_call_demucs_service --config config.yml