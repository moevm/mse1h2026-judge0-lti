#!/bin/bash

cp .env.example .env
cp judge0.conf.example judge0.conf 

docker-compose up --build -d