FROM python:3

RUN apt-get -qq -y update && apt-get -qq -y upgrade
RUN apt-get -qq -y install python-pip build-essential git
RUN apt-get -qq -y autoremove && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install -q --upgrade pip && pip install -q --upgrade setuptools zulip

COPY .zuliprc /root/
COPY . /app
WORKDIR /app
RUN git clone https://github.com/zulip/zulip.git

ENTRYPOINT python /app/zulip/tools/zulip-export/zulip-export --stream=$STREAM \ 
    && cp zulip-$STREAM.json /out/ \
    && python zulip2md/zulip2md.py --inf=zulip-$STREAM.json --out=/out/$TOPIC.md --topic=$TOPIC