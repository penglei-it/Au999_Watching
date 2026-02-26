# 本地构建 Buildozer 环境（当无法拉取预构建镜像时）
# 使用: docker build -t goldmonitor-builder . && docker run --rm -v "c:\Au999_Watching:/src" -w /src/mobile goldmonitor-builder android debug

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    build-essential git zip unzip \
    libncurses5-dev libffi-dev libssl-dev libsqlite3-dev \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages buildozer cython

WORKDIR /src
CMD ["buildozer", "android", "debug"]
