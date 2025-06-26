from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..db.database import get_db
from ..models.user import User
from ..models.session import Session as UserSession, SESSION_TEMPLATES
from ..schemas.user import UserCreate, User as UserSchema, Token, TokenData
from ..config import settings

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    except Exception as e:
        print(f"JWT encoding error: {e}")
        raise HTTPException(status_code=500, detail="Token creation failed")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserSchema)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 사용자명 중복 확인
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # 사용자 생성
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        birth_year=user_data.birth_year
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 12개 세션 자동 생성
    for template in SESSION_TEMPLATES:
        session = UserSession(
            user_id=db_user.id,
            session_number=template["session_number"],
            title=template["title"],
            description=template["description"],
            is_completed=False
        )
        db.add(session)
    db.commit()
    
    return db_user

@router.post("/token", response_model=Token)
async def login_oauth(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 웹앱용 로그인 엔드포인트 (form data 형식)
@router.post("/login", response_model=Token)
async def login_web(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"Login attempt for username: {form_data.username}")
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        print(f"Authentication failed for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"User authenticated successfully: {user.username}")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    print(f"Token created successfully for user: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

# 테스트용 사용자 생성 엔드포인트
@router.post("/create-test-user")
async def create_test_user(db: Session = Depends(get_db)):
    # 테스트 사용자가 이미 있는지 확인
    test_user = db.query(User).filter(User.username == "testuser").first()
    if test_user:
        return {"message": "Test user already exists", "username": "testuser"}
    
    # 테스트 사용자 생성
    hashed_password = get_password_hash("test123")
    db_user = User(
        email="test@example.com",
        username="testuser",
        full_name="테스트 사용자",
        birth_year=1960,
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 12개 세션 자동 생성
    for template in SESSION_TEMPLATES:
        session = UserSession(
            user_id=db_user.id,
            session_number=template["session_number"],
            title=template["title"],
            description=template["description"],
            is_completed=False
        )
        db.add(session)
    db.commit()
    
    return {
        "message": "Test user created successfully",
        "username": "testuser", 
        "password": "test123",
        "email": "test@example.com",
        "debug_info": {
            "google_api_key_set": bool(settings.google_api_key and not settings.google_api_key.startswith("AIzaSyDummy")),
            "api_key_prefix": settings.google_api_key[:10] if settings.google_api_key else None
        }
    }

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user