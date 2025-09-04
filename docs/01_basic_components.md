# 1. Basic Components

This guide covers the fundamental UI components in WebLib. These are the building blocks for creating user interfaces.

## Card

Cards are versatile containers for displaying content. They can include a header, footer, title, text, and more.

### Example

```python
from weblib import Card, H5, Small

# A card with a header, title, text, and footer.
card_example = Card(
    header=H5("Featured Content"),
    title="Card Title",
    text="This is some text inside the card body. It's great for descriptions.",
    footer=Small("Card Footer", classes=["text-muted"]),
    classes=["shadow-sm", "mb-4"]
)

# To render the component, call .render()
print(card_example.render())
```

### Key Properties
- `header`: Content for the card's header section.
- `title`: A shortcut to create a title within the card body.
- `text`: A shortcut for a paragraph of text in the card body.
- `footer`: Content for the card's footer section.
- `classes`: A list of custom CSS classes to apply to the card.

---

## Alert

Alerts display contextual feedback messages for typical user actions.

### Example

```python
from weblib import Alert

# A success alert that can be dismissed by the user.
alert_success = Alert(
    message="Success! Your action was completed.",
    type="success",  # Can be 'success', 'info', 'warning', 'danger'.
    dismissible=True
)

# A non-dismissible warning alert.
alert_warning = Alert(
    message="Warning! Please double-check your input.",
    type="warning"
)

print(alert_success.render())
print(alert_warning.render())
```

### Key Properties
- `message`: The text to display in the alert.
- `type`: The style of the alert (`success`, `info`, `warning`, `danger`).
- `dismissible`: If `True`, a close button is added.

---

## Badge

Badges are small components used for counts, labels, or status indicators.

### Example

```python
from weblib import Badge, Span

# A simple primary badge.
badge_primary = Badge(text="Primary", variant="primary")

# A rounded "pill" badge with a number inside.
badge_notification = Badge(
    text="Notifications", 
    variant="secondary", 
    pill=True
).add_child(Span(" 4", classes=["ms-1"])) # Add child elements

print(badge_primary.render())
print(badge_notification.render())
```

### Key Properties
- `text`: The label for the badge.
- `variant`: The color style (`primary`, `secondary`, `success`, etc.).
- `pill`: If `True`, the badge has fully rounded corners.

---

## Button

Buttons are used to trigger actions and events.

### Example

```python
from weblib import Button

# A standard primary button.
button_primary = Button("Primary Button", classes=["btn", "btn-primary"])

# An outline-styled button.
button_outline = Button("Outline Button", classes=["btn", "btn-outline-secondary"])

# A large success button.
button_large = Button("Large Button", classes=["btn", "btn-success", "btn-lg"])

print(button_primary.render())
```

### Key Properties
- `classes`: A list of CSS classes to style the button (e.g., `btn`, `btn-primary`).

---

## Spinner

Spinners provide a visual cue that an action is being processed.

### Example

```python
from weblib import Spinner

# Standard "border" spinner.
spinner_border = Spinner(type="border", variant="primary")

# "Growing" circle spinner.
spinner_grow = Spinner(type="grow", variant="info", size="sm")

print(spinner_border.render())
print(spinner_grow.render())
```

### Key Properties
- `type`: The animation style (`border` or `grow`).
- `variant`: The color of the spinner.
- `size`: The size (`sm` for small).

---

## Progress

Progress bars display the completion status of a task.

### Example

```python
from weblib import Progress

# A 60% complete progress bar.
progress_bar = Progress(
    value=60,              # The current progress value (0-100).
    label="60% Complete",  # Optional text label.
    striped=True,          # Adds a striped pattern.
    animated=True,         # Animates the stripes.
    variant="info"
)

print(progress_bar.render())
```

### Key Properties
- `value`: The percentage of completion.
- `label`: Text displayed on the progress bar.
- `striped`: If `True`, applies a striped style.
- `animated`: If `True`, animates the stripes (requires `striped=True`).
- `variant`: The color of the progress bar.
```
