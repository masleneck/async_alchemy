import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from queries.orm import AsyncORM
from queries.core import AsyncCore

async def core_main():
    await AsyncCore.create_tables()
    await AsyncCore.insert_workers()
    await AsyncCore.select_workers()
    await AsyncCore.update_worker()

async def orm_main():
    await AsyncORM.create_tables()
    await AsyncORM.insert_workers()
    # await AsyncORM.select_workers()
    # await AsyncORM.update_worker()
    await AsyncORM.insert_resumes()
    # await AsyncORM.select_resumes_avg_compensation()
    # await AsyncORM.select_workers_with_joined_relationship() # ленивая подгрузка не работает в асинхронной алхимии!
    # await AsyncORM.select_workers_with_selectin_relationship()
    # await AsyncORM.select_workers_with_condition_relationship()
    await AsyncORM.convert_workers_to_dto()
    await AsyncORM.add_vacancies_and_replies()
    await AsyncORM.select_resumes_with_all_relationships()


def create_fastapi_app():
    app = FastAPI(title="FastAPI")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
    )
        
    @app.get("/workers", tags=["Кандидат"])
    async def get_workers():
        workers = await AsyncORM.convert_workers_to_dto()
        return workers
    
    @app.get("/resumes", tags=["Резюме"])
    async def get_resumes():
        resumes = await AsyncORM.select_resumes_with_all_relationships()
        return resumes

    return app

app = create_fastapi_app()

if __name__ == '__main__':
    # asyncio.run(core_main())
    # asyncio.run(orm_main())
    ...