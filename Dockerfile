FROM python:3.12-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Créer un utilisateur non-root
RUN useradd -m appuser

WORKDIR /app

# Copier uniquement requirements.txt pour utiliser le cache
COPY requirements.txt .

# Installer dépendances système et Python
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    python3-dev \
    && pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --progress-bar off -r requirements.txt \
    && apt-get purge -y build-essential pkg-config python3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copier le reste du projet
COPY . .

# Changer les permissions
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8090"]
