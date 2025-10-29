FROM node:lts-alpine as builder

WORKDIR '/app'
COPY package.json .
RUN npm install

COPY . .

RUN npm run build



FROM nginx
EXPOSE 8080
COPY --from=builder /app/build  /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf