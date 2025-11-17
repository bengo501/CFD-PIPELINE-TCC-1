#!/bin/bash

echo "========================================"
echo "   CFD PIPELINE - DOCKER SETUP"
echo "========================================"
echo

echo "[1/5] verificando docker..."
if ! command -v docker &> /dev/null; then
    echo "erro: docker não encontrado!"
    echo "instale docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "docker encontrado ✓"

echo
echo "[2/5] verificando docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "erro: docker-compose não encontrado!"
    exit 1
fi
echo "docker-compose encontrado ✓"

echo
echo "[3/5] criando arquivo .env..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "arquivo .env criado ✓"
else
    echo "arquivo .env já existe ✓"
fi

echo
echo "[4/5] parando containers existentes..."
docker-compose down

echo
echo "[5/5] iniciando containers..."
docker-compose up -d

echo
echo "========================================"
echo "   CONTAINERS INICIADOS!"
echo "========================================"
echo
echo "serviços disponíveis:"
echo "- frontend:    http://localhost:5173"
echo "- backend:     http://localhost:8000"
echo "- postgres:    localhost:5432"
echo "- redis:       localhost:6379"
echo "- minio:       http://localhost:9000"
echo "- minio admin: http://localhost:9001"
echo
echo "para ver logs: docker-compose logs -f"
echo "para parar:    docker-compose down"
echo
