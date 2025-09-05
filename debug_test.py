#!/usr/bin/env python3
"""
Script di debugging per WebLib che testa ogni componente individualmente
per identificare dove si verifica l'errore di sottrazione tra stringhe.
"""

import sys
import traceback
from weblib import *
from weblib.components import *
from weblib.app import WebApp, PageBuilder
from weblib.html import *

# Setup base app
app = WebApp("WebLib Debug Test")

# Test di ogni componente individualmente
def test_component(name, component_fn, args=None):
    """Testa un singolo componente e cattura eventuali errori."""
    args = args or {}
    print(f"\n{'='*50}")
    print(f"Testing component: {name}")
    print(f"{'='*50}")
    try:
        component = component_fn(**args)
        html_result = component.render()
        print(f"✅ SUCCESS: Component {name} renders correctly")
        return True
    except Exception as e:
        print(f"❌ ERROR in component {name}: {str(e)}")
        traceback.print_exc()
        return False

# Funzione per una pagina minima di test con un solo componente
def create_test_page(name, component):
    @app.route(f"/{name.lower()}")
    def test_page(request):
        page = PageBuilder(title=f"Test {name}")
        page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css")
        
        container = Div(classes=[CSS.CONTAINER, CSS.MT_5])
        container.add_child(H1(f"Testing {name}", classes=[CSS.TEXT_CENTER, "mb-4"]))
        
        # Aggiungi il componente di test
        try:
            container.add_child(component)
            container.add_child(P("✅ Component rendered successfully!", classes=["text-success", "mt-3"]))
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            container.add_child(Div(error_msg, classes=["alert", "alert-danger", "mt-3"]))
            print(error_msg)
            traceback.print_exc()
            
        page.add_to_body(container)
        return page.build()

# Crea un indice di tutti i test
@app.route("/")
def index(request):
    page = PageBuilder(title="WebLib Debug Tests")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css")
    
    container = Div(classes=[CSS.CONTAINER, CSS.MT_5])
    container.add_child(H1("WebLib Component Debug Tests", classes=[CSS.TEXT_CENTER, "mb-4"]))
    container.add_child(P("Click on each link to test individual components.", classes=[CSS.LEAD, CSS.TEXT_CENTER, "mb-5"]))
    
    # Lista di link ai test
    test_list = Ul(classes=["list-group", "mb-4"])
    for name in components_to_test:
        test_list.add_child(
            Li(A(name, href=f"/{name.lower()}"), classes=["list-group-item", "list-group-item-action"])
        )
    
    container.add_child(test_list)
    page.add_to_body(container)
    
    return page.build()

# ---------------------------------------------------------------
# TEST 1: Componenti UI Base
# ---------------------------------------------------------------

print("\n🔍 Testing Basic HTML Components...")
test_component("Div", Div, {"content": "Test Div"})
test_component("P", P, {"content": "Test Paragraph"})
test_component("H1", H1, {"content": "Test Heading"})
test_component("A", A, {"content": "Test Link", "href": "#"})
test_component("Button", Button, {"content": "Test Button"})

# ---------------------------------------------------------------
# TEST 2: Bootstrap Components
# ---------------------------------------------------------------

print("\n🔍 Testing Bootstrap Components...")
test_component("Card", Card, {"title": "Test Card", "text": "Card content"})
test_component("Alert", Alert, {"message": "Test alert", "type": "info"})
test_component("Badge", Badge, {"text": "New"})

# ---------------------------------------------------------------
# TEST 3: Pagination - Possibile fonte del problema
# ---------------------------------------------------------------

print("\n🔍 Testing Pagination Component...")
try:
    # Test con diversi tipi di parametri per trovare il problema
    print("Testing pagination with integer params...")
    test_component("Pagination Int", Pagination, {"current_page": 1, "total_pages": 5})
    
    print("Testing pagination with string params (that are numbers)...")
    test_component("Pagination Str-Num", Pagination, {"current_page": "1", "total_pages": "5"})
    
    print("Testing pagination with string params (non-numbers)...")
    test_component("Pagination Str", Pagination, {"current_page": "one", "total_pages": "five"})
except Exception as e:
    print(f"❌ ERROR during pagination tests: {str(e)}")
    traceback.print_exc()

# ---------------------------------------------------------------
# TEST 4: Chart Components
# ---------------------------------------------------------------

print("\n🔍 Testing Chart Components...")
try:
    print("Testing charts with proper data types...")
    labels = ["Jan", "Feb", "Mar"]
    data = [10, 20, 30]
    
    test_component("LineChart", quick_line_chart, {"chart_id": "lineChart", "labels": labels, "data": data})
    test_component("BarChart", quick_bar_chart, {"chart_id": "barChart", "labels": labels, "data": data})
    test_component("PieChart", quick_pie_chart, {"chart_id": "pieChart", "labels": labels, "data": data})
    
    print("Testing charts with string data (that should be numbers)...")
    str_data = ["10", "20", "30"]
    test_component("LineChart Str", quick_line_chart, {"chart_id": "lineChartStr", "labels": labels, "data": str_data})
except Exception as e:
    print(f"❌ ERROR during chart tests: {str(e)}")
    traceback.print_exc()

# ---------------------------------------------------------------
# TEST 5: Forms
# ---------------------------------------------------------------

print("\n🔍 Testing Form Components...")
try:
    from weblib.forms import StringField, EmailField, FormValidator
    
    class TestForm(FormValidator):
        username = StringField(required=True)
        email = EmailField(required=True)
    
    form = TestForm()
    test_component("Form", form.render_form, {"action": "/test", "method": "POST"})
except Exception as e:
    print(f"❌ ERROR during form tests: {str(e)}")
    traceback.print_exc()

# ---------------------------------------------------------------
# Elenco dei componenti da testare nel browser
# ---------------------------------------------------------------

components_to_test = [
    "Card", 
    "Alert", 
    "Badge", 
    "Pagination", 
    "Progress", 
    "ButtonGroup",
    "LineChart",
    "BarChart"
]

# Crea route di test per ogni componente
create_test_page("Card", Card(title="Test Card", text="This is a test card content"))
create_test_page("Alert", Alert(message="This is a test alert", type="info"))
create_test_page("Badge", Badge(text="New"))
create_test_page("Pagination", Pagination(current_page=1, total_pages=5))
create_test_page("Progress", Progress(value=60, label="60%"))

# ButtonGroup test
create_test_page("ButtonGroup", ButtonGroup(buttons=[
    Button("Left", classes=[CSS.BTN_SECONDARY]),
    Button("Middle", classes=[CSS.BTN_SECONDARY]),
    Button("Right", classes=[CSS.BTN_SECONDARY]),
]))

# Chart tests
labels = ["Jan", "Feb", "Mar"]
data = [10, 20, 30]
create_test_page("LineChart", quick_line_chart("lineChart", labels, data))
create_test_page("BarChart", quick_bar_chart("barChart", labels, data))

# ---------------------------------------------------------------
# Esegui il server per testare interattivamente
# ---------------------------------------------------------------

if __name__ == "__main__":
    print("\n🚀 Starting test server...")
    print("Visit http://127.0.0.1:5000 to test components interactively.")
    app.run(debug=True)
