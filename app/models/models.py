import uuid
from sqlalchemy import Column, String, Text, DateTime, Date, ForeignKey, func, Integer, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from app.schemas.task_schema import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy import UniqueConstraint
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import expression
from sqlalchemy import Enum
 
Base = declarative_base()


class User(Base):
    """
    Represents a user in the system.
    """
    __tablename__ = "users"
    __table_args__ = {"schema": "task"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    country_code = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    year_of_birth = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)

    # Relationships
    r_credentials = relationship("UserCredentials", back_populates="r_cred_user", uselist=False, cascade="all, delete-orphan")
    r_tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")



class UserCredentials(Base):
    """
    Stores authentication details for a user.
    """
    __tablename__ = "user_credentials"
    __table_args__ = {"schema": "task"}

    user_id = Column(UUID(as_uuid=True), ForeignKey("task.users.id", ondelete="CASCADE"), primary_key=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    refresh_token = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    refresh_token_expiry = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    r_cred_user = relationship("User", back_populates="r_credentials")




class Task(Base):
    """
    Represents a task assigned to a user.
    """
    __tablename__ = "tasks"
    __table_args__ = {"schema": "task"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium)
    due_date = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("task.users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="r_tasks")

