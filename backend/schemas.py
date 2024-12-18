from pydantic import BaseModel
from datetime import datetime

# Message
class MessageBase(BaseModel):
    msg: str
    sender: bool = False

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    user_id: int
    time_stamp: datetime

    class Config:
        from_attributes = True


# User
class UserBase(BaseModel):
    name: str 
    username: str # emial

class UserCreate(UserBase):
    hashed_password: str

class User(UserBase):
    id: int
    is_active: bool | None = None # is active

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str
