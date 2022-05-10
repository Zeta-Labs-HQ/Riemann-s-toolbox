"""Initialize the database."""

import abc
import typing as t
from contextlib import asynccontextmanager

if t.TYPE_CHECKING:
    import aiosqlite
    import psycopg  # pylint: disable=unused-import
    import psycopg_pool  # pylint: disable=unused-import

    from .bot import Bot
else:
    psycopg_pool = psycopg = aiosqlite = t.Any
    Bot = t.Any


Row = t.Mapping[str, t.Any]


class Database(abc.ABC):
    """Database abstract class."""

    __slots__ = ()

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the database.

        It is not an error to close an alredy closed database.
        However, any operation on a closed database will raise an exception.
        """

    @abc.abstractmethod
    @asynccontextmanager
    async def connection(self) -> t.AsyncIterator["Connection"]:
        """Context manager to get a :class:`Connection` to the database."""
        yield Connection()  # type: ignore # pylint: disable=abstract-class-instantiated


class NoDatabase(Database):
    """There is no database."""

    __slots__ = ()

    async def close(self) -> None:
        """Close the database that doesn't exist.

        This function does nothing.
        """

    async def connection(self) -> t.NoReturn:  # type: ignore
        """Get no connection.

        This function never returns, but rather always errors

        :raise RuntimeError: This database doesn't exist
        """
        raise RuntimeError("The database is a lie")


class SQLite(Database):
    """SQLite database interface.

    Parameters
    ----------
    connection: :class:`aiosqlite.Connection`
        Raw connection to the database.

    Attributes
    ----------
    conn: :class:`aiosqlite.Connection`
        Raw connection to the database.
        This attribute is exposed in case the exposed API is insufficient.
    """

    __slots__ = ("conn", "_is_closed")

    def __init__(self, connection: "aiosqlite.Connection") -> None:
        """Initialize the database.

        :param connection: Connection to the database
        :type connection: :class:`aiosqlite.Connection`
        """
        self.conn = connection
        self._is_closed = False

    # pylint: disable=import-outside-toplevel
    @classmethod
    async def setup(cls, config: t.Mapping[str, t.Any]) -> "SQLite":
        """Initialize the database.

        :param config: Configuration of the database
        :type config: Mapping[:class:`str`, Any]
        :return: Instance of the database
        :rtype: :class:`SQLite`
        """
        try:
            import aiosqlite as aio

            database = await aio.connect(config["database"], isolation_level=None)
            database.row_factory = aiosqlite.Row
            return cls(database)
        except ImportError:
            raise ValueError(
                "aiosqlite isn't installed ! Please install it with "
                "python -m pip install aiosqlite"
            ) from None

    async def close(self) -> None:
        """Close the database.

        It is not an error to close an alredy closed database.
        However, any operation on a closed database will raise an exception.
        """
        self._is_closed = True
        await self.conn.close()

    @asynccontextmanager
    async def connection(self) -> t.AsyncIterator["SQLiteConnection"]:
        """Context manager to get a :class:`SQLiteConnection` to the database.

        :raise RuntimeError: The database is closed
        """
        if self._is_closed:
            raise RuntimeError("The database is closed")

        yield SQLiteConnection(self.conn)


class PostgreSQL(Database):
    """PostgreSQL database.

    Parameters
    ----------
    pool: :class:`psycopg_pool.AsyncConnectionPool`
        Raw pool of connections to the database.

    Attributes
    ----------
    pool: :class:`psycopg_pool.AsyncConnectionPool`
        Pool of connections to the database.
        This attribute is exposed in case the exposed API is insufficient.
    """

    __slots__ = ("pool", "_is_closed")

    def __init__(
        self,
        pool: "psycopg_pool.AsyncConnectionPool",
    ) -> None:
        """Initialize the database.

        :param pool: Pool of connections to the database
        :type pool: :class:`psycopg_pool.AsyncConnectionPool`
        """
        self.pool = pool
        self._is_closed = False

    # pylint: disable=import-outside-toplevel
    @classmethod
    async def setup(cls, config: t.Mapping[str, t.Any]) -> "PostgreSQL":
        """Initialize the database.

        :param config: Configuration of the database
        :type config: Mapping[:class:`str`, Any]
        :return: Instance of the database
        :rtype: :class:`PostgreSQL`
        """
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
            raise RuntimeError(
                "psycopg isn't installed ! Please install it with "
                "python -m pip install psycopg[pool]"
            ) from None

    async def close(self) -> None:
        """Close the database.

        It is not an error to close an alredy closed database.
        However, any operation on a closed database will raise an exception.
        """
        self._is_closed = True
        await self.pool.close()

    @asynccontextmanager
    async def connection(self) -> t.AsyncIterator["PostgreSQLConnection"]:
        """Context manager to get a :class:`PostgreSQLConnection` to the pool.

        :raise RuntimeError: The database is closed
        """
        if self._is_closed:
            raise RuntimeError("The database is closed")

        async with self.pool.connection() as connection:
            yield PostgreSQLConnection(connection.cursor())


class Connection(abc.ABC):
    """Connection abstract class."""

    __slots__ = ()

    @abc.abstractmethod
    async def execute(
        self, query: str, params: t.Optional[t.Sequence[t.Any]] = None
    ) -> None:
        """Execute a query.

        :param query: Query to execute
        :type query: :class:`str`
        :param params: Parameters of the query
        :type params: Optional[Sequence[Any]]
        """

    @abc.abstractmethod
    async def executemany(
        self, query: str, params_seq: t.Sequence[t.Sequence[t.Any]]
    ) -> None:
        """Execute a query with multiple parameters.

        :param query: Query to execute
        :type query: :class:`str`
        :param params_seq: Sequence of parameters of the query
        :type params_seq: Sequence[Sequence[Any]]
        """

    @abc.abstractmethod
    async def fetchone(self) -> t.Optional[Row]:
        """Fetch one row.

        :return: One row from the most recent query
        :rtype: Optional[Mapping[:class:`str`, Any]]
        """

    @abc.abstractmethod
    async def fetchall(self) -> t.List[Row]:
        """Fetch all rows.

        :return: All rows from the most recent query
        :rtype: List[Mapping[:class:`str`, Any]]
        """

    @abc.abstractmethod
    async def fetchmany(self, size: int = 1) -> t.List[Row]:
        """Fetch some rows.

        :param size: Number of rows to fetch
        :type size: int
        :return: size rows from the most recent query
        :rtype: List[Mapping[:class:`str`, Any]]
        """


class SQLiteConnection(Connection):
    """SQLite connection."""

    __slots__ = ("_conn", "_cursor")

    def __init__(self, conn: "aiosqlite.Connection") -> None:
        """Initialize the connection.

        :param conn: Connection to the database
        :type conn: :class:`aiosqlite.Connection`
        """
        self._conn = conn
        self._cursor: t.Optional[aiosqlite.Cursor] = None

    async def execute(
        self, query: str, params: t.Optional[t.Iterable[t.Any]] = None
    ) -> None:
        """Execute a query.

        :param query: Query to execute
        :type query: :class:`str`
        :param params: Parameters of the query
        :type params: Optional[Sequence[Any]]
        """
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
        """Execute a query with multiple parameters.

        :param query: Query to execute
        :type query: :class:`str`
        :param params_seq: Sequence of parameters of the query
        :type params_seq: Sequence[Sequence[Any]]
        """
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
        """Fetch one row.

        :return: One row from the most recent query
        :rtype: Optional[Mapping[:class:`str`, Any]]
        """
        if self._cursor is None:
            return None
        return await self._cursor.fetchone()  # type: ignore

    async def fetchall(self) -> t.List[Row]:
        """Fetch all rows.

        :return: All rows from the most recent query
        :rtype: List[Mapping[:class:`str`, Any]]
        """
        if self._cursor is None:
            return []
        return await self._cursor.fetchall()  # type: ignore

    async def fetchmany(self, size: int = 1) -> t.List[Row]:
        """Fetch some rows.

        :param size: Number of rows to fetch
        :type size: int
        :return: size rows from the most recent query
        :rtype: List[Mapping[:class:`str`, Any]]
        """
        if self._cursor is None:
            return []
        return await self._cursor.fetchmany(size)  # type: ignore


class PostgreSQLConnection(Connection):
    """PostgreSQL connection."""

    __slots__ = ("_cursor",)

    def __init__(self, cursor: "psycopg.AsyncCursor[t.Any]") -> None:
        """Initialize the connection.

        :param cursor: Cursor to the database
        :type cursor: :class:`psycopg.AsyncCursor`
        """
        self._cursor = cursor

    async def execute(
        self, query: str, params: t.Optional[t.Sequence[t.Any]] = None
    ) -> None:
        """Execute a query.

        :param query: Query to execute
        :type query: :class:`str`
        :param params: Parameters of the query
        :type params: Optional[Sequence[Any]]
        """
        await self._cursor.execute(
            query.replace("?", "%s"),  # psycopg parameterized queries
            params,
        )

    async def executemany(
        self,
        query: str,
        params_seq: t.Sequence[t.Sequence[t.Any]],
    ) -> None:
        """Execute a query with multiple parameters.

        :param query: Query to execute
        :type query: :class:`str`
        :param params_seq: Sequence of parameters of the query
        :type params_seq: Sequence[Sequence[Any]]
        """
        await self._cursor.executemany(
            query.replace("?", "%s"),  # psycopg parameterized queries
            params_seq,
        )

    async def fetchone(self) -> t.Optional[Row]:
        """Fetch one row.

        :return: One row from the most recent query
        :rtype: Optional[Mapping[:class:`str`, Any]]
        """
        return await self._cursor.fetchone()

    async def fetchall(self) -> t.List[Row]:
        """Fetch all rows.

        :return: All rows from the most recent query
        :rtype: List[Mapping[:class:`str`, Any]]
        """
        return await self._cursor.fetchall()

    async def fetchmany(self, size: int = 1) -> t.List[Row]:
        """Fetch some rows.

        :param size: Number of rows to fetch
        :type size: int
        :return: size rows from the most recent query
        :rtype: List[Mapping[:class:`str`, Any]]
        """
        return await self._cursor.fetchmany(size)


async def load(bot: Bot) -> Database:
    """Load the database.

    :param bot: Bot instance to load the database for
    :type bot: :class:`Bot`
    :return: Database instance
    :rtype: :class:`Database`
    """
    config = bot.config["database"]
    database_type = config["type"]

    if database_type == "none":
        return NoDatabase()

    if database_type == "postgresql":
        return await PostgreSQL.setup(config["postgresql"])

    if database_type == "sqlite":
        return await SQLite.setup(config["sqlite"])

    raise ValueError(f"Unsupported database type: {config['type']}")
