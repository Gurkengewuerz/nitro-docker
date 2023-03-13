FROM node:lts-alpine as builder

WORKDIR /app

RUN apk add --no-cache git
RUN git clone --recurse-submodules https://github.com/billsonnn/nitro-converter.git .
RUN git checkout -b habbo-room-content
RUN yarn install
RUN yarn build

ENTRYPOINT ["node", "/app/dist/Main.js"]