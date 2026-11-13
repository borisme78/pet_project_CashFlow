# Беремо готове середовище з Python
FROM python:3.12-slim

# Задаємо робочу папку всередині контейнера
WORKDIR /app

# Копіюємо список залежностей у робочу папку
COPY requirements.txt .

# Встановлюємо бібліотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо файли проєкту
COPY . .

# Запускаємо Flask
CMD ["python", "-m", "flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]
