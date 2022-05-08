"""Initialize the database."""

import abc
import typing as t
from contextlib import asynccontextmanager

if t.TYPE_CHECKING:
    import psycopg_pool
    import psycopg
    import aiosqlite
else:
    psycopg_pool = psycopg = aiosqlite = t.Any


Row = t.Mapping[str, t.Any]


class Database(abc.ABC):
    """Database abstract class."""

    @abc.abstractmethod
    @classmethod
    async def setup(cls, config: t.Mapping[str, t.Any]) -> "Database":
        """Initialize the database."""

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the database."""

    @abc.abstractmethod
    @asynccontextmanager
    async def connection(self) -> t.AsyncIterator["Connection"]:
        """Get a connection."""
        yield Connection()  # type: ignore # pylint: disable=abstract-class-instantiated


class SQLite(Database):
    """Sqlite database."""

    def __init__(self, connection: aiosqlite.Connection) -> None:
        """Initialize the database."""
        self.conn = connection

    # pylint: disable=import-outside-toplevel
    @classmethod
    async def setup(cls, config: t.Mapping[str, t.Any]) -> "SQLite":
        """Initialize the database."""
        try:
            import aiosqlite as aio

            database = await aio.connect(config["database"])
            database.row_factory = aiosqlite.Row
            return cls(database)
        except ImportError:
            raise ValueError(
                "aiosqlite isn't installed ! Please install it with "
                "python -m pip install aiosqlite"
            ) from None

    async def close(self) -> None:
        """Close the database."""
        await self.conn.close()

    @asynccontextmanager
    async def connection(self) -> t.AsyncIterator["SQLiteConnection"]:
        """Get a connection."""
        yield SQLiteConnection(self.conn)


class PostgreSQL(Database):
    """PostgreSQL database."""

    def __init__(
        self,
        pool: psycopg_pool.AsyncConnectionPool,
    ) -> None:
        """Initialize the database."""
        self.pool = pool

    # pylint: disable=import-outside-toplevel
    @classmethod
    async def setup(cls, config: t.Mapping[str, t.Any]) -> "PostgreSQL":
        """Initialize the database."""
        try:
            import psycopg_pool as pooler
            from psycopg.rows import dict_row

            pool = pooler.AsyncConnectionPool(
                **config,
                row_factory=dict_row,
            )
            await pool.open()
            return cls(pool)
        except ImportError:
            raise ValueError(
                "psycopg isn't installed ! Please install it with "
                "python -m pip install psycopg[pool]"
            ) from None

    async def close(self) -> None:
        """Close the database."""
        await self.pool.close()

    @asynccontextmanager
    async def connection(self) -> t.AsyncIterator["PostgreSQLConnection"]:
        """Create a connection to the database."""
        async with self.pool.connection() as connection:
            yield PostgreSQLConnection(connection.cursor())
            await connection.commit()


class Connection(abc.ABC):
    """Connection abstract class."""

    @abc.abstractmethod
    async def execute(
        self, query: str, params: t.Optional[t.Sequence[t.Any]] = None
    ) -> None:
        """Execute a query."""

    @abc.abstractmethod
    async def executemany(
        self, query: str, params_seq: t.Sequence[t.Sequence[t.Any]]
    ) -> None:
        """Execute a query with multiple parameters."""

    @abc.abstractmethod
    async def fetchone(self) -> t.Optional[Row]:
        """Fetch one row."""

    @abc.abstractmethod
    async def fetchall(self) -> t.List[Row]:
        """Fetch all rows."""

    @abc.abstractmethod
    async def fetchmany(self, size: int = 1) -> t.List[Row]:
        """Fetch some rows."""


class SQLiteConnection(Connection):
    """SQLite connection."""

    def __init__(self, conn: aiosqlite.Connection) -> None:
        """Initialize the connection."""
        self._conn = conn
        self._cursor: t.Optional[aiosqlite.Cursor] = None

    async def execute(
        self, query: str, params: t.Optional[t.Iterable[t.Any]] = None
    ) -> None:
        """Execute an SQL statement."""
        if self._cursor is None:
            self._cursor = await self._conn.execute(
                query,
                params,
            )
        else:
            if params is None:
                await self._cursor.execute(query)
            else:
                await self._cursor.execute(
                    query,
                    params,
                )

    async def executemany(
        self,
        query: str,
        params_seq: t.Sequence[t.Sequence[t.Any]],
    ) -> None:
        """Execute an SQL statement with various parameters."""
        if self._cursor is None:
            self._cursor = await self._conn.executemany(
                query,
                params_seq,
            )
        else:
            await self._cursor.executemany(
                query,
                params_seq,
            )

    async def fetchone(self) -> t.Optional[Row]:
        """Fetch one row."""
        if self._cursor is None:
            return None
        return await self._cursor.fetchone()  # type: ignore

    async def fetchall(self) -> t.List[Row]:
        """Fetch all rows."""
        if self._cursor is None:
            return []
        return await self._cursor.fetchall()  # type: ignore

    async def fetchmany(self, size: int = 1) -> t.List[Row]:
        """Fetch some rows."""
        if self._cursor is None:
            return []
        return await self._cursor.fetchmany(size)  # type: ignore


class PostgreSQLConnection(Connection):
    """PostgreSQL connection."""

    def __init__(self, cursor: psycopg.AsyncCursor[t.Any]) -> None:
        """Initialize the connection."""
        self.cursor = cursor

    async def execute(
        self, query: str, params: t.Optional[t.Sequence[t.Any]] = None
    ) -> None:
        """Execute an SQL statement."""
        await self.cursor.execute(
            query.replace("?", "%s"),  # psycopg parameterized queries
            params,
        )

    async def executemany(
        self,
        query: str,
        params_seq: t.Sequence[t.Sequence[t.Any]],
    ) -> None:
        """Execute an SQL statement with various parameters."""
        await self.cursor.executemany(
            query.replace("?", "%s"),  # psycopg parameterized queries
            params_seq,
        )

    async def fetchone(self) -> t.Optional[Row]:
        """Fetch one row."""
        return await self.cursor.fetchone()

    async def fetchall(self) -> t.List[Row]:
        """Fetch all rows."""
        return await self.cursor.fetchall()

    async def fetchmany(self, size: int = 1) -> t.List[Row]:
        """Fetch multiple rows."""
        return await self.cursor.fetchmany(size)


async def load(config: t.Mapping[str, t.Any]) -> Database:
    """Load the database."""
    if config["database"]["type"] == "postgresql":
        return await PostgreSQL.setup(config["database"]["postgresql"])
    if config["database"]["type"] == "sqlite":
        return await SQLite.setup(config["database"]["sqlite"])

    raise ValueError(f"Unsupported database type: {config['database']['type']}")
