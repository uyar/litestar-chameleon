# litestar-chameleon

litestar-chameleon lets developers use
[Chameleon](https://chameleon.readthedocs.io/) templates
in [Litestar](https://litestar.dev/) applications.

## Usage

When creating the application:

```python
from litestar.template import TemplateConfig
from litestar_chameleon import ChameleonTemplateEngine

template_config = TemplateConfig(
    engine=ChameleonTemplateEngine,
    directory=templates_dir,
)

app = Litestar(..., template_config=template_config, ...)
```

When using it in a route:

```python
from litestar.response import Template

@get("/")
async def demo() -> Template:
    return Template(
        "demo.pt",
        context={"title": "...", "body": "..."},
    )
```
