# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:15-buster-slim


WORKDIR /app

COPY package*.json /app/

RUN npm install

COPY ./ /app/

ARG FRONTEND_ENV=production

ENV VUE_APP_ENV=${FRONTEND_ENV}

# Comment out the next line to disable tests
#RUN npm run test:unit

RUN npm run build

