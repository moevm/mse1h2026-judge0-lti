from app.database.models import User, Module, Task, ModuleTaskOrder, Language, TaskLanguage, Solution, Attempt, UserTypeEnum
from sqlalchemy.orm import Session


def insert_languages(db: Session) -> list[Language]:
    languages = [
        Language(id=43, language="Plain Text"),
        Language(id=44, language="Executable"),
        Language(id=45, language="Assembly (NASM 2.14.02)"),
        Language(id=46, language="Bash (5.0.0)"),
        Language(id=47, language="Basic (FBC 1.07.1)"),
        Language(id=48, language="C (GCC 7.4.0)"),
        Language(id=49, language="C (GCC 8.3.0)"),
        Language(id=50, language="C (GCC 9.2.0)"),
        Language(id=51, language="C# (Mono 6.6.0.161)"),
        Language(id=52, language="C++ (GCC 7.4.0)"),
        Language(id=53, language="C++ (GCC 8.3.0)"),
        Language(id=54, language="C++ (GCC 9.2.0)"),
        Language(id=55, language="Common Lisp (SBCL 2.0.0)"),
        Language(id=56, language="D (DMD 2.089.1)"),
        Language(id=57, language="Elixir (1.9.4)"),
        Language(id=58, language="Erlang (OTP 22.2)"),
        Language(id=59, language="Fortran (GFortran 9.2.0)"),
        Language(id=60, language="Go (1.13.5)"),
        Language(id=61, language="Haskell (GHC 8.8.1)"),
        Language(id=62, language="Java (OpenJDK 13.0.1)"),
        Language(id=63, language="JavaScript (Node.js 12.14.0)"),
        Language(id=64, language="Lua (5.3.5)"),
        Language(id=65, language="OCaml (4.09.0)"),
        Language(id=66, language="Octave (5.1.0)"),
        Language(id=67, language="Pascal (FPC 3.0.4)"),
        Language(id=68, language="PHP (7.4.1)"),
        Language(id=69, language="Prolog (GNU Prolog 1.4.5)"),
        Language(id=70, language="Python (2.7.17)"),
        Language(id=71, language="Python (3.8.1)"),
        Language(id=72, language="Ruby (2.7.0)"),
        Language(id=73, language="Rust (1.40.0)"),
        Language(id=74, language="TypeScript (3.7.4)"),
        Language(id=75, language="C (Clang 7.0.1)"),
        Language(id=76, language="C++ (Clang 7.0.1)"),
        Language(id=77, language="COBOL (GnuCOBOL 2.2)"),
        Language(id=78, language="Kotlin (1.3.70)"),
        Language(id=79, language="Objective-C (Clang 7.0.1)"),
        Language(id=80, language="R (4.0.0)"),
        Language(id=81, language="Scala (2.13.2)"),
        Language(id=82, language="SQL (SQLite 3.27.2)"),
        Language(id=83, language="Swift (5.2.3)"),
        Language(id=84, language="Visual Basic.Net (vbnc 0.0.0.5943)"),
        Language(id=85, language="Perl (5.28.1)"),
        Language(id=86, language="Clojure (1.10.1)"),
        Language(id=87, language="F# (.NET Core SDK 3.1.202)"),
        Language(id=88, language="Groovy (3.0.3)"),
        Language(id=89, language="Multi-file program"),
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
            title="Hello World",
            description="Напишите программу, которая выводит 'Hello, World!'",
            timeout=5,
            tests_pipeline=[
                {"title": "Базовый тест", "input": {}, "output": {"stdout": "Hello, World!\n"}}
            ],
        ),
        Task(
            id=2,
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
        TaskLanguage(task_id=1, language_id=71),  # python
        TaskLanguage(task_id=1, language_id=63),  # javascript
        TaskLanguage(task_id=2, language_id=71),  # python
        TaskLanguage(task_id=3, language_id=71),  # python
        TaskLanguage(task_id=3, language_id=62),  # java
    ]
    db.add_all(links)
    db.flush()


def insert_solutions(db: Session) -> None:
    solutions = [
        Solution(
            user_id=3,
            task_id=1,
            language="Python (3.8.1)",
            current_code='print("Hello, World!")',
            is_solved=True
        ),
        Solution(
            user_id=3,
            task_id=2,
            language="Python (3.8.1)",
            current_code='a, b = map(int, input().split())\nprint(a + b)',
            is_solved=False
        ),
        Solution(
            user_id=4,
            task_id=1,
            language="JavaScript (Node.js 12.14.0)",
            current_code='console.log("Hello, World!");',
            is_solved=True
        ),
    ]
    db.add_all(solutions)
    db.flush()


def insert_attempts(db: Session) -> None:
    attempts = [
        Attempt(
            solution_user_id=3,
            solution_task_id=1,
            message="Все тесты пройдены",
        ),
        Attempt(
            solution_user_id=3,
            solution_task_id=2,
            message="Тест 1 не пройден: ожидалось 5, получено -1",
        ),
        Attempt(
            solution_user_id=4,
            solution_task_id=1,
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