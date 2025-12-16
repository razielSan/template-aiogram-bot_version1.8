Ну все вроде начинаю разбираться по маленьку =)
Сделад в pyproject.toml команду cli и убрал manage.py функцию

[project]
name = "bot-app"
version = "0.1.0"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[project.scripts]
bot = "app.main:main"
cli = "app.cli:main"

Так же в тестах протестриовал еще две функции

import sys
from pathlib import Path

from aiogram import Dispatcher

from app.app_utils.module_creator.creator import create_module
from app.app_utils.module_loader.loader import (
    load_modules,
    get_child_modules_settings_inline_data,
    get_child_modules_settings_temp_folder,
)
from app.settings.init_logging import root_error_logger
from app.core.modules_loader import ModuleInfo


def test_load_modules_integration(tmp_path: Path):
    # Создаем структуру
    modules_path = tmp_path / "test_app" / "bot" / "modules"
    modules_path.mkdir(parents=True)
    modules = [
        "video/childes/audio",
        "video/childes/temp",
        "video/childes/data",
        "video/childes/create",
        "video/childes/create/childes/temp",
        "video/childes/create/childes/data",
        "video/childes/create/childes/name",
        "video/childes/create/childes/name/childes/test",
        "test",
        "audio/childes/create",
        "create/childes/data",
    ]

    result = create_module(list_path_modules=modules, rel_path_to_modules=modules_path)

    assert result.error is None
    dp = Dispatcher()
    try:
        sys.path.insert(0, str(tmp_path))

        list_modules = load_modules(
            dp=dp,
            error_logger=root_error_logger,
            modules_path=Path(
                modules_path,
            ),
            root_package="test_app.bot.modules",
        )
        assert len(list_modules) == 14

        for module in list_modules:
            assert isinstance(module, ModuleInfo)
            assert module.router is not None
            assert module.settings is not None

        # Тестируем на возможных вариантах функции get_child_modules_settings_inline_data
        array_video = get_child_modules_settings_inline_data(
            module_path=modules_path / Path("video/childes"),
            root_package="test_app.bot.modules.video.childes",
            error_logger=root_error_logger,
        )
        assert len(array_video) == 4

        array_video_create = get_child_modules_settings_inline_data(
            module_path=modules_path / Path("video/childes/create/childes"),
            root_package="test_app.bot.modules.video.childes.create.childes",
            error_logger=root_error_logger,
        )
        assert len(array_video_create) == 3

        array_video_create_name = get_child_modules_settings_inline_data(
            module_path=modules_path
            / Path("video/childes/create/childes/name/childes"),
            root_package="test_app.bot.modules.video.childes.create.childes.name.childes",
            error_logger=root_error_logger,
        )
        assert len(array_video_create_name) == 1

        array_test = get_child_modules_settings_inline_data(
            module_path=modules_path / Path("test/childes"),
            root_package="test_app.bot.modules.test.childes",
            error_logger=root_error_logger,
        )
        assert len(array_test) == 0

        array_audio = get_child_modules_settings_inline_data(
            module_path=modules_path / Path("audio/childes"),
            root_package="test_app.bot.modules.audio.childes",
            error_logger=root_error_logger,
        )
        assert len(array_audio) == 1

        array_audio_create = get_child_modules_settings_inline_data(
            module_path=modules_path / Path("audio/childes/create/childes"),
            root_package="test_app.bot.modules.audio.childes.create.childes",
            error_logger=root_error_logger,
        )
        assert len(array_audio_create) == 0

        # Тестирование функции get_child_modules_settings_temp_folder
        array_temp_folder = get_child_modules_settings_temp_folder(
            module_path=modules_path,
            error_logger=root_error_logger,
            root_package="test_app.bot.modules"
        )
        assert len(array_temp_folder) == 14

    finally:
        sys.path.remove(str(tmp_path))

Вроде пока не ломается =)

(venv) D:\ProgrammingProjects\Python\Bot\Project\BOT_PROJECT\func_store_botV1.4>pytest tests
======================================= test session starts =======================================
platform win32 -- Python 3.8.10, pytest-8.3.5, pluggy-1.5.0
rootdir: D:\ProgrammingProjects\Python\Bot\Project\BOT_PROJECT\func_store_botV1.4
configfile: pytest.ini
collected 13 items

