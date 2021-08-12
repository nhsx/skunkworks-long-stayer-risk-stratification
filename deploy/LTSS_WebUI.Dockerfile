FROM node:lts-alpine as vue-build

WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
ENV NODE_ENV production

COPY webui/package.json /app/package.json
RUN npm install --silent

COPY webui/ /app
RUN npm run build

FROM nginx:1.19.10-alpine
COPY --from=vue-build /app/dist /usr/share/nginx/html
COPY /deploy/ltss.nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8090
CMD ["nginx", "-g", "daemon off;"]
