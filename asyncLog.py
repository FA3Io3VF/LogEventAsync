
import asyncio
from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Query
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

Base = declarative_base()
engine = create_async_engine('sqlite+aiosqlite:///log.db', future=True, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession)

class LogError(Base):
    __tablename__ = 'log_error'
    id = Column(Integer, primary_key=True, autoincrement=True)
    error = Column(String, nullable=False)
    function = Column(String, nullable=False)
    motivation = Column(String, nullable=False)
    user = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    event = Column(Boolean, nullable=False, default=False)

class LogErrorResponse(BaseModel):
    error: str
    function: str
    motivation: str
    user: str
    timestamp: datetime
    event: bool

class DateRangeRequest(BaseModel):
    start_date: str
    end_date: str

class LogErrorActor:
    def __init__(self, session_maker: sessionmaker):
        self._lock = asyncio.Lock()
        self._session_maker = session_maker

    async def register_error(self, error: str, function: str, motivation: str, user: str, event: bool = False):
        async with self._lock:
            log = LogError(
                error=error,
                function=function,
                motivation=motivation,
                user=user,
                timestamp=datetime.now(),
                event=event
            )

            async with self._session_maker() as session:
                session.add(log)

                try:
                    await session.commit()
                except:
                    await session.rollback()
                    raise

    async def _get_user_errors(self, query: Query) -> List[LogErrorResponse]:
        async with self._lock:
            async with self._session_maker() as session:
                try:
                    errors = await session.execute(query)
                    return [LogErrorResponse(**row) for row in errors.all()]
                except:
                    await session.rollback()
                    raise

    async def get_user_errors(self, user: str, event: bool = None) -> List[LogErrorResponse]:
        query = Query(LogError).filter_by(user=user)
        if event is not None:
            query = query.filter_by(event=event)
        return await self._get_user_errors(query)

    async def get_date_errors(self, date: datetime) -> List[LogErrorResponse]:
        query = Query(LogError).filter_by(timestamp=date)
        return await self._get_user_errors(query)

    async def get_date_range_errors(self, start_date: datetime, end_date: datetime) -> List[LogErrorResponse]:
        query = Query(LogError).filter(LogError.timestamp.between(start_date, end_date))
        return await self._get_user_errors(query)

app = FastAPI()

log_error_actor = LogErrorActor(async_session)

@app.on_event("startup")
async def startup_event():
    try:
        raise Exception("Test error")
    except Exception as e:
        await log_error_actor.register_error(str(e), "startup_event", "Testing", "admin", True)

@app.post("/errors")
async def register_error(error: str, function: str, motivation: str, user: str, event: bool = False):
    await log_error_actor.register_error(error, function, motivation, user, event)
    return {"message": "Error registered successfully"}

@app.get("/user_errors/{user}")
async def get_user_errors(user: str, event: bool = None) -> List[LogErrorResponse]:
    errors = await log_error_actor.get_user_errors(user, event)
    if not errors:
        raise HTTPException(status_code=404, detail="Errors not found")
    return errors

@app.get("/date_errors/{date}")
async def date_errors(date: datetime) -> List[LogErrorResponse]:
    errors = await log_error_actor.get_date_errors(date)
    if not errors:
        raise HTTPException(status_code=404, detail="Errors not found")
    return errors

@app.post("/date_range_errors")
async def date_range_errors(request: DateRangeRequest) -> List[LogErrorResponse]:
    start_date = datetime.fromisoformat(request.start_date)
    end_date = datetime.fromisoformat(request.end_date)
    errors = await log_error_actor.get_date_range_errors(start_date, end_date)
    if not errors:
        raise HTTPException(status_code=404, detail="Errors not found")
    return errors
