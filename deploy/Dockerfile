FROM python:2.7

ARG version=v0.12.1
ARG workdir=/opt/kpm

RUN rm -rf $workdir

RUN git clone https://github.com/kubespray/kpm.git $workdir --depth=1 --branch=$version

WORKDIR $workdir

RUN pip install -r requirements.txt -U
RUN pip install gunicorn -U
RUN python setup.py install

ENTRYPOINT ["gunicorn", "kpm.api.wsgi:app"]
CMD ["-b", ":5000", "--threads", "3", "-w", "1"]
EXPOSE 5000
