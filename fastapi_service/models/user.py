from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)

    is_active = Column(Boolean)
    is_staff = Column(Boolean)
    is_superuser = Column(Boolean)