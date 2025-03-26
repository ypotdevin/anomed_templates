# alpine is not sufficient
FROM python:3.10-slim

RUN apt-get update && apt-get install -y nginx

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip3 install --requirement /tmp/requirements.txt

COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default

COPY anomed.py ./

# forward request and error logs to docker log collector
# (see https://serverfault.com/a/634296)
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# This needs to be ENTRYPOINT instead of CMD, to make sure the app will have PID
# 1 and receives signals from docker.
ENTRYPOINT ["/bin/sh", "-c", "gunicorn -D anomed && nginx -g 'daemon off;'"]

EXPOSE 80
