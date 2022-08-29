import os
import aioredis
from random import randint
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi_limiter import FastAPILimiter
from fastapi.responses import RedirectResponse
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
from dependency_injector.wiring import inject, Provide

from core.redis.containers import Container
from core.redis.services import Service
from user.schemas import UserCreate, UserCode, UserResend
from core.db import database
from user import services
from utils.sms import send_sms

app = FastAPI()
app.state.database = database

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    """The function is executed when turned on server"""
    # Redis create connection
    redis_host = os.environ.get('REDIS_HOST')
    redis_pass = os.environ.get('REDIS_PASSWORD')
    redis = await aioredis.create_redis(f"redis://{redis_host}", password=redis_pass)
    await FastAPILimiter.init(redis)
    # Postgres database connect
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    """The function is executed when switched off server"""
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    """Redirect from '/' path to '/docs'"""
    return RedirectResponse(url='/docs')


@app.post(
    '/signup',
    dependencies=[Depends(RateLimiter(times=3, seconds=60))],
    summary="Create new user",
    status_code=status.HTTP_201_CREATED)
@inject
async def create_user(data: UserCreate, service: Service = Depends(Provide[Container.service])):
    """
    Register user

    :param data: class 'user.schemas.UserCreate', parameters: email: str, phone: str, birthday: date, password: str
    :param service
    :return: object
    """
    # Add user to database
    phone = await services.create_user(data)
    if phone:
        code: str = str(randint(000000, 999999))
        # Add to Redis code
        await service.process(phone, code)
        # Send SMS
        result: bool = await send_sms(code, data.phone)
        if result:
            return {'status': 'success', 'message': 'Code sent successfully'}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred while registering"
        )


@app.post(
    '/code',
    dependencies=[Depends(RateLimiter(times=3, seconds=60))],
    summary="Verification code sent to phone",
    status_code=status.HTTP_200_OK
)
@inject
async def check_code(data: UserCode, service: Service = Depends(Provide[Container.service])):
    """
    Check code from sms

    :param data: class 'user.schemas.UserCode', parameters: code: str, phone: str
    :param service
    :return: object
    """
    # Get code from Redis
    code = await service.get_value(data.phone)
    if code == data.code:
        # Get User Data
        user = await services.get_user(data)
        # Delete code from redis db
        await service.remove_key(data.phone)
        return {
            'status': 'success',
            'message': 'Successful phone verification',
            'data': user
        }
    else:
        return {'status': 'error', 'message': 'Code is wrong'}


@app.post(
    '/resend',
    dependencies=[Depends(RateLimiter(times=1, seconds=60))],
    summary="Resend code",
    status_code=status.HTTP_200_OK)
@inject
async def resend_code(data: UserResend, service: Service = Depends(Provide[Container.service])):
    """
    Resend code

    :param data: class 'user.schemas.UserResend', parameters: phone: str
    :param service
    :return: object
    """
    code: str = str(randint(000000, 999999))
    # Add to Redis code
    await service.process(data.phone, code)
    # Send SMS
    result: bool = await send_sms(code, data.phone)
    if result:
        return {'status': 'success', 'message': 'Code sent successfully'}


container = Container()
container.config.redis_host.from_env("REDIS_HOST", "redis")
container.config.redis_password.from_env("REDIS_PASSWORD", "password")
container.wire(modules=[__name__])
