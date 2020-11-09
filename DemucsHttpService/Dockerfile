FROM python:latest
ENV RABBITMQ_HOST 127.0.0.1:5672
ENV RABBITMQ_USER guest
ENV RABBITMQ_PASSWORD guest
RUN mkdir -p /app
COPY demucshttpservice.py config.yml /app/
WORKDIR /app/
RUN apt-get update -y && pip3 install nameko
EXPOSE 8000
CMD ["nameko","run", "demucshttpservice", "--config", "config.yml"]
