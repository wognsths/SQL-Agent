from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database management class"""

    def __init__(self, db_url=None):
        self.db_url = db_url or settings.DATABASE_URL
        self.engine = None
        self.SessionLocal = None
        self.init_db()

    def init_db(self):
        """Initalize database"""
        try:
            self.engine = create_engine(self.db_url)
            self.SessionLocal = sessionmaker(autocommit = False,
                                             autoflush  = False,
                                             bind       = self.engine)
            self.Base = declarative_base()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def get_session(self):
        """Return database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def execute_query(self, query, params = None):
        """
        Execute SQL query

        Args:
            query: SQL query string
            params: (Optional) Query parameter
        Returns:
            Query result (Dictionary list)
        """
        try:
            with self.engine.connect() as connection:
                if params:
                    result = connection.execute(text(query), params)
                else:
                    result = connection.execute(text(query))
            
                if result.returns_rows:
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in result.fetchall()]
                return []
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            if params:
                logger.error(f"Params: {params}")
            raise

db = Database()