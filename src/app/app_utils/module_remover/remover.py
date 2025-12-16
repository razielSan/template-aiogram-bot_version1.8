import shutil
from pathlib import Path


def remove_module(
    name: str,
    log_path: Path,
    temp_path: Path,
    modules_path: Path,
):

    modules_path = modules_path / name

    if not modules_path.exists():
        print(f"Модуль {name} не найден")
        return

    # 1. Удаляем модуль
    result = input(
        f"Вы точно хотите удалить модуль - {name}\n1. "
        "Да - Нажмите 'Enter'\n2. Нет - Отправьте любой символ"
    )
    if not result:
        shutil.rmtree(modules_path)
        print(f"Модуль {modules_path} " "и его дочерние модули успешно удалены")
    else:
        print(f"Удаление модуля {modules_path} отменено")
        return

    # 2. Удлаляем temp папки
    temp_folder = temp_path / name
    if temp_folder.exists():
        shutil.rmtree(temp_folder)
        print(f"Удалена папка {temp_folder} и ее дочерние папки")

    # 3. Удлаляем логи
    log_path = log_path / name
    if log_path.exists():
        shutil.rmtree(log_path)
        print(f"Удалены логи - {log_path}")

    print(f"Процедура удаления {modules_path} завершена")
