from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .config import get_settings

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str]
    age: Mapped[int]
    weight: Mapped[float]
    goal: Mapped[str]
    intensity: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(index=True)
    original_plan: Mapped[str]
    updated_plan: Mapped[str | None] = mapped_column(default=None)
    nutrition_tip: Mapped[str]
    feedback: Mapped[str | None] = mapped_column(default=None)
    updated_at: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def save_user(data) -> User:
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.user_id == data.user_id))
        if existing:
            existing.username = data.username
            existing.age = data.age
            existing.weight = data.weight
            existing.goal = data.goal
            existing.intensity = data.intensity
            db.commit()
            db.refresh(existing)
            return existing

        user = User(
            user_id=data.user_id,
            username=data.username,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


def save_plan(user_id: str, original_plan: str, nutrition_tip: str) -> Plan:
    with SessionLocal() as db:
        existing = db.scalar(select(Plan).where(Plan.user_id == user_id))
        if existing:
            existing.original_plan = original_plan
            existing.updated_plan = None
            existing.nutrition_tip = nutrition_tip
            existing.feedback = None
            existing.updated_at = None
            db.commit()
            db.refresh(existing)
            return existing

        plan = Plan(
            user_id=user_id,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan


def get_user(user_id: str) -> User | None:
    with SessionLocal() as db:
        return db.scalar(select(User).where(User.user_id == user_id))


def get_plan(user_id: str) -> Plan | None:
    with SessionLocal() as db:
        return db.scalar(select(Plan).where(Plan.user_id == user_id))


def update_plan(user_id: str, updated_plan: str, feedback: str, nutrition_tip: str) -> Plan | None:
    with SessionLocal() as db:
        plan = db.scalar(select(Plan).where(Plan.user_id == user_id))
        if not plan:
            return None
        plan.updated_plan = updated_plan
        plan.feedback = feedback
        plan.nutrition_tip = nutrition_tip
        plan.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(plan)
        return plan


def get_all_users_with_plans():
    with SessionLocal() as db:
        users = list(db.scalars(select(User).order_by(User.created_at.desc())).all())
        result = []
        for user in users:
            plan = db.scalar(select(Plan).where(Plan.user_id == user.user_id))
            result.append((user, plan))
        return result


def delete_user(user_id: str) -> bool:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.user_id == user_id))
        if not user:
            return False
        plan = db.scalar(select(Plan).where(Plan.user_id == user_id))
        if plan:
            db.delete(plan)
        db.delete(user)
        db.commit()
        return True
