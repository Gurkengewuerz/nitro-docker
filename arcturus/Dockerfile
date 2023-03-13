FROM maven:3-amazoncorretto-8 AS builder

ARG BRANCH=dev

RUN yum install -y git

WORKDIR /build/arcturus-community
RUN git clone --recurse-submodules https://git.krews.org/morningstar/Arcturus-Community.git .
RUN git checkout -b ${BRANCH}
RUN mvn package
RUN mvn install
RUN cp target/*-jar-with-dependencies.jar target/emulator.jar

WORKDIR /build/arcturus-ws
RUN git clone --recurse-submodules https://git.krews.org/nitro/ms-websockets.git .
RUN sed -i 's#<version>3.0.0</version>#<version>[1.0.0,)</version>#g' pom.xml
RUN mvn package
RUN cp target/NitroWebsockets-*.jar target/websockets.jar


WORKDIR /build/apollyon
RUN git clone --recurse-submodules https://git.krews.org/morningstar/archive/apollyon.git .
RUN sed -i 's#<version>3.0.0</version>#<version>[1.0.0,)</version>#g' pom.xml
RUN mvn package
RUN cp target/Apollyon-*.jar target/apollyon.jar

FROM amazoncorretto:8-alpine-jre

WORKDIR /app

RUN apk add --no-cache mariadb-client bash

COPY --from=builder /build/arcturus-community/sqlupdates /app/sqlupdates
COPY --from=builder /build/arcturus-community/target/emulator.jar /app/emulator.jar
RUN mkdir -p /app/plugins
COPY --from=builder /build/arcturus-ws/target/websockets.jar /app/plugins/websockets.jar
COPY --from=builder /build/apollyon/target/apollyon.jar /app//plugins/apollyon.jar

ENTRYPOINT ["/usr/bin/java", "-jar", "/app/emulator.jar"]