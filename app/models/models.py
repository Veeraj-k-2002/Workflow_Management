import uuid
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.schemas.task_schema import TaskPriority, TaskStatus

Base = declarative_base()


class UserRole(str, PyEnum):
    ADMIN = "admin"
    SUPERUSER = "superuser"
    NORMAL = "normal"


class Company(Base):
    """Represents a company/organization."""

    __tablename__ = "companies"
    __table_args__ = {"schema": "task"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    r_users = relationship("User", back_populates="r_company")


class User(Base):
    """Represents a user in the system."""

    __tablename__ = "users"
    __table_args__ = {"schema": "task"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    country_code = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    year_of_birth = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)

    role = Column(
        Enum(UserRole, values_callable=lambda obj: [e.value for e in obj], native_enum=False),
        default=UserRole.NORMAL,
        nullable=False,
    )
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("task.companies.id", ondelete="CASCADE"),
        nullable=True,
    )

    r_credentials = relationship(
        "UserCredentials",
        back_populates="r_cred_user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    r_tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
    r_company = relationship("Company", back_populates="r_users")


class UserCredentials(Base):
    """Stores authentication details for a user."""

    __tablename__ = "user_credentials"
    __table_args__ = {"schema": "task"}

    user_id = Column(UUID(as_uuid=True), ForeignKey("task.users.id", ondelete="CASCADE"), primary_key=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    refresh_token = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    refresh_token_expiry = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    r_cred_user = relationship("User", back_populates="r_credentials")


class Task(Base):
    """Represents a task assigned to a user."""

    __tablename__ = "tasks"
    __table_args__ = {"schema": "task"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.backlog)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium)
    due_date = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("task.users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    started_at = Column(DateTime(timezone=True), nullable=True)
    review_due_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    done_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="r_tasks")
