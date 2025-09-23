# utils/module_loader.py
import importlib
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def discover_modules(
    package_path: Path,
    package_name: str,
    export_name: str,
    exclude: Optional[List[str]] = None,
    only_include: Optional[List[str]] = None,
) -> List[dict]:
    """
    Recursively discovers modules within a package and extracts their exported instances and priorities.
    """
    exclude = exclude or []
    only_include = only_include or []
    discovered = []

    for item in package_path.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            subpackage_name = f"{package_name}.{item.name}"
            discovered.extend(
                discover_modules(item, subpackage_name, export_name, exclude, only_include)
            )
        elif item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
            module_name = item.stem

            if only_include and module_name not in only_include:
                continue
            if module_name in exclude:
                continue

            try:
                module = importlib.import_module(f".{module_name}", package=package_name)
                export_instance = getattr(module, export_name, None)
                priority = getattr(module, "priority", 50)
                
                if export_instance:
                    discovered.append({
                        "export": export_instance,
                        "priority": priority,
                        "name": module_name,
                        "package": package_name
                    })
            except Exception as e:
                logger.exception(
                    f"Failed to process module {package_name}.{module_name}: {e}"
                )
    return discovered