#!/bin/bash

# توحيد ملفات Docker
mv src/Dockerfile_from_core src/Dockerfile

# تحديث إعدادات Kubernetes
kustomize build deployments/k8s/production | kubectl apply -f - 