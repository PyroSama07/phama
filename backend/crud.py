from sqlalchemy.orm import Session
import models, schemas

def get_user_by_email(db:Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db:Session, user:schemas.UserCreate):
    db_user = models.User(name=user.name, username=user.username, hashed_password=user.hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def save_message(db:Session, msg: str, sender:bool, user_id:int):
    m = models.Message(msg=msg, sender=sender, user_id=user_id)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def get_all_messages_of_user(db: Session, user_id: int):
    return db.query(models.Message).filter(models.Message.user_id == user_id).order_by(models.Message.time_stamp)

def delete_all_messages_of_user(db: Session, user_id: int):
    db.query(models.Message).filter(models.Message.user_id == user_id).delete()
    db.commit()