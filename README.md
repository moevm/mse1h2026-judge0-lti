# Платформа для решения задач по программированию

## Установка и запуск

### Требования 

- Docker
- docker-compose

### Инструкции по установке и запуску проекта.

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/moevm/mse1h2026-judge0-lti.git
    cd mse1h2026-judge0-lti

2. Создать и заполнить конфигурационные файл .env по примеру .env.example и файл judge0.conf по примеру judge0.conf.example.

3. Запуск впервые
    ```
    chmod +x build-and-run.sh
    ./build-and-run.sh
    ```

    ИЛИ

    ```
    docker-compose up --build -d
    ```

* Для проверки работы проекта предусмотрен упрощённый запуск:
    ```
    chmod +x start-example.sh
    ./start-example.sh
    ```

4. Выключение 
    ```
    docker-compose down 
    ```

## Проверка работоспособности
Инструкции по проверке работоспособности проекта (основной функциональности и результатов).

1. Установить и запустить проект.

2. Перейти на localhost. 

3. Попробовать решить задание и нажать кнопку "Проверить".

## Дополнительная информация

### Стэк технологий 
- Python
- FastAPI
- Pytest
- TypeScript
- React
- SASS
- React-Query
- PostgreSQL
- SQLAlchemy
- Redis
- Docker
- docker-compose
- judge0 