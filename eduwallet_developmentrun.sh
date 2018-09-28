#!/bin/bash

export FLASK_APP=eduwallet_webserver.py
export FLASK_DEBUG=1

./eduwallet_webserver.py
# flask run --host=0.0.0.0 --port=5100

