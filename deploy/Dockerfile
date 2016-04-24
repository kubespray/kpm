FROM alpine:3.3

ARG version=0.14.1
ARG workdir=/opt
RUN rm -rf $workdir
RUN mkdir -p $workdir
COPY kpm-$version.tar.gz $workdir

WORKDIR $workdir
RUN tar xzvf kpm-$version.tar.gz
WORKDIR $workdir/kpm-$version

RUN apk --update add python py-pip openssl ca-certificates
RUN apk --update add --virtual build-dependencies python-dev build-base wget \
  && pip install gunicorn -U \
  && python setup.py install \
  && apk del build-dependencies


ENTRYPOINT ["gunicorn", "kpm.api.wsgi:app"]
CMD ["-b", ":5000", "--threads", "3", "-w", "1"]
EXPOSE 5000
