FROM debian:10 AS builder

RUN apt-get update \
 && apt-get install -y \
    build-essential autoconf autoconf-archive automake coreutils libtool gettext git ncurses-dev texinfo texlive libwxgtk3.0-dev

RUN apt-get install -y \
    tmux xvfb x11vnc ffmpeg libwxgtk3.0-gtk3-dev

WORKDIR /logo

RUN git clone https://github.com/jrincayc/ucblogo-code /logo

RUN autoreconf --install \
    && ./configure \
    && make \
    && make install

RUN apt-get install -y \
    x11-apps imagemagick ghostscript xdotool bc

COPY entrypoint.sh /logo/

VOLUME [ "/input", "/output" ]

ENTRYPOINT [ "/logo/entrypoint.sh" ]
