FROM ubuntu:18.04
RUN apt-get update
RUN apt-get -y install wget
RUN apt-get -y install vim
RUN apt-get -y install less
RUN apt-get -y install python-minimal
RUN apt-get -y install emboss
RUN wget https://serratus-public.s3.amazonaws.com/rce/serratax/tarball/serratax.tar.gz
RUN tar -zxvf serratax.tar.gz
RUN mv serratax_lib/* /usr/local/bin
ENV SERRATAX_REFDIR /serratax_ref
ENV SERRATAX_LIBDIR /usr/local/bin
COPY bash_include /root
RUN cat /root/bash_include >> /root/.profile
RUN cat /root/bash_include >> /root/.bashrc
COPY .vimrc /root
CMD serratax
