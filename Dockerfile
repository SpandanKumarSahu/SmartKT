FROM ubuntu:16.04

ENV HTTP_PROXY "http://172.16.2.30:8080"
ENV HTTPS_PROXY "http://172.16.2.30:8080"
ENV http_proxy "http://172.16.2.30:8080"
ENV https_proxy "http://172.16.2.30:8080"
ENV HTTP_PROXY=http://172.16.2.30:8080
ENV HTTPS_PROXY=http://172.16.2.30:8080
ENV http_proxy=http://172.16.2.30:8080
ENV https_proxy=http://172.16.2.30:8080
ENV NO_PROXY "127.0.0.1, localhost"

COPY DockerHelpers/apt.conf /etc/apt/apt.conf.d/proxy.conf

# Install dependencies
RUN apt-get -qq update; \
    apt-get install -qqy --no-install-recommends \
        autoconf automake cmake dpkg-dev file git make patch curl \
        libc-dev libc++-dev libgcc-5-dev libstdc++-5-dev  \
        dirmngr gnupg2 lbzip2 wget xz-utils git;

# Signing keys
RUN curl -k https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | apt-key add -

# Version info
ENV LLVM_RELEASE 6
ENV LLVM_VERSION 6.0.1

# Install Clang and LLVM
COPY DockerHelpers/install.sh .
RUN chmod +x install.sh
RUN ./install.sh

# Copy SmartKT codes
RUN mkdir -p workspace
WORKDIR workspace
COPY . .

# Install dependencies
RUN apt-get update
RUN apt-get install -qqy python python-pip vim
RUN chmod +x *
RUN ./install_dependencies.sh

# EXPOSE
EXPOSE 5000
EXPOSE 5001
EXPOSE 7000
EXPOSE 7777

RUN git clone https://github.com/glennrp/libpng.git projects/libpng 

# Specify the dependencies of the project
RUN apt-get install zlib1g-dev

RUN python initialize.py projects/libpng
CMD python examine.py clean libpng comments/Identifier/program_domain.csv comments/ProblemDomains/libpng/problem_domain.txt projects/libpng/build/pngtest projects/libpng/pngtest.png
