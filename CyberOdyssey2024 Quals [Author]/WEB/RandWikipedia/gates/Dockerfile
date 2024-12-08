FROM nginx:alpine

RUN apk add --no-cache python3

COPY conf/nginx.conf /etc/nginx/nginx.conf
COPY conf/passwd /etc/nginx/passwd
COPY secondgate.py /usr/local/bin/secondgate.py
RUN ln -sf /proc/self/fd /dev/
RUN chmod +x /usr/local/bin/secondgate.py

CMD ["sh", "-c", "python3 /usr/local/bin/secondgate.py & nginx -g 'daemon off;'"]
