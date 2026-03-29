"""
SQLite Database Optimization Module
Оптимизация SQLite: индексы, WAL mode, connection pooling
"""

import sqlite3
import threading
import time
from contextlib import contextmanager
from queue import Queue, Empty
from typing import Optional, Generator, Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class SQLiteConnectionPool:
    """Connection pool для SQLite с оптимизациями"""
    
    def __init__(self, database_path: str, max_connections: int = 10, 
                 timeout: float = 30.0, enable_wal: bool = True):
        self.database_path = database_path
        self.max_connections = max_connections
        self.timeout = timeout
        self.enable_wal = enable_wal
        self._pool = Queue(maxsize=max_connections)
        self._all_connections = set()
        self._lock = threading.RLock()
        
        # Инициализация пула
        self._initialize_pool()
    
    def _create_connection(self) -> sqlite3.Connection:
        """Создание оптимизированного соединения"""
        conn = sqlite3.connect(
            self.database_path,
            timeout=self.timeout,
            check_same_thread=False,
            isolation_level=None  # Autocommit mode
        )
        
        # Применяем оптимизации
        self._apply_optimizations(conn)
        return conn
    
    def _apply_optimizations(self, conn: sqlite3.Connection):
        """Применение оптимизаций к соединению"""
        cursor = conn.cursor()
        
        try:
            # Включаем WAL mode для лучшей производительности
            if self.enable_wal:
                cursor.execute("PRAGMA journal_mode=WAL")
                logger.info("WAL mode enabled")
            
            # Оптимизации производительности
            optimizations = [
                "PRAGMA synchronous=NORMAL",  # Быстрее чем FULL, безопаснее чем OFF
                "PRAGMA cache_size=10000",    # Увеличиваем кеш
                "PRAGMA temp_store=MEMORY",   # Временные данные в памяти
                "PRAGMA mmap_size=268435456", # 256MB memory mapping
                "PRAGMA page_size=4096",      # Оптимальный размер страницы
                "PRAGMA foreign_keys=ON",     # Включаем внешние ключи
                "PRAGMA busy_timeout=30000"   # Таймаут для блокировок
            ]
            
            for pragma in optimizations:
                cursor.execute(pragma)
                logger.debug(f"Applied: {pragma}")
                
        except sqlite3.Error as e:
            logger.error(f"Error applying optimizations: {e}")
        finally:
            cursor.close()
    
    def _initialize_pool(self):
        """Инициализация пула соединений"""
        with self._lock:
            for _ in range(self.max_connections):
                try:
                    conn = self._create_connection()
                    self._all_connections.add(conn)
                    self._pool.put(conn, block=False)
                except Exception as e:
                    logger.error(f"Failed to create connection: {e}")
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager для получения соединения из пула"""
        conn = None
        try:
            # Получаем соединение из пула
            try:
                conn = self._pool.get(timeout=self.timeout)
            except Empty:
                raise RuntimeError(f"No available connections within {self.timeout}s")
            
            # Проверяем соединение
            if not self._is_connection_valid(conn):
                conn = self._create_connection()
            
            yield conn
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            # Пересоздаем соединение при ошибке
            if conn:
                try:
                    conn.close()
                except:
                    pass
                conn = self._create_connection()
            raise
        finally:
            # Возвращаем соединение в пул
            if conn:
                try:
                    self._pool.put(conn, block=False)
                except:
                    # Пул полон, закрываем соединение
                    conn.close()
    
    def _is_connection_valid(self, conn: sqlite3.Connection) -> bool:
        """Проверка валидности соединения"""
        try:
            conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False
    
    def close_all(self):
        """Закрытие всех соединений"""
        with self._lock:
            # Закрываем соединения в пуле
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                except Empty:
                    break
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            
            # Закрываем все остальные соединения
            for conn in self._all_connections:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            
            self._all_connections.clear()

class SQLiteOptimizer:
    """Класс для оптимизации SQLite базы данных"""
    
    def __init__(self, connection_pool: SQLiteConnectionPool):
        self.pool = connection_pool
    
    def analyze_table_performance(self, table_name: str) -> Dict[str, Any]:
        """Анализ производительности таблицы"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем статистику таблицы
            stats = {}
            
            # Количество записей
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            stats['row_count'] = cursor.fetchone()[0]
            
            # Размер таблицы
            cursor.execute("""
                SELECT page_count * page_size as size 
                FROM pragma_page_count(), pragma_page_size()
            """)
            stats['db_size'] = cursor.fetchone()[0]
            
            # Информация об индексах
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            stats['indexes'] = []
            
            for index in indexes:
                index_name = index[1]
                cursor.execute(f"PRAGMA index_info({index_name})")
                index_info = cursor.fetchall()
                stats['indexes'].append({
                    'name': index_name,
                    'unique': bool(index[2]),
                    'columns': [col[2] for col in index_info]
                })
            
            return stats
    
    def suggest_indexes(self, table_name: str, query_patterns: List[str]) -> List[str]:
        """Предложения по созданию индексов на основе паттернов запросов"""
        suggestions = []
        
        for pattern in query_patterns:
            # Простой анализ WHERE условий
            if "WHERE" in pattern.upper():
                # Извлекаем колонки из WHERE условий
                where_part = pattern.upper().split("WHERE")[1]
                # Упрощенное извлечение колонок (в реальности нужен парсер SQL)
                for word in where_part.split():
                    if word.isalpha() and word not in ['AND', 'OR', 'NOT', 'IN', 'LIKE']:
                        suggestions.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{word.lower()} ON {table_name}({word.lower()})")
        
        return list(set(suggestions))  # Убираем дубликаты
    
    def create_recommended_indexes(self, table_name: str, columns: List[str]):
        """Создание рекомендованных индексов"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            for column in columns:
                index_name = f"idx_{table_name}_{column}"
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column})")
                    logger.info(f"Created index: {index_name}")
                except sqlite3.Error as e:
                    logger.error(f"Failed to create index {index_name}: {e}")
    
    def vacuum_analyze(self):
        """Выполнение VACUUM и ANALYZE для оптимизации"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # ANALYZE обновляет статистику для оптимизатора запросов
                cursor.execute("ANALYZE")
                logger.info("ANALYZE completed")
                
                # VACUUM дефрагментирует базу данных
                cursor.execute("VACUUM")
                logger.info("VACUUM completed")
                
            except sqlite3.Error as e:
                logger.error(f"Error during VACUUM/ANALYZE: {e}")
    
    def explain_query(self, query: str) -> List[tuple]:
        """Анализ плана выполнения запроса"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute(f"EXPLAIN QUERY PLAN {query}")
                return cursor.fetchall()
            except sqlite3.Error as e:
                logger.error(f"Error explaining query: {e}")
                return []

# Пример использования
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Создание пула соединений
    pool = SQLiteConnectionPool("example.db", max_connections=5, enable_wal=True)
    
    # Создание оптимизатора
    optimizer = SQLiteOptimizer(pool)
    
    try:
        # Пример создания таблицы
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    email TEXT NOT NULL,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Анализ производительности
        stats = optimizer.analyze_table_performance("users")
        print(f"Table stats: {stats}")
        
        # Создание индексов
        optimizer.create_recommended_indexes("users", ["email", "created_at"])
        
        # Анализ запроса
        plan = optimizer.explain_query("SELECT * FROM users WHERE email = 'test@example.com'")
        print(f"Query plan: {plan}")
        
        # Оптимизация базы
        optimizer.vacuum_analyze()
        
    finally:
        pool.close_all()