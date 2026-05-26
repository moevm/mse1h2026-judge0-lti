#!/bin/bash

cp .env.example .env
cp judge0.conf.example judge0.conf

mkdir -p keys

if [ ! -f keys/private.key ]; then
    echo "Generating LTI keys..."
    openssl genrsa -out keys/private.key 2048
    openssl rsa -in keys/private.key -pubout -out keys/public.key
fi

docker compose up --build -d

echo "Go to http://localhost/lti-key to get your public key for Moodle."