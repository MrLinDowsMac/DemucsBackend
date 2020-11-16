FROM python:latest
ENV SENDGRID_KEY ""
COPY sendmailservice.py /app/
WORKDIR /app/
RUN apt-get update -y \
    && pip3 install nameko \
    && pip3 install nameko-sendgrid
CMD ["nameko","run", "sendmailservice", "--config", "config.yml"]