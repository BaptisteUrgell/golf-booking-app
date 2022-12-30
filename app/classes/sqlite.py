import aiosqlite
import sqlite3

from app.core.config import get_api_settings
settings = get_api_settings()
DATABASE = settings.database

class SQLite():
    def __init__(self, file=DATABASE):
        self.file=file
    async def __aenter__(self):
        self.conn = await aiosqlite.connect(self.file)
        self.cursor = await  self.conn.cursor()
        self.conn.row_factory = aiosqlite.Row
        return self.cursor
    async def __aexit__(self, type, value, traceback):
        await self.cursor.close()
        await self.conn.commit()
        await self.conn.close()

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        self.cursor =  self.conn.cursor()
        self.conn.row_factory = sqlite3.Row
        return self.cursor
    def __exit__(self, type, value, traceback):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()