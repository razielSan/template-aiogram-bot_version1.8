import pytest
from aiohttp import ClientSession
from aiohttp import request, web

from app.error_handlers.network import error_handler_for_the_website


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [
        403,
        404,
        205,
        101,
        216,
        301,
        310,
        501,
        513
    ],
)
async def test_error_status_code_response(
    aiohttp_server, fake_logging_data, status
):
    """
    Тестируем на отличные от 200 кода статусы.

    Работа с error_handler_for_the_website.
    """
    # Определяем какие данные будет отдавать web запрос
    async def handler(request):
        return web.Response(status=status)

    app = web.Application()  # веб приложение
    app.router.add_get("/", handler)  # url запроса
    server = await aiohttp_server(app)  # сервер для отправки запроса

    # делаем запроса
    async with ClientSession() as session:
        resp = await error_handler_for_the_website(
            session=session,
            url=str(server.make_url("/")),
            logging_data=fake_logging_data,
        )

    # Проверяем статус код и наличие ошбики
    assert resp.status == status
    assert resp.error is not None



