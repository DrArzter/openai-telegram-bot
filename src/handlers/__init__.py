# handlers/__init__.py
from typing import Optional
from aiogram import Dispatcher
import importlib
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


def include_routers(
    dp: Dispatcher, path: Optional[Path] = None, package: Optional[str] = None
) -> None:
    """
    Recursively includes all routers from a handlers directory and its subdirectories.

    :param dp: Dispatcher instance to register routers.
    :param path: Path to the current folder (used internally for recursion).
    :param package: Package name for importlib (used internally for recursion).
    """
    if path is None:
        path = Path(__file__).parent
    if package is None:
        package = __name__

    for item in path.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            # Recurse into subpackage
            subpackage = f"{package}.{item.name}"
            include_routers(dp, path=item, package=subpackage)
        elif item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
            module_name = item.stem
            try:
                module = importlib.import_module(f".{module_name}", package=package)
                router = getattr(module, "router", None)
                if router is not None:
                    dp.include_router(router)  # type: ignore
                    logger.info(
                        f"Router from {package}.{module_name} included successfully"
                    )
            except ModuleNotFoundError as e:
                logger.error(f"Module not found: {package}.{module_name} - {e}")
            except Exception as e:
                logger.exception(
                    f"Failed to include router from {package}.{module_name}: {e}"
                )
