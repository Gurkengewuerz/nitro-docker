FROM node:lts-alpine as builder

ARG BRANCH=dev

WORKDIR /build

RUN apk add --no-cache git
RUN git clone --recurse-submodules https://github.com/billsonnn/nitro-react.git .
RUN git checkout -b ${BRANCH}
RUN yarn install
RUN yarn build



FROM nginx:alpine

COPY --from=builder /build/build/ /usr/share/nginx/html/
