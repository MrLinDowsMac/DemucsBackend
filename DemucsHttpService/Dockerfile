FROM python:latest
RUN mkdir -p /app
COPY demucshttpservice.py config.yml /app
WORKDIR /app/
RUN apt-get update -y && pip3 install nameko
EXPOSE 80
CMD ["nameko","run", "demucshttpservice", "--config", "config.yml"]
