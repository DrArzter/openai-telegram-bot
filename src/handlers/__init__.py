# handlers/__init__.py
from aiogram import Dispatcher
from pathlib import Path
from typing import Optional, List
from utils.logger import get_logger
from utils.module_loader import discover_modules

logger = get_logger(__name__)


def include_routers(
    dp: Dispatcher,
    exclude: Optional[List[str]] = None,
    only_include: Optional[List[str]] = None,
) -> None:
    """
    Discovers and registers all routers with priority, exclusion, and inclusion logic.
    """
    discovered_routers = discover_modules(
        package_path=Path(__file__).parent,
        package_name=__name__,
        export_name="router",
        exclude=exclude,
        only_include=only_include,
    )

    discovered_routers.sort(key=lambda item: item["priority"])

    for router_info in discovered_routers:
        dp.include_router(router_info["export"])
        logger.info(
            f"Router from {router_info['package']}.{router_info['name']} included successfully (priority: {router_info['priority']})"
        )
