# 🚀 WebLib: The Pythonic Web Framework

**Build modern, data-driven web applications with 100% Python. No HTML, no JavaScript, just pure productivity.**

**[➡️ View the Live Demo](https://weblib-landing-page.onrender.com/)**

WebLib is a powerful Python library for building web applications with a programmatic approach. Create complete, interactive web apps with built-in support for CSS frameworks, databases, authentication, and UI components.

## ✨ Key Features

- **🐍 100% Python**: Build complex UIs without writing a single line of HTML or JavaScript.
- **🧩 Rich Component Library**: Over 30 ready-to-use components, from navbars to data tables.
- **📊 Built-in Data Visualization**: Create interactive charts with a single function call.
- **� Integrated Authentication**: Secure user authentication and session management out of the box.
- **� Flexible ORM**: Interact with your database using intuitive Python objects. Supports PostgreSQL, SQLite, and more.
- **⚡ High Performance**: Built on Starlette and Uvicorn for asynchronous speed.

---

## 🚀 Quick Start: A Complete Starter App

This example demonstrates a complete, runnable application with a navbar, a card, a chart, and a paginated list of items.

**File: `app.py`**
```python
#!/usr/bin/env python3
from weblib import WebApp, PageBuilder
from weblib.components import *
from weblib.charts import quick_line_chart
from weblib.html import Div, H1, P
from weblib.config import CSSClasses as CSS
from weblib.utils import extract_query_param

# 1. Initialize the App
app = WebApp("WebLib Starter App")

# 2. Sample Data
sample_items = [f"Item {i}" for i in range(1, 101)]
sales_data = {"labels": ["Jan", "Feb", "Mar"], "data": [100, 150, 120]}

# 3. Create the Main Route
@app.route("/")
def index(request):
    """Main page showcasing various components."""
    page = PageBuilder(title="WebLib Starter Pack")
    
    # Add Bootstrap CSS and JS
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css")
    page.add_js("https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js")
    page.add_js("https://cdn.jsdelivr.net/npm/chart.js")

    # --- Page Content ---
    
    # Navbar
    navbar = NavBar(brand="MyApp", links=[
        {"text": "Home", "url": "/"},
        {"text": "About", "url": "/about"}
    ])
    page.add_to_body(navbar)

    # Main Container
    container = Div(classes=[CSS.CONTAINER, CSS.MT_5])
    
    # Header
    container.add_child(H1("Welcome to WebLib!", classes=[CSS.TEXT_CENTER, "mb-4"]))
    container.add_child(P("A complete starter example.", classes=[CSS.LEAD, CSS.TEXT_CENTER, "mb-5"]))

    # Grid for components
    row = Div(classes=[CSS.ROW])
    
    # Card and Chart
    chart = quick_line_chart("salesChart", sales_data["labels"], sales_data["data"])
    row.add_child(Div(Card(title="Sales Chart", content=[chart]), classes=[CSS.COL_MD_6, CSS.MB_4]))
    
    # Paginated List
    page_num = extract_query_param(request.query_string, "page", 1, as_int=True)
    items_per_page = 10
    total_pages = (len(sample_items) + items_per_page - 1) // items_per_page
    
    start_index = (page_num - 1) * items_per_page
    end_index = start_index + items_per_page
    paginated_items = sample_items[start_index:end_index]
    
    item_list = Ul([Li(item, classes=["list-group-item"]) for item in paginated_items], classes=["list-group"])
    
    pagination_component = Pagination(
        current_page=page_num,
        total_pages=total_pages,
        base_url="/?page="
    )
    
    list_card = Card(title="Paginated List", content=[item_list, pagination_component])
    row.add_child(Div(list_card, classes=[CSS.COL_MD_6, CSS.MB_4]))

    container.add_child(row)
    page.add_to_body(container)
    
    return page.build()

# 4. Run the App
if __name__ == "__main__":
    print("🚀 Starting WebLib Starter App on http://127.0.0.1:5000")
    app.run(debug=True)
```

**To run this example:**
1. Save the code as `app.py`.
2. Install the necessary dependencies:
   ```bash
   pip install starlette uvicorn python-multipart
   ```
3. Run the script:
   ```bash
   python app.py
   ```
4. Open `http://127.0.0.1:5000` in your browser.

---

## 📖 Core Concepts

### Components
WebLib provides a rich set of pre-built components.

```python
# Simple Card
Card(title="My Card", text="This is the content of the card.")

# Alert Message
Alert(message="Operation successful!", type="success")

# Navigation Bar
NavBar(brand="MyApp", links=[{"text": "Home", "url": "/"}])
```

### Layouts
Structure your page with responsive grids.

```python
container = Div(classes=[CSS.CONTAINER])
row = Div(classes=[CSS.ROW])

col1 = Div(Card(title="First"), classes=[CSS.COL_MD_6])
col2 = Div(Card(title="Second"), classes=[CSS.COL_MD_6])

row.add_child(col1).add_child(col2)
container.add_child(row)
```

### Charts
Generate charts from your Python data.

```python
# Line Chart
chart = quick_line_chart(
    chart_id="myChart", 
    labels=["Jan", "Feb", "Mar"], 
    data=[10, 20, 15]
)
```

### Forms & ORM
Define forms and database models with Python classes.

```python
# forms.py
class RegistrationForm(FormValidator):
    username = StringField(required=True)
    email = EmailField(required=True)

# models.py
class User(Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True)
    email = Column(String(120), unique=True)

# app.py
@app.route("/register", methods=["GET", "POST"])
def register(request):
    form = RegistrationForm()
    if request.method == "POST" and form.validate(request.form_data):
        User.create_user(db=db, **form.data)
        return Response("User created!")
    return form.render_form()
```

---

## �️ Installation

To use WebLib, you need Python 3.7+ and pip.

```bash
# Install core library and dependencies
pip install starlette uvicorn python-multipart sqlalchemy psycopg2-binary passlib python-jose bcrypt requests
```

## 🤝 Contributing

We welcome contributions! Please see our [contributing guide](CONTRIBUTING.md) for more details.

1. **Fork** the repository.
2. **Create** a feature branch (`git checkout -b feature/my-feature`).
3. **Commit** your changes (`git commit -m 'Add my new feature'`).
4. **Push** to the branch (`git push origin feature/my-feature`).
5. **Open** a Pull Request.

## ⚖️ License

WebLib is released under the **Apache 2.0 License**. See the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ and Python | © 2025 WebLib**
