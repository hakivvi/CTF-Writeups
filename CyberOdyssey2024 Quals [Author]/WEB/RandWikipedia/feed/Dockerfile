FROM ruby:3.1

RUN gem install rack puma

WORKDIR /app

COPY config.ru .

EXPOSE 80

CMD ["puma", "-b", "tcp://0.0.0.0:9292", "-e", "prod", "-v"]
