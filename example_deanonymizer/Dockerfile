# alpine is not sufficient
FROM python:3.10-slim

RUN apt-get update && apt-get install -y dumb-init nginx

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip3 install --requirement /tmp/requirements.txt

COPY nginx.conf /etc/nginx/conf.d/default.conf
# adjust this to your needs
COPY deanonymizer.py entrypoint.sh ./

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
# adjust this to your needs
CMD ["/entrypoint.sh", "deanonymizer"]

EXPOSE 80
