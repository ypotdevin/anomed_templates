# AnoMed Image Templates

In this repository we provide templates to derive Docker images from web
applications. You need such Docker images to submit them to the AnoMed platform.
In more detail, we will explain by example how to create Docker images based on

1. the [example challenge](https://github.com/ypotdevin/anomed_challenge) web
   application,
2. the [example anonymizer](https://github.com/ypotdevin/anomed_anonymizer) web
   application and
3. the [example deanonymizer](https://github.com/ypotdevin/anomed_deanonymizer)
   web application.

The presented procedures should be transferable to your specific use case.

Afterwards, we setup a simulation environment to let the corresponding Docker
containers interact among each other in a way that is similar to how they would
interact, if they would have been submitted to the AnoMed platform. Hopefully,
this will give you an intuition about the capabilities and the limitations of
the AnoMed platform.

## Prerequisites

- Your host machine needs a running [Docker
  engine](https://docs.docker.com/engine/).
- Resources, e.g. challenge data, need to be present on your local machine that
  you will use to Dockerize web applications. Containers submitted to the AnoMed
  platform won't have internet access. You will be given an opportunity to
  upload resources (a single (!) file, e.g. a `.zip` file) to the platform from your
  local machine.

## General Recommendations Regarding the Dockerization of Web Applications

Applications are dockerized by creating a suitable dockerfile. We do not
recommend cramming all commands and configurations into just the `Dockerfile`,
but to separate different aspects into different files. That is why in our
examples, there are also files like `entrypoint.sh` and `requirements.txt`. The
`entrypoint.sh` file handles the correct startup of the web server and the
`requirements.txt` states the pip dependencies of your challenge and will be
used during Docker image build time. If you're unfamiliar with Docker, first
work through [a tutorial](https://www.docker.com/101-tutorial/), as we will not
cover the basics here.

The web applications in our templates are expected to be served by a combination
of [GUnicorn](https://gunicorn.org/) and [nginx](https://nginx.org/). The
`entrypoint.sh` scripts and the `nginx.conf` configuration files are designed
for that situation. If you would like to deploy your web app differently, you
need to adjust to your case. But even if you stick to our recommendation, you
might have to adjust the setting of `client_max_body_size` within `nginx.conf`,
depending on how large requests might become given the challenge you are working
on / contributing to.

### Dockerizing a Challenge Web Application

Assuming that you have already developed a challenge web application (in this
example it is given in the Python file `./example_challenge/challenge.py`,
assigned to the `application` variable at the end of the script), the next step
is to define a suitable dockerfile. The dockerfile given at
`./example_challenge/Dockerfile` serves as an example. We will discuss it here
briefly.

We have good experience with the use of the python:3.10-slim base Docker image,
which is why we choose that base image by stating `FROM python:3.10-slim`.

Next we install dumb-init to handle signals better and also nginx which is not
part of the base image by default (`RUN apt-get update && apt-get install -y
dumb-init nginx`). If you plan to deploy using other software, you may avoid
installing nginx.

The command

```docker
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip3 install --requirement /tmp/requirements.txt
```

temporarily mounts the `requirements.txt` file (not copying it to the image) and
installs the mentioned requirements. If you have different dependencies from
those in our example, make sure to mention them all here – otherwise your
application will crash once the container is running.

The next two lines

```docker
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY challenge.py entrypoint.sh ./
```

replace the nginx default configuration by our template configuration, add the
challenge app (defined in `/example_challenge/challenge.py`) and the entry point
script to the image. If your module containing the web app has a different name,
or if you even use more modules, make sure to mention them in these lines.

Finally, the commands

```docker
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/entrypoint.sh", "challenge"]
```

tell to start the container using
[dumb-init](https://github.com/Yelp/dumb-init), for proper signal handling and
to execute our entry point script with one parameter (`"challenge"`): the name
of the module (without `.py` extension) containing the web application. Adjust
this if your module is named differently.

Assuming that you now have adjusting the dockerfile to your needs, only two more
steps are necessary. The first is to build the Docker image. We will use the
Docker engine to do so, more specifically, the [docker build
command](https://docs.docker.com/get-started/docker-concepts/building-images/build-tag-and-publish-an-image/):

```bash
cd example_challenge
docker build -t example_challenge:latest.
```

Having successfully build an image with name `example_challenge` and tag
`latest`, the last remaining step is to dump the image to a zipped file which
you then may submit to the AnoMed platform:

```bash
docker save example_challenge:latest | gzip > example_challenge_latest.tar.gz
```

### Dockerizing an Anonymizer/Deanonymizer Web Application

Dockerizing an anonymizer web app (or deanonymizer web app) is very similar to
dockerizing a challenge web app. Is you might have noticed, our (de)anonymizer
template setup is almost equal to the challenge template setup, except for a
different name of the python module and different packages in the
`requirements.txt`. So you may follow the steps of the previous section while
adjusting only file paths and image names.

## Simulation Environment

Due to the limited feedback you will receive from the AnoMed platform,
especially during development, you might be interested in simulating the
interaction of your container(s) prior to submission. We provide a Docker
compose file (`example-docker-compose.yaml`) which covers the most important
issues (special environment variables and volume mounts).

Another key feature of the simulation environment is the mock of the AnoMed
platform itself (`./anomed_mock/anomed.py`). It provides an API to submit
evaluation results to, just like there would be within the AnoMed platform – but
of course without a real effect (here, the provided evaluation records are just
mirrored back).

### Setup

To setup the simulation environment, you not only need a running Docker engine,
but also [Docker compose](https://docs.docker.com/compose/install/). Once it is
available, follow these steps:

1. Build all docker images and create (but not run) the corresponding
   containers: `docker compose -f example-docker-compose.yaml create`
2. Copy challenge resources to the accompanying challenge volume which was
   created by the previous command. Is this case do so by issuing `docker
compose -f example-docker-compose.yaml cp ./resources/iris.npz
example_challenge:persistent_data`. If your resources have a different name
   or format, adjust the command accordingly. As mentioned in the prerequisites
   section, you will be given the opportunity to upload a single resources file
   while contributing your challenge to the AnoMed platform. You may access that
   file from within your container through a docker volume, just like within this
   simulation environment.
3. Finally start the containers: `docker compose -f example-docker-compose.yaml
start`

### Testing Containers

To execute the following basic tests, make sure you have
[httpie](https://pypi.org/project/httpie/) available at your host machine (e.g.
install it via `pip install httpie`). We assume that you did not change the port
forwarding configuration of the `example-docker-compose.yaml` file, meaning that
the ports 8000, 8001, 8002 and 8003 forward to anomed_mock, example_challenge,
example_anonymizer and example_deanonymizer, respectively.

#### Testing Availability

To just check whether the web servers booted correctly and are available, issue
the following httpie command for the ports 8000 to 8003 respectively. You should
receive responses similar to this:

```bash
$ http localhost:8000
> HTTP/1.1 200 OK
> Connection: keep-alive
> Content-Length: 43
> Content-Type: application/json
> Date: Mon, 24 Mar 2025 15:33:54 GMT
> Server: nginx/1.22.1
>
> {
>     "message": "AnoMed mock server is alive!"
> }
```

#### Testing the Example Anonymizer

To test whether your anonymizer fits and evaluates successfully, your simulation
environment needs to contain a suitable challenge web server. Otherwise, your
anonymizer will not be able to pull fitting data and to use evaluation
functionality.

In this example, a suitable challenge server is present (which is then
indirectly tested trough the anonymizer). To test fitting, issue this command:

```bash
$ http --form post localhost:8002/fit
> HTTP/1.0 201 Created
> Date: Mon, 24 Mar 2025 15:43:57 GMT
> Server: WSGIServer/0.2 CPython/3.10.16
> content-length: 55
> content-type: application/json
>
> {
>     "message": "Fitting has been completed successfully."
> }
```

To test evaluation, issue this command:

```bash
$ http --form post localhost:8002/evaluate data_split==tuning
> HTTP/1.0 201 Created
> Date: Mon, 24 Mar 2025 15:45:17 GMT
> Server: WSGIServer/0.2 CPython/3.10.16
> content-length: 118
> content-type: application/json
>
> {
>     "evaluation": {
>         "accuracy": 0.5454545454545454
>     },
>     "message": "The anonymizer has been evaluated based on tuning data."
> }
```

#### Testing the Example Deanonymizer

To test whether your deanonymizer fits and evaluates successfully, your
simulation environment needs to contain a suitable challenge web server and also
a suitable anonymizer web server (the attack target). Otherwise, your
deanonymizer will not be able to pull fitting data, to use evaluation
functionality and to target the anonymizer.

In this example, a suitable challenge server and an anonymizer server are
present (which are then indirectly tested trough the deanonymizer). To test
fitting, issue this command:

```bash
$ http --form post localhost:8003/fit
> HTTP/1.0 201 Created
> Date: Mon, 24 Mar 2025 15:52:38 GMT
> Server: WSGIServer/0.2 CPython/3.10.16
> content-length: 55
> content-type: application/json
>
> {
>     "message": "Fitting has been completed successfully."
> }
```

To test evaluation, issue this command:

```bash
$ http --form post localhost:8003/evaluate data_split==tuning
> HTTP/1.0 201 Created
> Date: Mon, 24 Mar 2025 15:53:29 GMT
> Server: WSGIServer/0.2 CPython/3.10.16
> content-length: 124
> content-type: application/json
>
> {
>     "evaluation": {
>         "acc": 0.5,
>         "fpr": 0.5,
>         "tpr": 1.0
>     },
>     "message": "The deanonymizer has been evaluated based on tuning data."
> }
```
