# @formatter:off

import enum
from sqlalchemy import *
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSON, BIGINT, TIMESTAMP, ENUM

Base = declarative_base()


class UserTypeEnum(enum.Enum):
    admin   = "admin"
    student = "student"
    teacher = "teacher"

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id              = Column(BIGINT, primary_key=True, index=True)
    user_id         = Column(BIGINT, ForeignKey("users.id"), nullable=False, index=True)
    token_hash      = Column(String(512), nullable=False, unique=True)
    expires_at      = Column(TIMESTAMP(timezone=True), nullable=False)
    revoked         = Column(Boolean, nullable=False, default=False, index=True)
    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True),server_default=func.now(), onupdate=func.now())
    user            = relationship("User", back_populates="refresh_tokens")


class User(Base):
    __tablename__   = "users"

    id              = Column(BIGINT, primary_key=True, index=True)
    username        = Column(String(64), unique=True, nullable=False, index=True)
    full_name       = Column(String(128), nullable=False, index=True)
    role            = Column(ENUM(UserTypeEnum), nullable=False, index=True)
    password_hash   = Column(String(255), nullable=True)

    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True),server_default=func.now(), onupdate=func.now())

    solutions       = relationship("Solution", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens  = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    deleted_at      = Column(TIMESTAMP(timezone=True), nullable=True)


class Module(Base):
    __tablename__   = "modules"

    id              = Column(BIGINT, primary_key=True, index=True)
    title           = Column(String(128), index=True)
    description     = Column(Text, nullable=False)

    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True),server_default=func.now(), onupdate=func.now())

    task_links      = relationship("ModuleTaskOrder", back_populates="module",order_by="ModuleTaskOrder.order", cascade="all, delete-orphan")


class Task(Base):
    __tablename__   = "tasks"

    id              = Column(BIGINT, primary_key=True, index=True)
    title           = Column(String(128), index=True)
    description     = Column(Text, nullable=False)
    timeout         = Column(Integer, nullable=False, index=True)   # секунды
    tests           = relationship("TaskTest", back_populates="task", cascade="all, delete-orphan")

    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True),server_default=func.now(), onupdate=func.now())

    languages       = relationship("Language", secondary="tasks_languages", back_populates="tasks")
    solutions       = relationship("Solution", back_populates="task", cascade="all, delete-orphan")
    module_links    = relationship("ModuleTaskOrder", back_populates="task", cascade="all, delete-orphan")


class TaskTest(Base):
    __tablename__ = "task_tests"
    id              = Column(BIGINT, primary_key=True, index=True)
    task_id         = Column(BIGINT, ForeignKey("tasks.id"), nullable=False, index=True)
    title           = Column(String(128), nullable=False)
    stdin           = Column(Text, nullable=False, default="")
    stdout          = Column(Text, nullable=False)
    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True),server_default=func.now(), onupdate=func.now())
    task            = relationship("Task", back_populates="tests")

class ModuleTaskOrder(Base):
    __tablename__   = "module_tasks_order"
    __table_args__ = (
        UniqueConstraint(
            "module_id",
            "order",
            name="unique_module_order",
            deferrable=True,
            initially="DEFERRED",
        ),
    )

    module_id       = Column(BIGINT, ForeignKey("modules.id"), primary_key=True)
    task_id         = Column(BIGINT, ForeignKey("tasks.id"), primary_key=True)
    order           = Column(Integer, nullable=False, index=True)

    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True),server_default=func.now(), onupdate=func.now())

    module = relationship("Module", back_populates="task_links")
    task = relationship("Task", back_populates="module_links")


class Language(Base):
    __tablename__   = "languages"

    id              = Column(BIGINT, primary_key=True, index=True)
    language        = Column(String(64), nullable=False, index=True)

    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())

    tasks           = relationship("Task", secondary="tasks_languages", back_populates="languages")


class TaskLanguage(Base):
    __tablename__   = "tasks_languages"
    __table_args__  = (PrimaryKeyConstraint("task_id", "language_id", name="task_language_pk"),)

    task_id         = Column(BIGINT, ForeignKey("tasks.id"), nullable=False, index=True)
    language_id     = Column(BIGINT, ForeignKey("languages.id"), nullable=False, index=True)


class Solution(Base):
    __tablename__   = "solutions"
    __table_args__  = (PrimaryKeyConstraint("user_id", "task_id", name="solution_pk"),)

    user_id         = Column(BIGINT, ForeignKey("users.id"), nullable=False, index=True)
    task_id         = Column(BIGINT, ForeignKey("tasks.id"), nullable=False, index=True)

    # language        = Column(String(64), nullable=False, index=True)
    current_code	= Column(Text, nullable=False)
    is_solved       = Column(Boolean, nullable=False, default=False, index=True)

    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True),server_default=func.now(), onupdate=func.now())

    user            = relationship("User", back_populates="solutions")
    task            = relationship("Task", back_populates="solutions")
    attempts        = relationship("Attempt", back_populates="solution", cascade="all, delete-orphan")


class Attempt(Base):
    __tablename__ = "attempts"
    __table_args__ = (
        ForeignKeyConstraint(
                ["solution_user_id", "solution_task_id"],
                ["solutions.user_id", "solutions.task_id"],
                name="attempt_solution_fk"
            ),
        )

    id                  = Column(BIGINT, primary_key=True, index=True)
    solution_user_id    = Column(BIGINT, nullable=False)
    solution_task_id    = Column(BIGINT, nullable=False)
    message			    = Column(String(128), nullable=False)
    language            = Column(String(64), nullable=True)
    memory_mb           = Column(Integer, nullable=True)
    time_ms             = Column(Integer, nullable=True)
    is_solved           = Column(Boolean, nullable=False, default=False)

    created_at          = Column(TIMESTAMP(timezone=True), server_default=func.now())

    solution            = relationship("Solution", back_populates="attempts")

# @formatter:on
