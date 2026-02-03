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
        """Get database connection with appropriate cursor (lazy with retry/fallback)"""
        if self._connection is not None:
            return self._connection

        # Determine database type from environment
        self.is_postgresql = bool(os.environ.get('DATABASE_URL'))

        if self.is_postgresql:
            self._connection = self._connect_with_retry_and_fallback()
        else:
            self._connection = self._get_sqlite_connection()

        return self._connection

    def _connect_with_retry_and_fallback(self):
        """Connect to database with retry logic and fallback to SQLite"""
        import time

        # Try PostgreSQL first (Railway) with retry
        db_url = os.environ.get('DATABASE_URL')

        if db_url and db_url.startswith('postgres'):
            # Convert postgres:// to postgresql://
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)

            # Retry with exponential backoff (max 3 attempts, total ~7 seconds)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"🔄 Attempting PostgreSQL connection (attempt {attempt + 1}/{max_retries})...")
                    import psycopg2
                    from psycopg2.extras import RealDictCursor

                    # Add connection timeout
                    conn = psycopg2.connect(
                        db_url,
                        sslmode='require',
                        connect_timeout=5,  # 5 second timeout
                        options='-c statement_timeout=5000'  # 5 second query timeout
                    )
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    logger.info("✅ Connected to PostgreSQL database")
                    return cursor

                except ImportError:
                    logger.warning("⚠️  PostgreSQL driver not available, falling back to SQLite")
                    break
                except Exception as e:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"⚠️  PostgreSQL connection failed (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        logger.info(f"⏳ Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger.error("❌ PostgreSQL connection failed after all retries, falling back to SQLite")

        # Fallback to SQLite (built-in, always works)
        try:
            return self._get_sqlite_connection()
        except Exception as e:
            logger.critical(f"❌ CRITICAL: Even SQLite connection failed: {e}")
            raise

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
            # Handle datetime functions
            sql = sql.replace("datetime('now')", 'NOW()')
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

    def insert_or_ignore(self, table: str, data: dict, conflict_column: str = 'id'):
        """
        Insert data, ignoring if conflict occurs on specified column.
        Compatible with both SQLite and PostgreSQL.
        """
        if not data:
            return

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s' if self.is_postgresql else '?' for _ in data])

        if self.is_postgresql:
            # PostgreSQL: ON CONFLICT DO NOTHING
            sql = f"""
                INSERT INTO {table} ({columns})
                VALUES ({placeholders})
                ON CONFLICT ({conflict_column}) DO NOTHING
            """
        else:
            # SQLite: INSERT OR IGNORE
            sql = f"""
                INSERT OR IGNORE INTO {table} ({columns})
                VALUES ({placeholders})
            """

        params = tuple(data.values())
        cursor = self.execute(sql, params)
        return cursor

    def insert_or_replace(self, table: str, data: dict, conflict_columns: List[str]):
        """
        Insert data, replacing if conflict occurs on specified columns.
        Compatible with both SQLite and PostgreSQL.
        """
        if not data:
            return

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s' if self.is_postgresql else '?' for _ in data])

        if self.is_postgresql:
            # PostgreSQL: ON CONFLICT DO UPDATE
            update_columns = ', '.join([f"{col} = EXCLUDED.{col}" for col in data.keys()])
            conflict_cols = ', '.join(conflict_columns)
            sql = f"""
                INSERT INTO {table} ({columns})
                VALUES ({placeholders})
                ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_columns}
            """
        else:
            # SQLite: INSERT OR REPLACE
            sql = f"""
                INSERT OR REPLACE INTO {table} ({columns})
                VALUES ({placeholders})
            """

        params = tuple(data.values())
        cursor = self.execute(sql, params)
        return cursor

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
