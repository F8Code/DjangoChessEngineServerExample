# backend/Dockerfile

# Używamy obrazu Python
FROM python:3.10-slim

# Ustawiamy katalog roboczy
WORKDIR /app

# Kopiujemy plik z wymaganiami
COPY requirements.txt .

# Instalujemy wymagane biblioteki
RUN pip install -r requirements.txt

# Kopiujemy wszystkie pliki projektu
COPY . .

# Kopiujemy plik stockfish do odpowiedniego katalogu (jeśli jest potrzebny)
COPY stockfish/stockfish /app/stockfish/stockfish

# Uruchom migracje bazy danych i serwer Django
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8080"]