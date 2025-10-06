FROM node:20-slim as builder

ARG BRANCH=dev
ARG COMMIT=7ff2405

WORKDIR /app

RUN apt-get update && apt-get install -y \
        git \
        build-essential \
        python3 \
        libcairo2-dev \
        libpango1.0-dev \
        libjpeg-dev \
        libgif-dev \
        librsvg2-dev \
    && rm -rf /var/lib/apt/lists/*
    
RUN apt remove apt --autoremove -y --allow-remove-essential

RUN git clone --branch ${BRANCH} --recurse-submodules https://github.com/billsonnn/nitro-imager.git .
RUN git checkout $COMMIT

# Fix the library.parts issue before building
RUN node -e " \
  const fs = require('fs'); \
  const file = 'src/avatar/AvatarAssetDownloadManager.ts'; \
  let content = fs.readFileSync(file, 'utf8'); \
  \
  content = content.replace( \
    /([ \t]*)for\(const part of library\.parts\)/, \
    '\$1if(!library.parts || !Array.isArray(library.parts)) continue;\n\$1for(const part of library.parts)' \
  ); \
  \
  fs.writeFileSync(file, content, 'utf8'); \
  console.log('✓ Fixed library.parts check in AvatarAssetDownloadManager.ts'); \
"

RUN yarn install
RUN yarn build

ENTRYPOINT ["node", "/app/dist/src/main.js"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]