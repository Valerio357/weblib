#!/usr/bin/env python3
"""
🛍️ ShopLib Ultra Simple - Versione minimalista
"""

from weblib import *

# Configura framework CSS
set_css_framework('bootstrap')

# Crea app
app = WebApp(__name__)

# Dati semplici
CATEGORIES = [
    {"id": 1, "name": "Elettronica", "description": "Smartphone e laptop"},
    {"id": 2, "name": "Abbigliamento", "description": "Vestiti e scarpe"}
]

PRODUCTS = [
    {"id": 1, "name": "iPhone", "price": 999.99, "category_id": 1},
    {"id": 2, "name": "MacBook", "price": 1499.99, "category_id": 1},
    {"id": 3, "name": "Jeans", "price": 79.99, "category_id": 2}
]

@app.get('/')
def home(request):
    """Homepage semplice"""
    page = app.create_page("ShopLib Ultra Simple")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    
    content = [
        Div([
            H1("🛍️ ShopLib Ultra Simple", classes=["text-center", "mb-4"]),
            
            H2("📦 Prodotti"),
            Div([
                Card(
                    content=[
                        Div([
                            H5(product["name"], classes=["card-title"]),
                            P(f"€{product['price']:.2f}", classes=["text-primary"]),
                            Button("Aggiungi", classes=["btn", "btn-primary"])
                        ], classes=["card-body"])
                    ],
                    classes=["mb-3"]
                ).render()
                for product in PRODUCTS
            ])
        ], classes=["container", "mt-5"])
    ]
    
    page.add_to_body(Div(content))
    return page.build().render()

if __name__ == "__main__":
    print("🚀 Avviando ShopLib Ultra Simple...")
    print("🌐 URL: http://127.0.0.1:5001")
    
    try:
        app.run(debug=True, port=5001, host='127.0.0.1')
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
