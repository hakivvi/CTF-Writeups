FROM node:18

RUN echo "ODYSSEY{!_______BR1NG_0UR_SQL}" > /flag.txt

RUN useradd -m web
RUN mkdir /app && chown web:web /app

RUN apt-get update && apt-get install -y tini && apt-get clean

USER web
WORKDIR /app

COPY --chown=web:web app.js .
RUN npm install express mysql

EXPOSE 1337
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["node", "app.js"]

