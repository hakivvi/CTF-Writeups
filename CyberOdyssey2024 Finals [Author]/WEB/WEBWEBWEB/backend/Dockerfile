FROM python:3.11-slim

RUN useradd -m web
RUN mkdir /app && chown web:web /app
RUN echo "ODYSSEY{|_+_WEB_WAB_WOB_+_|}" > /flag_$(openssl rand -hex 40)

USER web
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY --chown=web:web src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=web:web src/ .

EXPOSE 8000

CMD ["bash", "/app/run.sh"]
