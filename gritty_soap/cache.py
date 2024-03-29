import base64
import datetime
import errno
import logging
import os
import sqlite3
import threading
from contextlib import contextmanager

import appdirs
import pytz
import six

logger = logging.getLogger(__name__)


class Base(object):

    def add(self, url, content):
        raise NotImplemented()

    def get(self, url):
        raise NotImplemented()


class InMemoryCache(Base):
    """Simple in-memory caching using dict lookup with support for timeouts"""
    _cache = {}  # global cache, thread-safe by default

    def __init__(self, timeout=3600):
        self._timeout = timeout

    def add(self, url, content):
        logger.debug("Caching contents of %s", url)
        self._cache[url] = (datetime.datetime.utcnow(), content)

    def get(self, url):
        try:
            created, content = self._cache[url]
        except KeyError:
            pass
        else:
            if not _is_expired(created, self._timeout):
                logger.debug("Cache HIT for %s", url)
                return content
        logger.debug("Cache MISS for %s", url)
        return None


class SqliteCache(Base):
    """Cache contents via an sqlite database on the filesystem"""
    _version = '1'

    def __init__(self, path=None, timeout=3600):

        # No way we can support this when we want to achieve thread safety
        if path == ':memory:':
            raise ValueError(
                "The SqliteCache doesn't support :memory: since it is not " +
                "thread-safe. Please use gritty_soap.cache.InMemoryCache()")

        self._lock = threading.RLock()
        self._timeout = timeout
        self._db_path = path if path else _get_default_cache_path()

        # Initialize db
        with self.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS request
                    (created timestamp, url text, content text)
                """)
            conn.commit()

    @contextmanager
    def db_connection(self):
        with self._lock:
            connection = sqlite3.connect(
                self._db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            yield connection
            connection.close()

    def add(self, url, content):
        logger.debug("Caching contents of %s", url)
        data = self._encode_data(content)

        with self.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM request WHERE url = ?", (url,))
            cursor.execute(
                "INSERT INTO request (created, url, content) VALUES (?, ?, ?)",
                (datetime.datetime.utcnow(), url, data))
            conn.commit()

    def get(self, url):
        with self.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT created, content FROM request WHERE url=?", (url, ))
            rows = cursor.fetchall()

        if rows:
            created, data = rows[0]
            if not _is_expired(created, self._timeout):
                logger.debug("Cache HIT for %s", url)
                return self._decode_data(data)
        logger.debug("Cache MISS for %s", url)

    def _encode_data(self, data):
        data = base64.b64encode(data)
        if six.PY2:
            return buffer(self._version_string + data)
        return self._version_string + data

    def _decode_data(self, data):
        if six.PY2:
            data = str(data)
        if data.startswith(self._version_string):
            return base64.b64decode(data[len(self._version_string):])

    @property
    def _version_string(self):
        prefix = u'$ZEEP:%s$' % self._version
        return bytes(prefix.encode('ascii'))


def _is_expired(value, timeout):
    """Return boolean if the value is expired"""
    if timeout is None:
        return False

    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    max_age = value.replace(tzinfo=pytz.utc)
    max_age += datetime.timedelta(seconds=timeout)
    return now > max_age


def _get_default_cache_path():
    path = appdirs.user_cache_dir('gritty_soap', False)
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    return os.path.join(path, 'cache.db')
