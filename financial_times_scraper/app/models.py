from sqlalchemy import Column, String, DateTime, Integer, Text, ARRAY
from sqlalchemy.sql import func
from .database import Base

class Article(Base):
    __tablename__ = "articles"

    url = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=False)
    scraped_at = Column(DateTime, server_default=func.now(), nullable=False)

    subtitle = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    image_url = Column(String, nullable=True)
    word_count = Column(Integer, nullable=True)
    reading_time = Column(String, nullable=True)
    related_articles = Column(ARRAY(String), nullable=True)
