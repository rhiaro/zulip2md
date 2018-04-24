FROM python:3

RUN apt-get -qq -y update && apt-get -qq -y upgrade
RUN apt-get -qq -y install python-pip build-essential git
RUN apt-get -qq -y autoremove && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install -q --upgrade pip && pip install -q --upgrade setuptools zulip

ARG stream

COPY .zuliprc ~/
WORKDIR /app
RUN git clone git@github.com:zulip/zulip.git
RUN python zulip/tools/zulip-export/zulip-export --stream=$stream
