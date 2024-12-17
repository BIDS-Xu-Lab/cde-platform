FROM node:18-alpine

WORKDIR /app

COPY ./web/package*.json ./

RUN npm install 