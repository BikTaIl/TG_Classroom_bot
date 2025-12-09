from typing import Optional

from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, Numeric, Text, TIMESTAMP, text,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True)
    active_github_username = Column(String)
    full_name = Column(String)
    banned = Column(Boolean)
    notifications_enabled = Column(Boolean)
    created_at = Column(
        TIMESTAMP,
        server_default=text("NOW()")
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=text("NOW()"),
        onupdate=text("NOW()")
    )

    github_accounts = relationship("GithubAccount", back_populates="user")
    courses_as_teacher = relationship("Course", back_populates="teacher")
    assistants = relationship("Assistant", back_populates="user")
    submissions = relationship("Submission", back_populates="student")
    notifications = relationship("Notification", back_populates="user")
    permissions = relationship("Permission", back_populates="user")
    oauth_states = relationship("OAuthState", back_populates="user")  # <- добавлено


class GithubAccount(Base):
    __tablename__ = "github_accounts"

    github_username = Column(String, primary_key=True)
    user_telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"))
    created_at = Column(
        TIMESTAMP,
        server_default=text("NOW()")
    )

    user = relationship("User", back_populates="github_accounts")


class Course(Base):
    __tablename__ = "courses"

    classroom_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    teacher_telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"))
    created_at = Column(
        TIMESTAMP,
        server_default=text("NOW()")
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=text("NOW()"),
        server_onupdate=text("NOW()")
    )

    teacher = relationship("User", back_populates="courses_as_teacher")
    assistants = relationship("Assistant", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")


class Assistant(Base):
    __tablename__ = "assistants"

    telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"), primary_key=True)
    course_id = Column(BigInteger, ForeignKey("courses.classroom_id"))

    user = relationship("User", back_populates="assistants")
    course = relationship("Course", back_populates="assistants")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(BigInteger, primary_key=True)
    classroom_id = Column(BigInteger, ForeignKey("courses.classroom_id"))
    title = Column(String)
    github_assignment_id = Column(String)
    max_score = Column(Numeric)
    deadline_full = Column(TIMESTAMP)
    created_at = Column(
        TIMESTAMP,
        server_default=text("NOW()")
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=text("NOW()"),
        server_onupdate=text("NOW()")
    )
    grading_mode = Column(String)

    course = relationship("Course", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(BigInteger, primary_key=True)
    assignment_id = Column(BigInteger, ForeignKey("assignments.id"))
    student_github_username = Column(String)
    student_telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"))
    repo_url = Column(String)
    is_submitted = Column(Boolean)
    submitted_at = Column(TIMESTAMP)
    score = Column(Numeric)
    created_at = Column(
        TIMESTAMP,
        server_default=text("NOW()")
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=text("NOW()"),
        server_onupdate=text("NOW()")
    )

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions")


class Notification(Base):
    __tablename__ = "notifications"

    telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"), primary_key=True)
    notification_time = Column(Integer, primary_key=True)

    user = relationship("User", back_populates="notifications")


class Permission(Base):
    __tablename__ = "permissions"

    telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"), primary_key=True)
    permitted_role = Column(String, primary_key=True)

    user = relationship("User", back_populates="permissions")


class OAuthState(Base):
    __tablename__ = "oauth_states"

    state = Column(String, primary_key=True)
    telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))

    user = relationship("User", back_populates="oauth_states")


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True)
    created_at = Column(
        TIMESTAMP,
        server_default=text("NOW()")
    )
    message = Column(Text)


class AccessDenied(Exception):
    def __init__(self, message: str, user_id: Optional[int] = None):
        self.message = message
        self.user_id = user_id
        super().__init__(message)
