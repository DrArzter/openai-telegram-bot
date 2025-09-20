# middlewares/__init__.py
from pathlib import Path
import importlib
from aiogram import Dispatcher
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def include_middlewares(
    dp: Dispatcher, path: Optional[Path] = None, package: Optional[str] = None
) -> None:
    """
    Recursively includes all middleware objects from middleware directory and subdirectories.
    Each file should export a 'middleware' variable (instance of BaseMiddleware)
    """
    if path is None:
        path = Path(__file__).parent
    if package is None:
        package = __name__

    for item in path.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            subpackage = f"{package}.{item.name}"
            include_middlewares(dp, path=item, package=subpackage)
        elif item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
            module_name = item.stem
            try:
                module = importlib.import_module(f".{module_name}", package=package)
                mw = getattr(module, "middleware", None)
                if mw is not None:
                    dp.update.middleware(mw)  # type: ignore
                    logger.info(
                        f"Middleware from {package}.{module_name} included successfully"
                    )
            except Exception as e:
                logger.exception(
                    f"Failed to include middleware from {package}.{module_name}: {e}"
                )
