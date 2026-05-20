#!/bin/bash

cp .env.example .env
cp judge0.conf.example judge0.conf

if [ ! -f keys/private.key ]; then
    echo "Generating LTI keys..."
    python3 backend/generate_keys.py
fi

docker-compose up --build -d
echo "Go to http://localhost/lti-key to get your public key for Moodle."