from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum as sql_enum
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP, VARCHAR
from sqlalchemy.dialects.postgresql import UUID as pg_uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schema.tasks import Priority, Status
from utils.db.general import MixInNameTable

from .base import Base


class Tasks(Base, MixInNameTable):
	id: Mapped[UUID] = mapped_column(
		pg_uuid(as_uuid=True), primary_key=True, nullable=False, default=uuid4
	)
	status: Mapped[str] = mapped_column(
		sql_enum(Status), index=True, nullable=False, unique=False
	)
	priority: Mapped[int] = mapped_column(
		sql_enum(Priority), nullable=False, unique=False
	)
	user: Mapped[UUID] = mapped_column(
		pg_uuid(as_uuid=True), nullable=True, unique=False
	)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False, default=datetime.now(UTC), index=True
	)
	updated_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True, default=None
	)
	task_list_id: Mapped[UUID] = mapped_column(
		ForeignKey("task_list.id"), nullable=True
	)
	task_list: Mapped["TaskList"] = relationship(back_populates="tasks")
	title: Mapped[str] = mapped_column(VARCHAR(25), nullable=False)
	description: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)


class TaskList(Base, MixInNameTable):
	id: Mapped[UUID] = mapped_column(
		pg_uuid(as_uuid=True), primary_key=True, nullable=False, default=uuid4
	)
	name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, unique=True)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False, default=datetime.now(UTC), index=True
	)
	updated_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True, default=None
	)
	tasks: Mapped[list["Tasks"]] = relationship(
		back_populates="task_list", cascade="all, delete-orphan"
	)


class Users(Base, MixInNameTable):
	id: Mapped[UUID] = mapped_column(
		pg_uuid(as_uuid=True), primary_key=True, nullable=False, default=uuid4
	)
	full_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, unique=False)
	email: Mapped[str] = mapped_column(
		VARCHAR(255), nullable=False, unique=True, index=True
	)
	password_hash: Mapped[str] = mapped_column(VARCHAR(255), unique=False)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False, default=datetime.now(UTC), index=True
	)
	updated_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True, default=None
	)
