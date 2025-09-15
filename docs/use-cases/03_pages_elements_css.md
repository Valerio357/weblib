03 — Page, Elements e CSS

Obiettivo: comporre HTML con DSL `E.*` e applicare CSS inline scoping.

DSL HTML e Page

```python
from weblib.page import Page
from weblib.elements import E

page = (
    Page(title="UI")
    .body(
        E.div(
            E.h1("Titolo"),
            E.p("Paragrafo"),
            E.a("Link", href="/", cls="btn"),
        ).cls("container")
    )
)
```

CSS inline scoped

```python
from weblib.css import CSS, css

base = CSS.scope("base").add(
    css("body", {"font-family": "system-ui", "margin": "0"}),
    css(".container", {"max-width": "720px", "margin": "0 auto"}),
)

page = page.use_css(base)
```

Component di base

```python
from weblib.elements import Component, E

class Card(Component):
    def render(self):
        return E.div(
            E.div(self.title, cls="card-title"),
            E.div(self.content, cls="card-text"),
            cls="card"
        )

card = Card(title="Hello", content="World")
```

Note

- Gli attributi sono normalizzati: `cls`→`class`, `data_id`→`data-id`, `for_`→`for`.
- Escaping HTML è automatico per il testo.

