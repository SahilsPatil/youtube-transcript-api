#!/bin/bash

#gunicorn -w 4 -b 0.0.0.0:5000 --timeout 500 app:app
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 500 app:app --log-level=debug --access-logfile=- --error-logfile=-
