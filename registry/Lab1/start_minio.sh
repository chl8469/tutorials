#!/bin/bash

docker run \
   -d \
   --network host \
   --name minio \
   -v ~/docker_volume/minio/data:/data \
   -e MINIO_ACCESS_KEY=test_access_key \
   -e MINIO_SECRET_KEY=test_secret_key \
   -e MINIO_ROOT_USER=test_user_id \
   -e MINIO_ROOT_PASSWORD=test_user_password \
   quay.io/minio/minio server /data --console-address ":9090"
