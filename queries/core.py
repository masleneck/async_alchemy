from loguru import logger
from sqlalchemy import Integer, and_, func, insert, select, text, update
from sqlalchemy.orm import aliased
from database import async_engine
from coremodels import metadata_obj, workers_table, resumes_table

class AsyncCore:
    
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(metadata_obj.drop_all)
            await conn.run_sync(metadata_obj.create_all)


    @staticmethod
    async def insert_workers():
        async with async_engine.connect() as conn:
            # stmt = """INSERT INTO workers (username) VALUES 
            #     ('Jack'),
            #     ('Michael');"""
            stmt = insert(workers_table).values(
                [
                    {"username": "Jack"},
                    {"username": "Michael"},
                ]
            )
            await conn.execute(stmt)
            await conn.commit()


    @staticmethod
    async def select_workers():
        async with async_engine.connect() as conn:
            query= select(workers_table) # SELECT * FROM workers
            result = await conn.execute(query)
            workers = result.all()
            print(f"{workers=}")


    @staticmethod
    async def update_worker(worker_id: int = 2, new_username: str = "DROP TABLE CASCADE workers"):
        async with async_engine.connect() as conn:
            # stmt = text("UPDATE workers SET username=:username WHERE id=:id")
            # stmt = stmt.bindparams(username=new_username, id=worker_id) # bindparams- защита от sql инъекций
            stmt=(
                update(workers_table)
                .values(username=new_username)
                # .where(workers_table.c.id==id) # название таблицы - колонка - id
                .filter_by(id=worker_id)
            )
            await conn.execute(stmt)
            await conn.commit()
             







'''
connect():
Этот метод создаёт подключение к базе данных.
Подключение можно использовать для выполнения запросов, но оно не управляет транзакциями автоматически.
Если ты выполняешь запросы, которые изменяют данные (например, INSERT, UPDATE, DELETE), 
тебе нужно вручную управлять транзакциями (например, вызывать commit() или rollback()).

begin():
Этот метод также создаёт подключение к базе данных, но автоматически начинает транзакцию.
Когда блок async with завершается, транзакция автоматически фиксируется (commit), если не произошло ошибок.
Если возникает ошибка, транзакция автоматически откатывается (rollback).
Это удобно для операций, которые изменяют данные, так как не нужно вручную управлять транзакциями.

Используй begin():
Для операций, которые изменяют данные (INSERT, UPDATE, DELETE).
Когда нужно автоматическое управление транзакциями.

Используй connect():
Для операций, которые только читают данные (SELECT).
Когда нужно вручную управлять транзакциями 
(например, если ты выполняешь несколько запросов в одной транзакции и хочешь сам решать, когда фиксировать изменения).
'''