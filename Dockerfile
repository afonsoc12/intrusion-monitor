FROM python:3.7-alpine

ARG VERSION="n/a"

LABEL VERSION=${VERSION}

MAINTAINER Afonso Costa

WORKDIR /src

COPY . .

RUN echo -e "def get_versions():\n    return {'version': '${VERSION}', 'full-revisionid': 'n/a', 'date': 'n/a', 'dirty': 'n/a', 'error': 'n/a'}" \
    > intrusion_monitor/_version.py

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install .

#EXPOSE 7007

ENTRYPOINT [ "python", "-m", "intrusion_monitor" ]