from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import cloudinary

cloudinary.config(
    cloud_name = settings.cloud_name,
    api_key = settings.cloudinary_api_key,
    api_secret = settings.cloudinary_api_secret
)

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'


# Prog-BIO

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=10, max_overflow=20) 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()


 
# while True:

#     try:
#         conn = psycopg2.connect(host= 'localhost', database= 'fastapi', user= 'postgres',
#                                 password= 'Ifeanyi058', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connection was successfull") 
#         break

#     except Exception as error:
#         print("connecting to database failed")
#         print("Error: ", error)
#         time.sleep(2)
