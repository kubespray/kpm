#FROM mhart/alpine-node:4.4
FROM registry.kubespray.io/kpm-ui:v0.0.2
MAINTAINER Antoine Legrand <2t.antoien@gmail.com>

ARG version=master
ARG workingdir=/opt/kpm-ui

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh build-base make python

RUN rm -rf $workingdir
RUN mkdir -p /root/.ssh
RUN ssh-keyscan gitlab.com >> /root/.ssh/known_hosts
COPY kubespray-build /root/.ssh/id_rsa
COPY kubespray-build.pub /root/.ssh/id_rsa.pub
RUN chmod 400 /root/.ssh/id_rsa

ENV KPMUI_ENV prod
RUN git clone git@gitlab.com:kubespray/kpm-ui.git $workingdir --depth=1 --branch=$version
WORKDIR $workingdir
RUN ln -s /usr/lib/node_modules/kpm-ui/node_modules/ $workingdir/node_modules
RUN npm update

RUN rm /root/.ssh/id_rsa

COPY docker-entrypoint.sh $workingdir/docker-entrypoint.sh
RUN chmod 755 $workingdir/docker-entrypoint.sh

CMD ["$workingdir/docker-entrypoint.sh"]
EXPOSE 8081
