from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker

Base = declarative_base()

dsn = "sqlite://db.sqlite"

engine = create_engine(dsn, echo=True)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    nickname = Column(String, nullable=False)
    profile_image = Column(String, nullable=False)
    email = Column(String, nullable=False)
    inactivate = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)


def create_user(db: Session, user: User):
    user = User(
        id=user.id,
        nickname=user.nickname,
        profile_image=user.profile_image,
        email=user.email,
        created_at=user.created_at,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
