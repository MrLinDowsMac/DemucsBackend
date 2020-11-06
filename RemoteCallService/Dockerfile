FROM continuumio/miniconda3
COPY demucs/ subsservice.py config.yml /app
WORKDIR /app

VOLUME /app/models/
WORKDIR /app/models/
#Checks if attached volume contains models, otherwise downloads pretrained models to avoid using -dl parameter at running time.
RUN [[ ! "$(ls -A /app/models/*.th* 2>/dev/null )" ]] 
&& wget "https://dl.fbaipublicfiles.com/demucs/v2.0/demucs.th"
&& wget "https://dl.fbaipublicfiles.com/demucs/v2.0/demucs.th.gz"
&& wget "https://dl.fbaipublicfiles.com/demucs/v2.0/demucs_extra.th"
&& wget "https://dl.fbaipublicfiles.com/demucs/v2.0/demucs_extra.th.gz"
&& wget "https://dl.fbaipublicfiles.com/demucs/v2.0/light.th"
&& wget "https://dl.fbaipublicfiles.com/demucs/v2.0/light.th.gz"
&& wget "https://dl.fbaipublicfiles.com/demucs/v2.0/light_extra.th"
&& wget "https://dl.fbaipublicfiles.com/demucs/v2.0/light_extra.th.gz"
&& wget "https://dl.fbaipublicfiles.com/demucs/v2.0/tasnet.th"
&& wget "https://dl.fbaipublicfiles.com/demucs/v2.0/tasnet_extra.th"
WORKDIR /app
#TODO: Add env variables to set cpu or gpu
RUN ["conda" ,"env", "update", "-f", "environment-cpu.yml"]
#TODO: Perhaps it doesn't work out of the box, i just activated conda env by manually 
#conecting to the container.
SHELL ["/bin/bash","-c"]
RUN conda activate demucs && pip3 install nameko
CMD ["nameko","run", "subsservice", "--config config.yml"]
