# Etap 1: budowanie aplikacji (Node.js jest potrzebny tylko tutaj)
FROM node:22-alpine AS build

WORKDIR /app

# Adres API wstawiany przez Vite do kodu przy budowaniu. Zapytania wysyła przeglądarka
# użytkownika, a nie kontener, więc to adres API widziany z hosta, a nie http://api:8000.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Etap 2: serwowanie zbudowanych plików statycznych
FROM nginx:1.28-alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
