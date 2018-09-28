#!/bin/bash

sslfiles=/.../ssl/current

gunicorn -w 4 --certfile $sslfiles/ssl.crt --keyfile $sslfiles/ssl.key -b 0.0.0.0:5100 eduwallet_webserver:app

