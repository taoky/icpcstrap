FROM ubuntu:22.04

# no ca-certificates inside :(
ARG APT_SOURCE=http://mirrors.ustc.edu.cn
ENV APT_SOURCE=$APT_SOURCE

RUN sed -Ei "s,https?://(archive|security)\.ubuntu\.com,$APT_SOURCE,g" /etc/apt/sources.list && \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends \
        binwalk casper genisoimage live-boot live-boot-initramfs-tools squashfs-tools xorriso \
        rsync curl ca-certificates && \
    apt-get clean

CMD ["/srv/icpcstrap"]
