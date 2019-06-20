FROM alpine:3.6

RUN apk add --update --no-cache --virtual=run-deps \
  python3 \
  git \
  uwsgi \
  uwsgi-http \
  uwsgi-python3 \
  ca-certificates

WORKDIR /opt/deployed

COPY requirements.txt /opt/deployed/requirements.txt.source
# Filter out pylint as it requires gcc
RUN grep -v pylint /opt/deployed/requirements.txt.source > /opt/deployed/requirements.txt
RUN pip3 install --no-cache-dir -r /opt/deployed/requirements.txt

COPY waylon /opt/deployed/waylon/
COPY settings.py /opt/deployed/
COPY iris_settings.py /opt/deployed/
COPY scripts/* /opt/deployed/
COPY *.sh /opt/deployed/

RUN chmod +x /opt/deployed/*.sh
RUN chmod +x /opt/deployed/run_*

ENV PYTHONPATH "${PYTHONPATH}:/opt/deployed"
