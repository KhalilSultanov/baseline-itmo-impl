# FastAPI сервис с OpenAI и Docker

## Описание проекта

Финальный проект для МегаШколы по направлению ИИ.

---

## Установка и запуск

### 1. Установка зависимостей

Для локального запуска установи Python 3.10 и активируй виртуальное окружение:

```sh
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Запуск локально (без Docker)

```sh
uvicorn main:app --host localhost --port 8080 --reload
```

API будет доступно по адресу: [http://localhost:8080/docs](http://localhost:8080/docs)

---

## Запуск в Docker

### 1. Собрать и запустить контейнер

```sh
docker-compose up --build -d
```

### 2. Проверить, запущен ли контейнер

```sh
docker-compose ps
```

API будет доступно по адресу: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)

### 3. Остановить контейнер

```sh
docker-compose down
```

---

## Работа с API

### 1. Получить Swagger-документацию

Перейди в браузере: [http://localhost:8080/docs](http://localhost:8080/docs)

### 2. Отправить POST-запрос в API

#### **Запрос локально:** `localhost:8080/api/request`
#### **Запрос на сервер:** `158.160.58.54:8080/api/request`

```json
{
  "id": 1,
  "query": "Какой факультет в Университете ИТМО отвечает за направление AI?"
}
```

#### **Ответ:**

```json
{
    "id": 1,
    "answer": "Факультет программной инженерии и компьютерных технологий",
    "reasoning": "Этот факультет ведет курсы по искусственному интеллекту и машинному обучению. Ответ сгенерирован моделью GPT4o.",
    "sources": ["https://itmo.ru"]
}
```