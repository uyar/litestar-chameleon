import pytest

from pathlib import Path

from litestar import Litestar, get
from litestar.response import Template
from litestar.template import TemplateConfig
from litestar.testing import TestClient

from litestar_chameleon import ChameleonTemplateEngine


@get("/")
async def demo() -> Template:
    return Template("demo.pt", context={"title": "Demo", "body": "Demo page text"})


@pytest.fixture()
def app() -> Litestar:
    """A demo application."""
    templates_dir = Path(__file__).parent
    template_config = TemplateConfig(
        engine=ChameleonTemplateEngine,
        directory=templates_dir,
    )

    routes = [demo]
    return Litestar(route_handlers=routes, template_config=template_config)


@pytest.fixture()
def client(app) -> TestClient:
    """A test client for the demo application."""
    return TestClient(app=app)
