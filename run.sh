#!/bin/bash
set -e

echo "== Copying configs =="

if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env created"
fi

if [ ! -f judge0.conf ]; then
    cp judge0.conf.example judge0.conf
    echo "judge0.conf created"
fi

echo "== Preparing keys =="

mkdir -p keys

if [ ! -f keys/private.key ]; then
    echo "Generating LTI keys..."

    openssl genrsa -out keys/private.key 2048
    openssl rsa -in keys/private.key -pubout -out keys/public.key
fi

echo "== Building project =="

docker compose up --build -d

echo "== Done =="