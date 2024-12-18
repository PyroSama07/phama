from datetime import datetime, timedelta, timezone
from typing import Annotated
import os
from dotenv import load_dotenv
load_dotenv()

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext # JWT
from pydantic import BaseModel

import crud, models, schemas
from schemas import User
from schemas import UserInDB

from database import SessionLocal, engine
from sqlalchemy.orm import Session

# CROS
from fastapi.middleware.cors import CORSMiddleware
origins = ["*"]

#JWT
# to create secret key run= openssl rand -hex 32
SECRET_KEY = os.getenv("JWT_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine) # create all db tables
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CROS origin add
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)
def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# add to list when hit logout, and using login check list
blacklist = set() # we can use redis store for this
def add_token_to_blacklist(token: str):
    blacklist.add(token)
def is_token_blacklisted(token: str) -> bool:
    return token in blacklist

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Check if token is blacklisted then user is logout
        if is_token_blacklisted(token):
            raise credentials_exception
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/")
async def healthCheck():
    return "healthCheck"

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session=Depends(get_db)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

# My functions
@app.post("/create_user/", response_model = schemas.User)
def create_user(user: schemas.UserCreate, db: Session=Depends(get_db)):
    db_user = crud.get_user_by_email(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail = "Email already registered")
    user.hashed_password = get_password_hash(user.hashed_password)
    return crud.create_user(db=db, user=user)

@app.post("/send_message", response_model = schemas.Message)
def add_message(message:schemas.MessageBase, current_user: Annotated[User, Depends(get_current_active_user)], db: Session=Depends(get_db)):
    # save user's message
    crud.save_message(db, msg = message.msg, sender=False, user_id=current_user.id)
    # get responce form model
    responce_message =  get_responce_RAG(message.msg)
    # save model's message
    m = crud.save_message(db, msg=responce_message, sender=True, user_id=current_user.id)
    return m

@app.get("/get_all_message", response_model = list[schemas.Message])
def get_all_messages(current_user: Annotated[User, Depends(get_current_active_user)], db: Session=Depends(get_db)):
    return crud.get_all_messages_of_user(db, user_id=current_user.id)

def get_responce_RAG(message=str):
    if message=="ਮਿਰਚ ਦੇ ਫ਼ਲ ਦੇ ਗੜੂੰਆਂ ਨੂੰ ਰੋਕਣ ਲਈ ਕਿਹੜੀ ਦਵਾਈ ਵਰਤੀ ਜਾ ਸਕਦੀ ਹੈ?":
        return "ਮਿਰਚ ਦੇ ਫ਼ਲ ਦੇ ਗੜੂੰਆਂ ਦੀ ਰੋਕਥਾਮ ਲਈ 50 ਮਿਲੀਲਿਟਰ ਕੋਰਾਜਨ 18.5 ਐਸ ਸੀ (ਕਲੋਰਐਂਟਰਾਨੀਲੀਪਰੋਲ) ਜਾਂ 50 ਮਿਲੀਲਿਟਰ ਟਰੇਸਰ 45 ਐਸ ਸੀ (ਸਪਾਈਨੋਸੈਡ) ਨੂੰ 100 ਲਿਟਰ ਪਾਣੀ ਵਿੱਚ ਮਿਲਾ ਕੇ ਏਕੜ ਵਿੱਚ ਛਿੜਕਾਅ ਕਰਨਾ ਚਾਹੀਦਾ ਹੈ।"
    if message=="ਖਰਬੂਜ਼ੇ ਦੀ ਫ਼ਸਲ ਲਈ ਕਿਹੜਾ ਤਾਪਮਾਨ ਢੁੱਕਵਾਂ ਹੈ?":
        return "ਖਰਬੂਜ਼ੇ ਦੀ ਫ਼ਸਲ ਲਈ 27 ਤੋਂ 30 ਡਿਗਰੀ ਸੈਂਟੀਗ੍ਰੇਡ ਤਾਪਮਾਨ ਢੁੱਕਵਾਂ ਹੁੰਦਾ ਹੈ।"
    return "This is the responce message form RAG model"

@app.post("/logout")
async def logout(token: Annotated[str, Depends(oauth2_scheme)]):
    add_token_to_blacklist(token)
    return {"msg": "Successfully logged out"}

@app.delete("/delete_all_messages", status_code=204)
def delete_all_messages(current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    return crud.delete_all_messages_of_user(db, user_id=current_user.id)

@app.post("/upload_image", response_model=schemas.Message)
def upload_image(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are supported.")
    
    image_data = getImageOCR()
    
    crud.save_message(db, msg=image_data, sender=False, user_id=current_user.id)
    
    response_message = get_responce_RAG(image_data)

    message = crud.save_message(db, msg=response_message, sender=True, user_id=current_user.id)

    return {
        "id": message.id,
        "msg": message.msg,
        "user_id": message.user_id,
        "time_stamp": message.time_stamp
    }

def getImageOCR():
    return "sending image data"