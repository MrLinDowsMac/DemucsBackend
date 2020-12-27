FROM python:latest
ENV RABBITMQ_HOST 127.0.0.1:5672
ENV RABBITMQ_USER guest
ENV RABBITMQ_PASSWORD guest
ENV FLASK_ENV production
ENV FLASK_APP demucshttpservice.py
RUN mkdir -p /app
COPY demucshttpservice.py /app/
WORKDIR /app/
RUN apt-get update -y && pip3 install nameko & pip3 install flask-restx
EXPOSE 5000
CMD ["flask","run"]