tests\test_create_module.py ............                                                     [ 92%]
tests\test_load_modules.py .                                                                 [100%]

======================================= 13 passed in 8.05s ========================================


Теперь я функцию где загружаю модули беру путь файла и от него от относительный путь от переданного
полного пути и получаю rel_path, затем беру переданый root_package("app.bot.modules") и соединяю его с
rel_path заменяя "/" на "." это правильный вариант ? root_package обязтелен я так понимаю ?
путь от app.bot.modules 

def load_modules(
    dp,
    modules_path: Path,
    error_logger: Logger,
    root_package: str,
) -> List[ModuleInfo]:
    """
    Проходится по всем папкам внутри переданного пути.

    Ищет внутри папок файлы router.py и settings.py.
    Внутри router.py ищет обьект router
    Внутри settings.py ищет обьект settings

    Если файлов settings.py или router.py идет дальше по папкам
    Если произошла ошибка импорта пишет в лог

    Args:
        modules_path (Path): Относительный путь до нужного модуля

        Пример
        bot/modules/video

        error_logger (Logger): Логер для записи в лог ошибок

    Returns:
        List[ModuleInfo]: обьект содержащий в себе

        Атрибуты ModuleInfo]:
            - root (str | None): Если роутер корневой будет указно его имя если нет None
            - settings (object): Обьект с настройками
            - router (object): Обьект router
            - parent (str | None): Если корневой роутер то будет None если child то имя
              корневого роутера
    """
    try:
        modules: List = []  # список из ModuleInfo
        root_router = None  # корневой роутер текущего модуля
        # Проходися по всем файлам содержащим router.py
        for router_file in modules_path.rglob("router.py"):
            module_dir: Path = router_file.parent
            # ПРоверяем содержится ли в пути settings.py
            settings_file: Path = module_dir / "settings.py"
            if not settings_file.exists():
                continue

            # Относительный импорт
            rel_path = router_file.parent.relative_to(modules_path)
            import_module = f"{root_package}.{rel_path.as_posix().replace('/', '.')}"
            # Безопасно имопртируем settings и router
            settings_module = safe_import(
                f"{import_module}.settings",
                error_logger=error_logger,
            )

            if not settings_module:
                continue

            router_module = safe_import(
                f"{import_module}.router",
                error_logger=error_logger,
            )
            if not router_module:
                continue

            # Проверяем есть ли внутри settings и router данные
            settings = getattr(settings_module, "settings", None)
            router = getattr(router_module, "router", None)
            register = getattr(
                router_module, "register", None
            )  # для подключения роутера

            # вычисляем по rel_path_to_root - root_name и parent
            rel_path_to_root = module_dir.relative_to(
                modules_path
            ).parts  # ["audio"], ["audio", "childes", "create"]

            # Проверяем являет ли router корневой или дочернем
            # Корневой(root_name="имя корневого роутера", parent=None)
            # Дочерний(root_name=None, parent="имя корневого роутера")
            root_name = rel_path_to_root[0] if len(rel_path_to_root) == 1 else None
            parent_name = rel_path_to_root[0] if len(rel_path_to_root) > 1 else None

            parent_router = (
                True if parent_name else False
            )  # определяем является ли роутер дочерним
            if (
                not parent_router
            ):  # Если роутер не дочерним кладем root_router  корневой роутер
                root_router = router

            # если есть в файле есть register то подключаем роутер
            if register:
                register(
                    dp=dp,
                    parent_router=parent_router,
                    root_router=root_router,
                )

            if settings and router:
                modules.append(
                    ModuleInfo(
                        root=root_name,
                        settings=settings,
                        router=router,
                        parent=parent_name,
                    )
                )
            else:
                error_logger.error(
                    f"[AUTO IMPORT ERROR] Обьекты {settings} и {router} не найдены"
                )

        return modules
    except Exception as err:
        error_logger.exception(err)
        
        
pyroject.toml хорошая штука надо про него поподробнее узнать
