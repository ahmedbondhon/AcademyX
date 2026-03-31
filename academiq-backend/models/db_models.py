from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from database.connection import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String, nullable=False)
    email           = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role            = Column(String, default="student")  # student | faculty | dean | admin
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)