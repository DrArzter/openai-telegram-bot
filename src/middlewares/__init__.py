# middlewares/__init__.py
from aiogram import Dispatcher
from pathlib import Path
from typing import Optional, List
from utils.logger import get_logger
from utils.module_loader import discover_modules

logger = get_logger(__name__)


def include_middlewares(
    dp: Dispatcher,
    exclude: Optional[List[str]] = None,
    only_include: Optional[List[str]] = None,
) -> None:
    """
    Discovers and registers all middlewares with priority, exclusion, and inclusion logic.
    """

    discovered_middlewares = discover_modules(
        package_path=Path(__file__).parent,
        package_name=__name__,
        export_name="middleware",
        exclude=exclude,
        only_include=only_include,
    )

    discovered_middlewares.sort(key=lambda item: item["priority"])

    for mw_info in discovered_middlewares:
        dp.update.middleware(mw_info["export"])
        logger.info(
            f"Middleware from {mw_info['package']}.{mw_info['name']} included successfully (priority: {mw_info['priority']})"
        )
