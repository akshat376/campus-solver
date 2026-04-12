from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "sqlite:///problems.db",
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Problem(Base):
    __tablename__ = "problems"

    id            = Column(String, primary_key=True)
    description   = Column(String)
    category      = Column(String)
    confidence    = Column(Float)
    department    = Column(String)
    status        = Column(String, default="Submitted")
    response      = Column(String, default="")
    created_at    = Column(String, default="")
    updated_at    = Column(String, default="")
    image_path    = Column(String, default="")
    student_name  = Column(String, default="")   # logged-in user's name
    student_email = Column(String, default="")   # logged-in user's email


Base.metadata.create_all(bind=engine)