FROM quay.io/kubespray/kpm:build
#FROM alpine:3.3

ARG workdir=/opt
ARG with_tests=true
ENV WITH_TESTS ${with_tests}

RUN rm -rf $workdir && mkdir -p $workdir
ADD . $workdir
WORKDIR $workdir
RUN apk --no-cache --update add python py-pip openssl ca-certificates git
RUN apk --no-cache --update add --virtual build-dependencies python-dev build-base wget openssl-dev libffi-dev \
    && pip install pip -U \
    && pip install gunicorn -U \
    && pip install -e .

RUN if [ "$WITH_TESTS" = true ]; then \
      pip install -r requirements_dev.txt -U ;\
    fi


CMD ["kpm"]
