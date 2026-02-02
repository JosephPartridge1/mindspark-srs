"""
Database Abstraction Layer for SRS Vocabulary App
Supports both SQLite (local development) and PostgreSQL (Railway production)
"""

import os
import logging
from typing import Any, List, Tuple, Optional

logger = logging.getLogger(__name__)

class DatabaseAdapter:
    """
    Database abstraction layer that handles differences between SQLite and PostgreSQL
    """

    def __init__(self):
        self.is_postgresql = bool(os.environ.get('DATABASE_URL'))
        self._connection = None
        logger.info(f"🗄️ DatabaseAdapter initialized for {'PostgreSQL' if self.is_postgresql else 'SQLite'}")

    def get_connection(self):
        """Get database connection with appropriate cursor"""
        if self._connection is not None:
            return self._connection

        if self.is_postgresql:
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor

                # Convert postgres:// to postgresql:// if needed
                db_url = os.environ['DATABASE_URL']
                if db_url.startswith('postgres://'):
                    db_url = db_url.replace('postgres://', 'postgresql://', 1)

                conn = psycopg2.connect(db_url, sslmode='require')
                self._connection = conn.cursor(cursor_factory=RealDictCursor)
                logger.info("✅ Connected to PostgreSQL database")
            except ImportError:
                logger.warning("⚠️ PostgreSQL driver not available, falling back to SQLite")
                self.is_postgresql = False
                return self._get_sqlite_connection()
        else:
            return self._get_sqlite_connection()

        return self._connection

    def _get_sqlite_connection(self):
        """Get SQLite connection"""
        import sqlite3
        conn = sqlite3.connect('srs_vocab.db', check_same_thread=False)
        conn.row_factory = sqlite3.Row
        self._connection = conn.cursor()
        logger.info("✅ Connected to SQLite database")
        return self._connection

    def adapt_sql(self, sql: str) -> str:
        """
        Adapt SQL syntax for the current database type
        """
        if self.is_postgresql:
            # Convert SQLite syntax to PostgreSQL
            sql = sql.replace('AUTOINCREMENT', 'SERIAL')
            sql = sql.replace('CURRENT_TIMESTAMP', 'NOW()')
            sql = sql.replace('?', '%s')
            # Handle boolean conversions in INSERT/UPDATE
            sql = sql.replace('TRUE', 'true')
            sql = sql.replace('FALSE', 'false')
        return sql

    def adapt_params(self, params: Tuple) -> Tuple:
        """
        Adapt parameters for the current database type
        """
        if not params:
            return params

        adapted = []
        for param in params:
            if isinstance(param, bool):
                if self.is_postgresql:
                    adapted.append(param)  # PostgreSQL handles bools natively
                else:
                    adapted.append(1 if param else 0)  # SQLite uses 0/1
            else:
                adapted.append(param)

        return tuple(adapted)

    def execute(self, sql: str, params: Tuple = None) -> Any:
        """
        Execute SQL query with proper adaptation
        """
        cursor = self.get_connection()
        adapted_sql = self.adapt_sql(sql)
        adapted_params = self.adapt_params(params) if params else None

        logger.debug(f"Executing SQL: {adapted_sql} with params: {adapted_params}")

        if adapted_params:
            cursor.execute(adapted_sql, adapted_params)
        else:
            cursor.execute(adapted_sql)

        return cursor

    def fetchall(self, cursor) -> List:
        """
        Fetch all results, handling different cursor types
        """
        results = cursor.fetchall()

        # Convert results to consistent format
        if self.is_postgresql:
            # psycopg2.extras.RealDictCursor returns dict-like objects
            return [dict(row) for row in results]
        else:
            # sqlite3.Row returns Row objects
            return [dict(row) for row in results]

    def fetchone(self, cursor) -> Optional[dict]:
        """
        Fetch one result, handling different cursor types
        """
        result = cursor.fetchone()

        if result is None:
            return None

        if self.is_postgresql:
            return dict(result)
        else:
            return dict(result)

    def commit(self):
        """Commit transaction"""
        if hasattr(self._connection, 'connection'):
            # PostgreSQL cursor has .connection attribute
            self._connection.connection.commit()
        else:
            # SQLite cursor is the connection
            self._connection.connection.commit()

    def close(self):
        """Close database connection"""
        if self._connection:
            if hasattr(self._connection, 'connection'):
                self._connection.connection.close()
            else:
                self._connection.connection.close()
            self._connection = None

    def get_db_type(self) -> str:
        """Get current database type"""
        return 'postgresql' if self.is_postgresql else 'sqlite'

# Global adapter instance
db_adapter = DatabaseAdapter()

def get_db_connection():
    """Legacy function for backward compatibility"""
    return db_adapter.get_connection()

def execute_query(sql: str, params: Tuple = None):
    """Execute query with database abstraction"""
    cursor = db_adapter.execute(sql, params)
    return cursor

def adapt_sql_query(sql: str) -> str:
    """Adapt SQL query syntax"""
    return db_adapter.adapt_sql(sql)
