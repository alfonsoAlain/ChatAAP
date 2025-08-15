#!/usr/bin/env bash
# build.sh - Script de build para Render con Django + Channels + Uvicorn

set -o errexit  # Detener ejecución si hay error
set -o nounset  # Fallar si una variable no está definida

echo "📦 Actualizando pip e instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄 Aplicando migraciones..."
python manage.py migrate --noinput

echo "🎨 Colectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "👤 Creando superusuario (si no existe)..."
python manage.py shell -c "import os; \
from django.contrib.auth import get_user_model; \
User = get_user_model(); \
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'); \
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'); \
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123'); \
User.objects.filter(username=username).exists() or User.objects.create_superuser(username, email, password)"

echo "✅ Build completado. Tu proyecto está listo para correr con Uvicorn."
