"""
Database Resilience Module for SRS Vocabulary App
Implements complete database connection resilience with:
- Configurable timeouts via environment variables
- Circuit breaker pattern to prevent hammering failed connections
- Signal alarm backup for hard timeouts
- Multi-level fallback: PostgreSQL -> SQLite -> Mock data
- Detailed timing logs for every connection attempt
"""

import os
import logging
import time
import signal
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Circuit breaker pattern to prevent hammering failed connections"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # 'closed', 'open', 'half-open'

    def can_attempt(self) -> bool:
        """Check if we can attempt a connection"""
        if self.state == 'closed':
            return True
        elif self.state == 'open':
            if self.last_failure_time and (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout:
                self.state = 'half-open'
                logger.info("🔄 Circuit breaker entering half-open state")
                return True
            return False
        elif self.state == 'half-open':
            return True
        return False

    def record_success(self):
        """Record successful connection"""
        self.failure_count = 0
        self.state = 'closed'
        logger.info("✅ Circuit breaker closed - connection successful")

    def record_failure(self):
        """Record failed connection"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
            logger.warning(f"🔴 Circuit breaker opened after {self.failure_count} failures")

    def get_status(self) -> str:
        """Get current circuit breaker status"""
        return self.state

class DatabaseResilience:
    """Main database resilience manager"""

    def __init__(self):
        # Configurable timeouts from environment
        self.connect_timeout = int(os.environ.get('DB_CONNECT_TIMEOUT', '10'))
        self.query_timeout = int(os.environ.get('DB_QUERY_TIMEOUT', '30'))
        self.retry_attempts = int(os.environ.get('DB_RETRY_ATTEMPTS', '3'))
        self.retry_delay = int(os.environ.get('DB_RETRY_DELAY', '2'))

        # Circuit breaker settings
        self.circuit_breaker_failures = int(os.environ.get('DB_CIRCUIT_BREAKER_FAILURES', '5'))
        self.circuit_breaker_recovery = int(os.environ.get('DB_CIRCUIT_BREAKER_RECOVERY', '60'))

        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.circuit_breaker_failures,
            recovery_timeout=self.circuit_breaker_recovery
        )

        # Connection state
        self.current_db_type = 'unknown'
        self.last_connection_time = None
        self.connection_attempts = 0
        self.connection_failures = 0

        logger.info("🛡️ Database Resilience initialized with timeouts:")
        logger.info(f"   - Connect timeout: {self.connect_timeout}s")
        logger.info(f"   - Query timeout: {self.query_timeout}s")
        logger.info(f"   - Retry attempts: {self.retry_attempts}")
        logger.info(f"   - Circuit breaker: {self.circuit_breaker_failures} failures, {self.circuit_breaker_recovery}s recovery")

    @contextmanager
    def timeout_context(self, seconds: int, description: str):
        """Context manager for timeout (signal-based on Unix, no-op on Windows)"""
        # Check if SIGALRM is available (Unix systems)
        if hasattr(signal, 'SIGALRM'):
            def timeout_handler(signum, frame):
                raise TimeoutError(f"⏰ {description} timed out after {seconds} seconds")

            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)

            try:
                yield
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # On Windows, just yield without timeout
            logger.debug(f"⏰ Timeout not supported on this platform, proceeding without timeout for {description}")
            yield

    def log_connection_attempt(self, db_type: str, attempt: int, start_time: float):
        """Log connection attempt with timing"""
        elapsed = time.time() - start_time
        self.connection_attempts += 1
        logger.info(f"🔌 [{datetime.now().isoformat()}] Connection attempt {attempt} to {db_type} - {elapsed:.2f}s elapsed")

    def get_connection_status(self) -> Dict[str, Any]:
        """Get comprehensive connection status"""
        return {
            'db_type': self.current_db_type,
            'circuit_breaker_state': self.circuit_breaker.get_status(),
            'last_connection_time': self.last_connection_time.isoformat() if self.last_connection_time else None,
            'connection_attempts': self.connection_attempts,
            'connection_failures': self.connection_failures,
            'connect_timeout': self.connect_timeout,
            'query_timeout': self.query_timeout,
            'retry_attempts': self.retry_attempts,
            'timestamp': datetime.now().isoformat()
        }

    def connect_postgresql(self) -> Optional[Any]:
        """Connect to PostgreSQL with full resilience"""
        if not self.circuit_breaker.can_attempt():
            logger.warning("🚫 PostgreSQL connection blocked by circuit breaker")
            return None

        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            logger.info("ℹ️ No DATABASE_URL found, skipping PostgreSQL")
            return None

        # Convert postgres:// to postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)

        for attempt in range(self.retry_attempts):
            start_time = time.time()

            try:
                logger.info(f"🔄 Attempting PostgreSQL connection (attempt {attempt + 1}/{self.retry_attempts})")

                with self.timeout_context(self.connect_timeout, "PostgreSQL connection"):
                    import psycopg2
                    from psycopg2.extras import RealDictCursor

                    conn = psycopg2.connect(
                        db_url,
                        sslmode='require',
                        connect_timeout=self.connect_timeout,
                        options=f'-c statement_timeout={self.query_timeout * 1000}'
                    )

                    # Test connection
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute('SELECT 1')
                    cursor.fetchone()
                    cursor.close()

                elapsed = time.time() - start_time
                logger.info(f"✅ PostgreSQL connected successfully in {elapsed:.2f}s")
                self.current_db_type = 'postgresql'
                self.last_connection_time = datetime.now()
                self.circuit_breaker.record_success()
                return conn

            except ImportError:
                logger.warning("⚠️ psycopg2 not available, skipping PostgreSQL")
                break
            except TimeoutError as e:
                elapsed = time.time() - start_time
                logger.warning(f"⏰ PostgreSQL connection timeout after {elapsed:.2f}s: {e}")
                self.circuit_breaker.record_failure()
            except Exception as e:
                elapsed = time.time() - start_time
                logger.warning(f"❌ PostgreSQL connection failed after {elapsed:.2f}s: {e}")
                self.circuit_breaker.record_failure()
                self.connection_failures += 1

                if attempt < self.retry_attempts - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"⏳ Retrying PostgreSQL in {delay}s...")
                    time.sleep(delay)

        return None

    def connect_sqlite(self) -> Optional[Any]:
        """Connect to SQLite as fallback"""
        start_time = time.time()

        try:
            logger.info("🔄 Attempting SQLite connection")

            with self.timeout_context(self.connect_timeout, "SQLite connection"):
                import sqlite3

                # Use in-memory SQLite if Railway environment (no persistent storage)
                is_railway = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY')
                db_path = ':memory:' if is_railway else 'srs_vocab.db'

                conn = sqlite3.connect(db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row

                # Test connection
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                cursor.fetchone()
                cursor.close()

            elapsed = time.time() - start_time
            logger.info(f"✅ SQLite connected successfully in {elapsed:.2f}s")
            self.current_db_type = 'sqlite'
            self.last_connection_time = datetime.now()
            return conn

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ SQLite connection failed after {elapsed:.2f}s: {e}")
            self.connection_failures += 1
            return None

    def create_mock_connection(self) -> Any:
        """Create mock connection for last resort"""
        logger.warning("🛑 Creating mock database connection - app will run in degraded mode")

        class MockConnection:
            def __init__(self):
                self.db_type = 'mock'
                self.is_mock = True

            def cursor(self):
                return MockCursor()

            def close(self):
                pass

            def commit(self):
                pass

            def rollback(self):
                pass

        class MockCursor:
            def execute(self, sql, params=None):
                logger.debug(f"🛑 Mock execute: {sql}")
                return self

            def fetchall(self):
                return []

            def fetchone(self):
                return None

            def close(self):
                pass

        self.current_db_type = 'mock'
        self.last_connection_time = datetime.now()
        return MockConnection()

    def get_connection(self) -> Any:
        """Get database connection with full fallback chain"""
        logger.info("🔌 Attempting database connection with resilience...")

        # Try PostgreSQL first
        conn = self.connect_postgresql()
        if conn:
            return conn

        # Fallback to SQLite
        conn = self.connect_sqlite()
        if conn:
            return conn

        # Last resort: Mock connection
        logger.critical("🚨 All database connections failed, using mock connection")
        return self.create_mock_connection()

# Global instance
db_resilience = DatabaseResilience()

def get_resilient_connection():
    """Get database connection with full resilience"""
    return db_resilience.get_connection()

def get_connection_status():
    """Get current connection status"""
    return db_resilience.get_connection_status()
