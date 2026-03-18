from app.database.models import User, Module, Task, ModuleTaskOrder, Language, TaskLanguage, Solution, Attempt, UserTypeEnum
from sqlalchemy.orm import Session


def insert_languages(db: Session) -> list[Language]:
    languages = [
        Language(id=1, language="python"),
        Language(id=2, language="javascript"),
        Language(id=3, language="java"),
    ]
    db.add_all(languages)
    db.flush()
    return languages


def insert_users(db: Session) -> list[User]:
    users = [
        User(id=1, username="admin",        full_name="Администратор",      role=UserTypeEnum.admin),
        User(id=2, username="teacher_ivan", full_name="Иван Петров",        role=UserTypeEnum.teacher),
        User(id=3, username="student_anna", full_name="Анна Смирнова",      role=UserTypeEnum.student),
        User(id=4, username="student_oleg", full_name="Олег Васильев",      role=UserTypeEnum.student),
    ]
    db.add_all(users)
    db.flush()
    return users


def insert_modules(db: Session) -> list[Module]:
    modules = [
        Module(id=1, title="Введение в Python",     description="Базовые конструкции языка Python"),
        Module(id=2, title="Алгоритмы и структуры", description="Сортировки, деревья, графы"),
    ]
    db.add_all(modules)
    db.flush()
    return modules


def insert_tasks(db: Session) -> list[Task]:
    tasks = [
        Task(
            id=1,
            module_id=1,
            title="Hello World",
            description="Напишите программу, которая выводит 'Hello, World!'",
            timeout=5,
            tests_pipeline=[
                {"title": "Базовый тест", "input": {}, "output": {"stdout": "Hello, World!\n"}}
            ],
        ),
        Task(
            id=2,
            module_id=1,
            title="Сумма двух чисел",
            description="Дано два числа. Выведите их сумму.",
            timeout=5,
            tests_pipeline=[
                {"title": "Тест 1", "input": {"stdin": "2 3"}, "output": {"stdout": "5\n"}},
                {"title": "Тест 2", "input": {"stdin": "0 0"}, "output": {"stdout": "0\n"}},
            ],
        ),
        Task(
            id=3,
            module_id=2,
            title="Сортировка пузырьком",
            description="Реализуйте сортировку пузырьком.",
            timeout=10,
            tests_pipeline=[
                {"title": "Тест 1", "input": {"stdin": "5 3 1 4 2"}, "output": {"stdout": "1 2 3 4 5\n"}},
            ],
        ),
    ]
    db.add_all(tasks)
    db.flush()
    return tasks


def insert_module_task_orders(db: Session) -> None:
    orders = [
        ModuleTaskOrder(module_id=1, task_id=1, order=1),
        ModuleTaskOrder(module_id=1, task_id=2, order=2),
        ModuleTaskOrder(module_id=2, task_id=3, order=1),
    ]
    db.add_all(orders)
    db.flush()


def insert_task_languages(db: Session) -> None:
    links = [
        TaskLanguage(task_id=1, language_id=1),  # python
        TaskLanguage(task_id=1, language_id=2),  # javascript
        TaskLanguage(task_id=2, language_id=1),  # python
        TaskLanguage(task_id=3, language_id=1),  # python
        TaskLanguage(task_id=3, language_id=3),  # java
    ]
    db.add_all(links)
    db.flush()


def insert_solutions(db: Session) -> None:
    solutions = [
        Solution(user_id=3, task_id=1, language="python",     is_solved=True),
        Solution(user_id=3, task_id=2, language="python",     is_solved=False),
        Solution(user_id=4, task_id=1, language="javascript", is_solved=True),
    ]
    db.add_all(solutions)
    db.flush()


def insert_attempts(db: Session) -> None:
    attempts = [
        Attempt(
            solution_user_id=3, solution_task_id=1,
            language="python",
            current_code='print("Hello, World!")',
            message="Все тесты пройдены",
        ),
        Attempt(
            solution_user_id=3, solution_task_id=2,
            language="python",
            current_code="a, b = map(int, input().split())\nprint(a - b)",
            message="Тест 1 не пройден: ожидалось 5, получено -1",
        ),
        Attempt(
            solution_user_id=4, solution_task_id=1,
            language="javascript",
            current_code='console.log("Hello, World!")',
            message="Все тесты пройдены",
        ),
    ]
    db.add_all(attempts)
    db.flush()


def run_seed(db: Session) -> None:
    """
    Заполняет базу данных тестовыми данными.

    Seed запускается один раз при старте приложения.
    Если данные уже есть — вставка не происходит (см. seed_database в database.py).

    Порядок вставки важен: сначала независимые таблицы (языки, пользователи),
    потом те, которые ссылаются на них через foreign key (задачи, решения и т.д.)
    """

    # Языки программирования — независимая таблица, вставляем первой
    insert_languages(db)

    # Пользователи — тоже независимы от других таблиц
    insert_users(db)

    # Модули — контейнеры для задач, нужны раньше самих задач
    insert_modules(db)

    # Задачи — ссылаются на модули (module_id), поэтому после них
    insert_tasks(db)

    # Порядок задач внутри модулей — ссылается и на модули, и на задачи
    insert_module_task_orders(db)

    # Связь задач с языками — ссылается на tasks и languages
    insert_task_languages(db)

    # Решения студентов — ссылаются на пользователей и задачи
    insert_solutions(db)

    # Попытки — ссылаются на решения, поэтому самые последние
    insert_attempts(db)

    # Фиксируем все изменения в базе одной транзакцией.
    # Если что-то выше упало — db.rollback() в seed_database откатит всё целиком
    db.commit()
    print("OK: Seed data inserted")