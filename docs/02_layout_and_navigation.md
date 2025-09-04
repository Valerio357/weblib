# 2. Layout and Navigation Components

This guide covers components used for structuring pages and providing navigation.

## NavBar

The `NavBar` component creates a responsive navigation bar at the top of your page.

### Example

```python
from weblib import NavBar, Div, A

# A dark-themed navigation bar.
navbar_example = NavBar(
    brand="📚 WebLib Docs",
    theme="dark",
    classes=["bg-dark"],
    links=[
        {"text": "Home", "url": "/"},
        {"text": "Features", "url": "#features"},
        {"text": "About", "url": "#about"}
    ],
    children=[
        Div([
            A("GitHub", href="#", classes=["btn", "btn-outline-light", "btn-sm"])
        ])
    ]
)

print(navbar_example.render())
```

### Key Properties
- `brand`: The text or component for the brand logo area.
- `theme`: The color scheme (`light` or `dark`).
- `classes`: Custom CSS classes for the `<nav>` element.
- `links`: A list of dictionaries, where each dictionary defines a navigation link with `text` and `url`.
- `children`: A list of additional components to be placed in the navbar, typically aligned to the right.

---

## Breadcrumb

Breadcrumbs indicate the current page's location within a navigational hierarchy.

### Example

```python
from weblib import Breadcrumb

# A breadcrumb trail.
breadcrumb_example = Breadcrumb(
    items=[
        {"text": "Home", "url": "/"},
        {"text": "Library", "url": "/library"},
        {"text": "Data"} # The last item is automatically marked as active.
    ]
)

print(breadcrumb_example.render())
```

### Key Properties
- `items`: A list of dictionaries or strings representing the path. Each dictionary should have `text` and an optional `url`.

---

## Pagination

The `Pagination` component is used to navigate between pages of content.

### Example

```python
from weblib import Pagination

# Pagination for a list of items.
pagination_example = Pagination(
    current_page=3,
    total_pages=10,
    base_url="?page="
)

print(pagination_example.render())
```

### Key Properties
- `current_page`: The currently active page number.
- `total_pages`: The total number of pages available.
- `base_url`: The URL prefix for page links. The page number will be appended to this URL.

---

## NavTabs

`NavTabs` create a tabbed navigation interface, useful for switching between different views of content.

### Example

```python
from weblib import NavTabs

# A set of navigation tabs.
navtabs_example = NavTabs(
    items=[
        {"text": "Profile", "href": "#profile", "active": True},
        {"text": "Settings", "href": "#settings"},
        {"text": "Contact", "href": "#contact", "disabled": True}
    ]
)

# To create "pills" style tabs:
navpills_example = NavTabs(
    items=[...],
    pills=True
)

print(navtabs_example.render())
```

### Key Properties
- `items`: A list of dictionaries, each defining a tab with `text`, `href`, and optional `active` or `disabled` status.
- `pills`: If `True`, styles the tabs as pills instead of standard tabs.
- `fill`: If `True`, forces the tabs to fill the full width of their parent.
- `justified`: If `True`, makes tabs equal-width.

---

## ListGroup

`ListGroup` is a flexible component for displaying a series of content.

### Example

```python
from weblib import ListGroup

# A simple list group.
list_group_example = ListGroup(
    items=[
        "An item",
        "A second item",
        "A third item"
    ]
)

# A more complex list group with links and contextual classes.
list_group_links = ListGroup(
    items=[
        {"content": "Homepage", "href": "/", "active": True},
        {"content": "Features", "href": "/features"},
        {"content": "Pricing", "href": "/pricing", "variant": "success"}
    ]
)

print(list_group_links.render())
```

### Key Properties
- `items`: A list of strings or dictionaries. Dictionaries can specify `content`, `href`, `active`, `disabled`, and `variant`.
- `flush`: If `True`, removes borders and rounded corners to render items edge-to-edge.
- `numbered`: If `True`, uses an ordered list (`<ol>`) to number the items.
- `horizontal`: If `True`, displays the list group items horizontally.
```
