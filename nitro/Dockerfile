FROM node:lts-alpine as builder

ARG BRANCH=dev

WORKDIR /build

RUN apk add --no-cache git
RUN git clone --branch ${BRANCH} --recurse-submodules https://github.com/billsonnn/nitro-react.git .
RUN yarn install
RUN yarn build



FROM nginx:alpine

COPY --from=builder /build/dist/ /usr/share/nginx/html/
