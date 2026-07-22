# src/output/template_engine.py
"""
テンプレートエンジンモジュール
JSONテンプレートの読み込みと変数置換を行う
"""
import json
import os
import re
import logging
from typing import Dict, Any

from ..utils import safe_str, validate_template_id

logger = logging.getLogger(__name__)


class TemplateEngine:
    """テンプレートベースのJSON生成エンジン"""

    def __init__(self, config: dict, enable_hot_reload: bool = False):
        self.directory = config.get("directory", "templates")
        self.mapping = config.get("mapping", {})
        self.id_cell = config.get("id_cell", "A1")
        self.enable_hot_reload = enable_hot_reload

        self._cache: Dict[str, tuple] = {}

        os.makedirs(self.directory, exist_ok=True)

    # ============================================================
    # Load
    # ============================================================

    def load(self, template_id: str, force_reload: bool = False) -> Any:
        template_id = template_id.strip().strip("[]")
        if not validate_template_id(template_id):
            raise ValueError(f"Invalid template ID: {template_id}")

        filename = self.mapping.get(template_id)
        if not filename:
            # フォールバック: templates/<template_id>.json
            fallback_name = f"{template_id}.json"
            path = os.path.realpath(os.path.join(self.directory, fallback_name))
            if os.path.exists(path):
                filename = fallback_name
            else:
                raise KeyError(
                    f"Template ID '{template_id}' not found in mapping and no fallback file {fallback_name}"
                )

        path = os.path.realpath(
            os.path.join(self.directory, filename)
        )

        real_dir = os.path.realpath(self.directory)

        if not path.startswith(real_dir):
            raise ValueError("Path traversal detected")

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        if force_reload or self.enable_hot_reload:
            self._reload_if_updated(template_id, path)

        if template_id in self._cache:
            return self._cache[template_id][1]

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._cache[template_id] = (
            os.path.getmtime(path),
            data
        )

        return data

    def _reload_if_updated(
        self,
        template_id: str,
        path: str
    ) -> None:
        """
        更新時キャッシュ破棄
        """
        mtime = os.path.getmtime(path)

        if template_id in self._cache:
            cached_mtime, _ = self._cache[template_id]

            if mtime > cached_mtime:
                del self._cache[template_id]

    # ============================================================
    # Render
    # ============================================================

    def render(
        self,
        template: Any,
        variables: Dict[str, Any]
    ) -> Any:
        """
        テンプレート再帰レンダリング
        dict key / value 両対応
        """
        if isinstance(template, dict):
            return {
                self.render(k, variables): self.render(v, variables)
                for k, v in template.items()
            }

        if isinstance(template, list):
            return [
                self.render(item, variables)
                for item in template
            ]

        if isinstance(template, str):
            return self._replace_vars(template, variables)

        return template

    def _replace_vars(
        self,
        text: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        {{var}} 置換
        """
        pattern = r"\{\{([^}]+)\}\}"

        def replacer(match):
            var_name = match.group(1).strip()

            special_map = {
                "$index": "_row_index",
                "$file": "_source_file",
                "$sheet": "_source_sheet",
                "$env": "_env",
            }

            if var_name in special_map:
                return safe_str(
                    variables.get(special_map[var_name], "")
                )

            if var_name in variables:
                return safe_str(variables[var_name])

            logger.warning(
                f"Variable not found: {var_name}"
            )

            return match.group(0)

        return re.sub(pattern, replacer, text)

    # ============================================================
    # Utility
    # ============================================================

    def clear_cache(self) -> None:
        self._cache.clear()
