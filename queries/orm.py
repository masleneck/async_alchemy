from loguru import logger
from sqlalchemy import Integer, and_, cast, func, select
from sqlalchemy.orm import joinedload, selectinload
from database import async_session_maker, async_engine, Base
from models import Workers, Resumes, Workload
from schemas import WorkersRelDTO

class AsyncORM:
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.success('Tables dropped successfully!')
            await conn.run_sync(Base.metadata.create_all)
            logger.success('Tables created successfully!')


    @staticmethod
    async def insert_workers():
        async with async_session_maker() as session:
            worker_jack  = Workers(username="Bobr")
            worker_michael  = Workers(username="Volk")
            session.add_all([worker_jack, worker_michael]) # await не нужен ибо мы не отправляем никуда данные
            # после flush мы отправили в БД изменения но еще не закомитили их можем делать остальные запросы - если нужно
            await session.flush() # flush взаимодействует с БД, поэтому пишем await
            await session.commit()
        logger.success('Data workers inserted successfully!')
    

    @staticmethod
    async def insert_resumes():
        async with async_session_maker() as session:
            junior = Resumes(
                title="Python Junior Developer", compensation=50000, workload=Workload.fulltime,worker_id=1
                )
            data_engeneer = Resumes(
                title="Python Data Engeneer", compensation=250000, workload=Workload.parttime,worker_id=2
                )
            developer = Resumes(
                title="Python Разработчик", compensation=150000, workload=Workload.fulltime,worker_id=1
                )
            scientist = Resumes(
                title="Data Scientist", compensation=300000, workload=Workload.fulltime,worker_id=2
                )
            session.add_all([junior, data_engeneer, developer, scientist]) 

            await session.commit()
        logger.success('Data resumes inserted successfully!')


    @staticmethod
    async def select_workers():
        async with async_session_maker() as session:
            query = select(Workers)
            result = await session.execute(query)
            workers = result.scalars().all()
            for worker in workers:
                logger.info(f"Worker ID: {worker.id}, Username: {worker.username}")


    @staticmethod
    async def update_worker(worker_id: int = 2, new_username: str = "Misha"):
        async with async_session_maker() as session:
            worker_michael = await session.get(Workers, worker_id) # получаем объект
            worker_michael.username = new_username
            await session.refresh(worker_michael) # обновляем объект
            await session.commit()

    @staticmethod
    async def select_resumes_avg_compensation(like_language: str = "Python"):
        '''
        select workload, avg(compensation)::int as avg_compensation
        from resumes
        where title like '%Python%' and compensation > 40000
        group by workload
        '''
        async with async_session_maker() as session:
            query=(
                select(
                    Resumes.workload,
                    func.avg(Resumes.compensation).cast(Integer).label("avg_compensation")
                )
                .select_from(Resumes)
                .filter(and_(
                    Resumes.title.contains(like_language),
                    Resumes.compensation > 40000,
                ))
                .group_by(Resumes.workload)
                .having(func.avg(Resumes.compensation) > 70000)
            )
            logger.info(query.compile(compile_kwargs={"literal_binds": True}))
            res = await session.execute(query)
            result = res.all()
            logger.info(result[0].avg_compensation)


    @staticmethod
    async def select_workers_with_lazy_relationship():
        async with async_session_maker() as session:
            query = (
                select(Workers)
            )
            
            res = await session.execute(query)
            result = res.scalars().all()

            # worker_1_resumes = result[0].resumes  # -> Приведет к ошибке
            # Нельзя использовать ленивую подгрузку в асинхронном варианте!

            # Ошибка: sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. 
            # Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)


    @staticmethod
    async def select_workers_with_joined_relationship(): # подходит для one2one many2one загрузки, не подходит для one2many
        async with async_session_maker() as session:
            query = (
                select(Workers)
                .options(joinedload(Workers.resumes))
            )
            
            res = await session.execute(query)
            result = res.unique().scalars().all() # unique запрос делается на уровне питона, чтобы алхимия не ругалась на дубликаты

            worker_1_resumes = result[0].resumes
            logger.success('Получить информация работника 1') 
            for resume in worker_1_resumes:
                # logger.info(resume.__dict__)           
                logger.info(resume.title, resume.compensation)
            
            worker_2_resumes = result[1].resumes
            logger.success('Получить информация работника 2')
            for resume in worker_2_resumes:
                # logger.info(resume.__dict__)
                logger.info(resume.title, resume.compensation)


    @staticmethod
    async def select_workers_with_selectin_relationship(): # подходит для one2many и many2many
        async with async_session_maker() as session:
            query = (
                select(Workers)
                .options(selectinload(Workers.resumes))
            )
            
            res = await session.execute(query)
            result = res.scalars().all()

            worker_1_resumes = result[0].resumes
            logger.success(worker_1_resumes)

            worker_2_resumes = result[1].resumes
            logger.success(worker_2_resumes)

    @staticmethod
    async def select_workers_with_condition_relationship():
        async with async_session_maker() as session:
            query = (
                select(Workers)
                .options(selectinload(Workers.resumes_parttime))
            )

            res = await session.execute(query)
            result = res.scalars().all()
            logger.success(result)


    @staticmethod
    async def convert_workers_to_dto():
        async with async_session_maker() as session:
            query = (
                select(Workers)
                .options(selectinload(Workers.resumes))
                .limit(2)
            )

            res = await session.execute(query)
            result_orm = res.scalars().all()
            logger.info(f"{result_orm}")
            result_dto = [WorkersRelDTO.model_validate(row, from_attributes=True) for row in result_orm]
            logger.info(f"{result_dto}")
            return result_dto




'''
@staticmethod — это декоратор в Python, который указывает, что метод является статическим. Статический метод:
Не требует экземпляра класса:
Его можно вызывать напрямую из класса, без создания объекта.
Не имеет доступа к экземпляру (self) или классу (cls):
Он работает как обычная функция, но находится внутри класса для логической группировки.


Что возвращает execute?

Для запросов SELECT:
Возвращает объект Result, из которого можно извлечь данные с помощью методов:
result.all() — все строки.
result.first() — первая строка.
result.scalar() — первое значение первой строки.
result.mappings() — строки в виде словарей.

Для запросов INSERT, UPDATE, DELETE:
Возвращает объект ResultProxy, который содержит информацию о выполненной операции (например, количество затронутых строк).

.filter_by
Особенности:
Использует именованные аргументы:
Фильтрация происходит по именам столбцов и их значениям.
Подходит для простых фильтров:
Удобен, когда нужно отфильтровать данные по конкретным значениям столбцов.
Не поддерживает сложные условия:
Нельзя использовать операторы сравнения (например, >, <, !=) или комбинировать условия через and_, or_.
query = select(User).filter_by(username="alice", age=25)

.filter
Особенности:
Использует выражения SQLAlchemy:
Фильтрация происходит с помощью SQLAlchemy-выражений, таких как User.username == "alice".
Подходит для сложных фильтров:
Можно использовать операторы сравнения (>, <, !=), комбинировать условия через and_, or_, а также применять функции (например, like, in_).
query = select(User).filter(
    or_(
        User.username == "alice",
        User.age < 30
    )
)

'''