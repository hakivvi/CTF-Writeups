FROM node:18

RUN useradd -m web
RUN mkdir /app && chown web:web /app

USER web
WORKDIR /app

COPY --chown=web:web app/package.json app/package-lock.json ./

RUN npm install

COPY --chown=web:web app/ .

EXPOSE 3000

RUN npm run build
RUN npm install serve

CMD ["bash", "/app/run.sh"]
