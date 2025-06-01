from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    executions = relationship("Execution", back_populates="project", cascade="all, delete-orphan")

class Execution(Base):
    __tablename__ = "executions"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    executed_at = Column(DateTime)
    triggered_by = Column(String)

    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)

    project = relationship("Project", back_populates="executions")
    test_cases = relationship("TestCase", back_populates="execution", cascade="all, delete-orphan")


class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey("executions.id"))
    name = Column(String)
    status = Column(String)
    duration_seconds = Column(Float)
    error_message = Column(Text)

    execution = relationship("Execution", back_populates="test_cases")
