from typing import Annotated
import loguru
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy import URL, String, text
from config import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL_acyncpg
)
loguru.logger.debug(f"Connecting to database: {settings.DATABASE_URL_acyncpg}")

async_session_maker = async_sessionmaker(async_engine)

str_256 = Annotated[str, 256]

class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256)
    }

    repr_cols_num = 3 # первые 3 колонки
    repr_cols = tuple()

    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"

if __name__ == '__main__':

    async def get_any():
        async with async_engine.connect() as conn:
            res = await conn.execute(text("SELECT version()"))
            print(f'{res.all()=}')

    asyncio.run(get_any())


'''
Сессия нужна для транзанций, по сути когда мы входим в сессию мы открываем транзакцию
-> делаем какие-то запросы -> commit/rollback таким образом завершая транзакцию (данные соответственно либо попадают илбо нет)
'''
