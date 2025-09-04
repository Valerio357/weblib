# 3. Interactive and Overlay Components

This guide explores components that provide interactivity, overlays, and dynamic content displays.

## Modal

Modals are dialog boxes that are displayed on top of the current page. They are used for important messages, forms, or multi-step processes.

### Example

```python
from weblib import Modal, Button

# A modal dialog.
modal_example = Modal(
    id="exampleModal",
    title="Modal Title",
    size="lg",  # Optional size: 'sm', 'lg', 'xl'
    footer=Div([
        Button("Close", classes=["btn", "btn-secondary"], attrs={"data-bs-dismiss": "modal"}),
        Button("Save Changes", classes=["btn", "btn-primary"])
    ])
).add_child(
    P("This is the content of the modal. You can put any component inside.")
)

# You also need a button to trigger the modal.
trigger_button = Button(
    "Launch Modal",
    classes=["btn", "btn-primary"],
    attrs={
        "data-bs-toggle": "modal",
        "data-bs-target": "#exampleModal"
    }
)

print(trigger_button.render())
print(modal_example.render())
```

### Key Properties
- `id`: A unique ID for the modal, used to trigger it.
- `title`: The text displayed in the modal's header.
- `size`: The width of the modal (`sm`, `lg`, `xl`).
- `footer`: Components to be placed in the modal's footer.
- Children of the `Modal` instance will be placed in its body.

---

## Accordion

An accordion is a vertically stacked list of items where each item can be expanded or collapsed to reveal its content.

### Example

```python
from weblib import Accordion

# An accordion with multiple items.
accordion_example = Accordion(
    id="myAccordion",
    items=[
        {
            "title": "Accordion Item #1",
            "content": "This is the first item's accordion body."
        },
        {
            "title": "Accordion Item #2",
            "content": "This is the second item's accordion body."
        }
    ],
    always_open=True # Allows multiple items to be open at once.
)

print(accordion_example.render())
```

### Key Properties
- `id`: A unique ID for the accordion group.
- `items`: A list of dictionaries, each with a `title` and `content`.
- `flush`: If `True`, removes borders for a seamless appearance.
- `always_open`: If `True`, multiple accordion items can be expanded simultaneously.

---

## Dropdown

Dropdowns are toggleable menus for displaying lists of links or actions.

### Example

```python
from weblib import Dropdown

# A dropdown menu.
dropdown_example = Dropdown(
    label="Dropdown Menu",
    variant="secondary",
    items=[
        {"text": "Action", "href": "#"},
        {"text": "Another action", "href": "#"},
        "divider", # Adds a horizontal line.
        {"text": "Separated link", "href": "#"}
    ]
)

print(dropdown_example.render())
```

### Key Properties
- `label`: The text on the dropdown's trigger button.
- `variant`: The color style of the button.
- `items`: A list of dictionaries (with `text` and `href`) or the string `"divider"`.
- `split`: If `True`, creates a split button dropdown.
- `direction`: The direction the menu opens (`down`, `up`, `start`, `end`).

---

## Offcanvas

Offcanvas is a sidebar component that can be toggled to appear from the side of the viewport.

### Example

```python
from weblib import Offcanvas, Button

# The Offcanvas component itself.
offcanvas_example = Offcanvas(
    id="myOffcanvas",
    title="Offcanvas Title",
    placement="start", # 'start', 'end', 'top', 'bottom'
    content=[
        P("This is the content of the offcanvas sidebar.")
    ]
)

# A button to trigger the offcanvas.
trigger_button = Button(
    "Open Offcanvas",
    classes=["btn", "btn-primary"],
    attrs={
        "data-bs-toggle": "offcanvas",
        "data-bs-target": "#myOffcanvas"
    }
)

print(trigger_button.render())
print(offcanvas_example.render())
```

### Key Properties
- `id`: A unique ID for the offcanvas component.
- `title`: The header text.
- `placement`: The side from which the component appears (`start`, `end`, `top`, `bottom`).
- `content`: A list of components to display inside the offcanvas body.

---

## Tooltip and Popover

Tooltips and Popovers provide small overlays of information on hover or click.

### Example

```python
from weblib import Tooltip, Popover

# A button with a tooltip.
tooltip_example = Tooltip(
    trigger="Hover for Tooltip",
    title="This is a tooltip!",
    placement="top"
)

# A button with a popover.
popover_example = Popover(
    trigger="Click for Popover",
    title="Popover Title",
    content="And here's some amazing content. It's very engaging.",
    placement="right"
)

# Note: You need to initialize tooltips and popovers with JavaScript.
# Example JS:
# var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
# var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
#   return new bootstrap.Tooltip(tooltipTriggerEl)
# })

print(tooltip_example.render())
print(popover_example.render())
```

### Key Properties (`Tooltip`)
- `trigger`: The content of the element that triggers the tooltip.
- `title`: The text to display in the tooltip.
- `placement`: The position of the tooltip (`top`, `bottom`, `left`, `right`).

### Key Properties (`Popover`)
- `trigger`: The content of the element that triggers the popover.
- `title`: The header text of the popover.
- `content`: The body content of the popover.
- `placement`: The position of the popover.
```
