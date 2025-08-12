#!/usr/bin/env bash
# build.sh - Script de build para Render con Django + Channels

set -o errexit  # Detener ejecución si hay error

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄 Migrando base de datos..."
python manage.py migrate --noinput

echo "🎨 Colectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Build completado."