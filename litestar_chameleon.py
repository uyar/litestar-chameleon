# Copyright 2026 H. Turgut Uyar <uyar@tekir.org>
#
# Permission to use, copy, modify, and/or distribute this software
# for any purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
from collections.abc import Mapping
from functools import partial
from pathlib import Path
from typing import Any

from chameleon import PageTemplate, PageTemplateFile, PageTemplateLoader
from litestar.exceptions import (
    ImproperlyConfiguredException,
    TemplateNotFoundException,
)
from litestar.template import TemplateEngineProtocol, TemplateProtocol
from litestar.template.base import TemplateCallableType, csrf_token, url_for


type Context = Mapping[str, Any]
type TemplateCallables = dict[str, TemplateCallableType]


class ChameleonTemplate(TemplateProtocol):
    def __init__(
        self,
        template: PageTemplateFile,
        template_callables: TemplateCallables,
    ) -> None:
        super().__init__()
        self.template: PageTemplateFile = template
        self.template_callables: TemplateCallables = template_callables

    def render(self, *args: Any, **kwargs: Any) -> str:
        template_callables = {}
        for key, template_callable in self.template_callables.items():
            template_callables[key] = partial(template_callable, kwargs)
        return self.template(*args, **(kwargs | template_callables))


class ChameleonTemplateEngine(
    TemplateEngineProtocol[ChameleonTemplate, Context]
):
    def __init__(
        self,
        directory: Path | list[Path] | None = None,
        engine_instance: PageTemplateLoader | None = None,
    ) -> None:
        reload = os.getenv("CHAMELEON_AUTO_RELOAD", "false").lower() == "true"
        match (directory, engine_instance):
            case (Path(), None):
                engine = PageTemplateLoader(
                    search_path=str(directory),
                    auto_reload=reload,
                )
            case (list(), None):
                search_path = list(map(str, directory))
                engine = PageTemplateLoader(
                    search_path=search_path,
                    auto_reload=reload,
                )
            case (None, PageTemplateLoader()):
                engine = engine_instance
            case _:
                raise ImproperlyConfiguredException("either a search path or a Chameleon PageTemplateLoader instance must be provided")  # noqa: E501
        self.engine: PageTemplateLoader = engine
        self._template_callables: TemplateCallables = {}
        self.register_template_callable("csrf_token", csrf_token)
        self.register_template_callable("url_for", url_for)

    def get_template(self, template_name: str) -> ChameleonTemplate:
        try:
            return ChameleonTemplate(
                self.engine[template_name],
                template_callables=self._template_callables,
            )
        except ValueError as exc:
            raise TemplateNotFoundException(
                template_name=template_name
            ) from exc

    def render_string(self, template_string: str, context: Context) -> str:
        return PageTemplate(template_string)(**context)

    def register_template_callable[**P, T](
        self,
        key: str,
        template_callable: TemplateCallableType[Context, P, T],
    ) -> None:
        self._template_callables[key] = template_callable
