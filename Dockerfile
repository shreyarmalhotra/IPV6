# syntax=docker/dockerfile:1
FROM node:12-alpine
RUN apk add --no-cache python2 g++ make
WORKDIR /IPV6
COPY . .
RUN yarn install --production
CMD ["node", "templates/index.html"]
EXPOSE 3000