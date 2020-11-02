FROM python:latest
COPY demucshttpservice.py config.yml /app
WORKDIR /app
RUN apt-get update -y && pip3 install nameko
#TODO: Add EXPOSE port
CMD ["nameko","run", "subsservice", "--config config.yml"]
