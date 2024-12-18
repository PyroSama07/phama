# POJO
# SQLAlchemy Models (Python classes that map to database tables)
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    name = Column(String(100))
    # email = Column(String(100), unique = True, index = True)
    username = Column(String(100), unique = True, index = True)
    is_active = Column(Boolean, default = False)
    hashed_password = Column(Text)

    # messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key = True)
    msg = Column(Text)
    sender = Column(Boolean, default = False)
    user_id = Column(Integer, ForeignKey("users.id"))
    time_stamp = Column(DateTime, default=datetime.now) 

    # user = relationship("User", back_populates="messages")
