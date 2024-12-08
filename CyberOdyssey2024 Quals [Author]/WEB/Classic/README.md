# Details

a classic case of cross protocol SSRF using PHP's wrappers, in this case FTP (passive mode) to redirect the server to send a FCGI packet to PHP-FPM, grab the IP of the backend, since `PASV` does not support hostnames, then redirect the server again to send a `uwsgi` packet to `uwsgi` server.
