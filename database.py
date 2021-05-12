from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


engine = create_engine("sqlite:///messenger.db")
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)


class Message(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    sender = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    receiver = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    message = Column(Text, nullable=False)
    subject = Column(String)
    create_date = Column(DateTime, default=datetime.now, nullable=False)
    read = Column(Boolean, default=0)


if __name__ == "__main__":
    Base.metadata.create_all(engine)