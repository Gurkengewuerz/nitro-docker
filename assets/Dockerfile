FROM node:lts-alpine as builder

ARG COMMIT=bd86e1f

WORKDIR /app

RUN apk add --no-cache git
RUN git clone --recurse-submodules https://github.com/billsonnn/nitro-converter.git .
RUN git switch -c habbo-room-content $COMMIT
RUN yarn install
RUN yarn build

ENTRYPOINT ["node", "/app/dist/Main.js"]