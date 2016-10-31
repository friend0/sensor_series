FROM continuumio/miniconda3:latest
MAINTAINER Ryan Rodriguez <ryarodriguez@tesla.com>

ADD ./environment.yml environment.yml

# update conda and setup environment
RUN conda update conda -y \
    && conda install pyyaml \
    && conda env create -f environment.yml

ENV PATH /opt/conda/envs/panopticon/bin:$PATH

EXPOSE 5000

ADD ./gritty_soap /panopticon/gritty_soap
ADD ./panopticon /panopticon/panopticon
ADD ./web /panopticon/web
ADD OpcXMLDaServer.asmx /panopticon/OpcXMLDaServer.asmx
ADD setup.py panopticon/setup.py

RUN cd panopticon && python setup.py install
WORKDIR /panopticon/web
RUN ls

#CMD [ "python /panopticon/app.py" ]