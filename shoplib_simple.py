#!/usr/bin/env python3
"""
🛍️ ShopLib Simple - E-commerce App con WebLib v2.0
Versione semplificata che evita errori di database
"""

import os
import json
from datetime import datetime, timedelta
from weblib import *

print("🛍️ Inizializzazione ShopLib Simple - E-commerce App")
print("=" * 50)

# Configurazione
set_css_framework('bootstrap')  # Cambia in 'tailwind' o 'bulma' per diversi stili

# Inizializza app
app = WebApp(__name__)

# === DATI IN MEMORIA (evita problemi DB) ===
CATEGORIES = [
    {"id": 1, "name": "Elettronica", "description": "Smartphone, laptop, accessori tech", "image_url": "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=300"},
    {"id": 2, "name": "Abbigliamento", "description": "Moda uomo, donna e bambini", "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300"},
    {"id": 3, "name": "Casa & Giardino", "description": "Arredamento, decorazioni, giardinaggio", "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300"},
    {"id": 4, "name": "Sport & Tempo Libero", "description": "Attrezzature sportive, hobby", "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300"}
]

PRODUCTS = [
    # Elettronica
    {"id": 1, "name": "iPhone 15 Pro", "description": "Ultimo iPhone con chip A17 Pro", "price": 1199.99, "original_price": 1299.99, "category_id": 1, "stock_quantity": 50, "is_featured": True, "rating": 4.8, "reviews_count": 245, "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=300", "tags": ["smartphone", "apple", "new"]},
    {"id": 2, "name": "MacBook Air M3", "description": "Laptop ultra-sottile con chip M3", "price": 1499.99, "original_price": 1599.99, "category_id": 1, "stock_quantity": 30, "is_featured": True, "rating": 4.9, "reviews_count": 189, "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=300", "tags": ["laptop", "apple", "ultrabook"]},
    {"id": 3, "name": "AirPods Pro", "description": "Cuffie wireless con cancellazione rumore", "price": 249.99, "original_price": 279.99, "category_id": 1, "stock_quantity": 100, "rating": 4.7, "reviews_count": 567, "image_url": "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=300", "tags": ["audio", "wireless", "apple"]},
    
    # Abbigliamento  
    {"id": 4, "name": "Giacca Denim Classica", "description": "Giacca jeans unisex in cotone premium", "price": 79.99, "original_price": 99.99, "category_id": 2, "stock_quantity": 75, "rating": 4.5, "reviews_count": 123, "image_url": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=300", "tags": ["jeans", "unisex", "casual"]},
    {"id": 5, "name": "Sneakers Sportive", "description": "Scarpe running professionali", "price": 129.99, "original_price": 149.99, "category_id": 2, "stock_quantity": 60, "is_featured": True, "rating": 4.6, "reviews_count": 298, "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300", "tags": ["scarpe", "sport", "running"]},
    
    # Casa & Giardino
    {"id": 6, "name": "Pianta Monstera", "description": "Pianta d'appartamento tropicale", "price": 34.99, "original_price": 39.99, "category_id": 3, "stock_quantity": 25, "rating": 4.4, "reviews_count": 89, "image_url": "https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=300", "tags": ["piante", "decorazione", "verde"]},
    {"id": 7, "name": "Lampada Designer", "description": "Lampada da tavolo moderna LED", "price": 89.99, "original_price": 109.99, "category_id": 3, "stock_quantity": 40, "rating": 4.3, "reviews_count": 156, "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300", "tags": ["illuminazione", "design", "led"]},
    
    # Sport
    {"id": 8, "name": "Tappetino Yoga", "description": "Tappetino antiscivolo per yoga e fitness", "price": 29.99, "original_price": 34.99, "category_id": 4, "stock_quantity": 80, "rating": 4.5, "reviews_count": 234, "image_url": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=300", "tags": ["yoga", "fitness", "sport"]},
]

# Carrello in memoria (semplificato)
CART_ITEMS = []

# === UTILITÀ ===
def get_product_by_id(product_id):
    """Trova prodotto per ID"""
    for product in PRODUCTS:
        if product['id'] == product_id:
            return product
    return None

def get_category_by_id(category_id):
    """Trova categoria per ID"""
    for category in CATEGORIES:
        if category['id'] == category_id:
            return category
    return None

def get_products_by_category(category_id):
    """Trova prodotti per categoria"""
    return [p for p in PRODUCTS if p['category_id'] == category_id]

def get_featured_products():
    """Prodotti in evidenza"""
    return [p for p in PRODUCTS if p.get('is_featured', False)]

# === COMPONENTI CUSTOM ===
def ProductCard(product, show_actions=True):
    """Card prodotto riutilizzabile"""
    
    # Badge sconto
    discount_badge = ""
    if product['original_price'] > product['price']:
        discount = int(((product['original_price'] - product['price']) / product['original_price']) * 100)
        discount_badge = Badge(text=f"-{discount}%", variant="danger").render()
    
    # Stelle rating
    stars = "⭐" * int(product['rating'])
    
    # Prezzo
    price_html = f"€{product['price']:.2f}"
    if product['original_price'] > product['price']:
        price_html += f" <small class='text-muted'><del>€{product['original_price']:.2f}</del></small>"
    
    # Azioni
    actions = ""
    if show_actions:
        actions = Div([
            Button("🛒 Aggiungi", 
                  classes=[CSS.BTN_PRIMARY, "btn-sm", "add-to-cart"],
                  data_product_id=str(product['id']),
                  data_product_name=product['name']),
            A("👁️ Dettagli", href=f"/product/{product['id']}", classes=[CSS.BTN_SECONDARY, "btn-sm", CSS.ME_2])
        ], classes=["mt-2"]).render()
    
    return Card(
        content=[
            Div([
                Img(src=product['image_url'] or "https://via.placeholder.com/300x200", 
                   alt=product['name'],
                   classes=["card-img-top"],
                   style="height: 200px; object-fit: cover;"),
                discount_badge
            ], classes=["position-relative"]),
            
            Div([
                H5(product['name'], classes=["card-title"]),
                P(product['description'][:100] + ("..." if len(product['description']) > 100 else ""), 
                  classes=["card-text", "text-muted"]),
                Div([
                    Span(stars + f" ({product['reviews_count']})", classes=["small", "text-muted"]),
                    "<br>",
                    H4(price_html, classes=["text-primary", "mb-2"])
                ]),
                actions
            ], classes=[CSS.CARD_BODY])
        ],
        classes=["mb-4", "product-card"]
    )

def ShoppingNavbar(cart_count=0):
    """Navbar personalizzata per shop"""
    return NavBar(
        brand="🛍️ ShopLib",
        theme="light",
        classes=[CSS.get_color_class('light', 'bg'), "mb-4"],
        links=[
            {"text": "🏠 Home", "url": "/"},
            {"text": "📱 Elettronica", "url": "/category/1"},
            {"text": "👕 Abbigliamento", "url": "/category/2"},
            {"text": "🏠 Casa", "url": "/category/3"},
            {"text": "⚽ Sport", "url": "/category/4"},
        ],
        children=[
            Div([
                A(f"🛒 Carrello ({cart_count})", 
                  href="/cart", 
                  classes=[CSS.BTN_SUCCESS, "me-2"]),
                A("👤 Login", href="/login", classes=[CSS.BTN_SECONDARY])
            ], classes=[CSS.D_FLEX])
        ]
    )

# === ROUTES ===
@app.get('/')
def home(request):
    """Homepage con prodotti in evidenza"""
    
    # Prodotti in evidenza
    featured_products = get_featured_products()[:6]
    
    page = app.create_page("ShopLib - Il tuo negozio online")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    page.add_js("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
    
    content = [
        ShoppingNavbar(len(CART_ITEMS)).render(),
        
        # Hero section
        Div([
            Div([
                H1("🛍️ Benvenuto in ShopLib", classes=[CSS.TEXT_CENTER]),
                P("Il tuo negozio online con i migliori prodotti ai prezzi più convenienti", 
                  classes=[CSS.TEXT_CENTER, "lead"]),
                Div([
                    A("Scopri i Prodotti", href="#featured", classes=[CSS.BTN_PRIMARY, "btn-lg", CSS.ME_2]),
                    A("Vedi Categorie", href="#categories", classes=[CSS.BTN, CSS.get_color_class('light', 'bg')])
                ], classes=[CSS.TEXT_CENTER])
            ], classes=[CSS.CONTAINER])
        ], classes=[CSS.get_color_class('primary', 'bg'), CSS.get_color_class('white', 'text'), "py-5", "mb-5"]),
        
        # Prodotti in evidenza
        Div([
            H2("⭐ Prodotti in Evidenza", classes=[CSS.TEXT_CENTER, CSS.MB_3], id="featured"),
            
            Div([
                Div([
                    ProductCard(product).render()
                ], classes=[CSS.get_col_size(4)]) 
                for product in featured_products
            ], classes=[CSS.ROW]) if featured_products else Alert(
                message="Nessun prodotto in evidenza al momento", 
                type="info"
            ).render()
            
        ], classes=[CSS.CONTAINER, "mb-5"]),
        
        # Categorie
        Div([
            H2("📂 Categorie", classes=[CSS.TEXT_CENTER, CSS.MB_3], id="categories"),
            
            Div([
                Div([
                    Card(
                        content=[
                            Img(src=cat['image_url'] or "https://via.placeholder.com/300x200",
                               alt=cat['name'],
                               classes=["card-img-top"],
                               style="height: 200px; object-fit: cover;"),
                            Div([
                                H5(cat['name'], classes=["card-title"]),
                                P(cat['description'], classes=["card-text"]),
                                A("Esplora", href=f"/category/{cat['id']}", 
                                  classes=[CSS.BTN_PRIMARY])
                            ], classes=[CSS.CARD_BODY])
                        ]
                    ).render()
                ], classes=[CSS.get_col_size(6, 'md'), "mb-4"])
                for cat in CATEGORIES
            ], classes=[CSS.ROW])
            
        ], classes=[CSS.CONTAINER, "mb-5"]),
        
        # Footer
        Div([
            Div([
                Div([
                    H5("ShopLib"),
                    P("Il tuo negozio online di fiducia dal 2025")
                ], classes=[CSS.get_col_size(6, 'md')]),
                
                Div([
                    H5("Contatti"),
                    P("📧 info@shoplib.com<br>📞 +39 123 456 789")
                ], classes=[CSS.get_col_size(6, 'md')])
            ], classes=[CSS.ROW])
        ], classes=[CSS.CONTAINER, CSS.get_color_class('dark', 'bg'), CSS.get_color_class('white', 'text'), "py-4"])
    ]
    
    # JavaScript per carrello
    js_code = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Aggiungi al carrello
        document.querySelectorAll('.add-to-cart').forEach(btn => {
            btn.addEventListener('click', function() {
                const productId = this.dataset.productId;
                const productName = this.dataset.productName;
                
                fetch('/api/cart/add', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({product_id: parseInt(productId), quantity: 1})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ ' + productName + ' aggiunto al carrello!');
                        location.reload();
                    } else {
                        alert('❌ Errore: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Errore:', error);
                    alert('❌ Errore di connessione');
                });
            });
        });
    });
    </script>
    """
    
    page.add_to_body(Div(content))
    page.add_to_body(js_code)
    return page.build().render()


@app.get('/category/<int:category_id>')
def category_page(request, category_id):
    """Pagina categoria con filtri"""
    
    category = get_category_by_id(category_id)
    products = get_products_by_category(category_id)
    
    if not category:
        return Response("Categoria non trovata", status_code=404)
    
    page = app.create_page(f"{category['name']} - ShopLib")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    page.add_js("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
    
    content = [
        ShoppingNavbar(len(CART_ITEMS)).render(),
        
        Div([
            # Breadcrumb
            Nav([
                Ol([
                    Li(A("Home", href="/"), classes=["breadcrumb-item"]),
                    Li(category['name'], classes=["breadcrumb-item", "active"])
                ], classes=["breadcrumb"])
            ]),
            
            # Header categoria
            Div([
                H1(f"📂 {category['name']}"),
                P(category['description'], classes=["lead", CSS.get_color_class('muted', 'text')])
            ], classes=["mb-4"]),
            
            # Filtri
            Div([
                H5("🔍 Filtri"),
                Div([
                    Button("Tutti", classes=[CSS.BTN, CSS.get_color_class('light', 'bg'), "filter-btn", "active"],
                           data_filter="all"),
                    Button("In Sconto", classes=[CSS.BTN, CSS.get_color_class('light', 'bg'), "filter-btn"],
                           data_filter="discount"),
                    Button("Più Venduti", classes=[CSS.BTN, CSS.get_color_class('light', 'bg'), "filter-btn"],
                           data_filter="popular"),
                    Button("Novità", classes=[CSS.BTN, CSS.get_color_class('light', 'bg'), "filter-btn"],
                           data_filter="new")
                ], classes=["btn-group", "mb-4"])
            ]),
            
            # Prodotti
            Div([
                H5(f"🛍️ Prodotti ({len(products)})"),
                Div([
                    Div([
                        ProductCard(product).render()
                    ], classes=[CSS.get_col_size(4), "product-item"])
                    for product in products
                ], classes=[CSS.ROW], id="products-grid") if products else Alert(
                    message="Nessun prodotto trovato in questa categoria", 
                    type="info"
                ).render()
            ])
            
        ], classes=[CSS.CONTAINER])
    ]
    
    # JavaScript per filtri
    products_json = json.dumps([{
        'id': p['id'],
        'name': p['name'],
        'price': p['price'],
        'original_price': p['original_price'],
        'rating': p['rating'],
        'reviews_count': p['reviews_count'],
        'image_url': p['image_url'] or "",
        'description': p['description'],
        'has_discount': p['original_price'] > p['price'],
        'is_popular': p['reviews_count'] > 200,
        'is_new': True
    } for p in products])
    
    js_code = f"""
    <script>
    const products = {products_json};
    
    document.querySelectorAll('.filter-btn').forEach(btn => {{
        btn.addEventListener('click', function() {{
            // Reset active
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            let filteredProducts = products;
            
            if (filter === 'discount') {{
                filteredProducts = products.filter(p => p.has_discount);
            }} else if (filter === 'popular') {{
                filteredProducts = products.filter(p => p.is_popular);
            }} else if (filter === 'new') {{
                filteredProducts = products.filter(p => p.is_new);
            }}
            
            // Re-render products (simplified)
            const grid = document.getElementById('products-grid');
            if (filteredProducts.length === 0) {{
                grid.innerHTML = '<div class="col-12"><div class="alert alert-info">Nessun prodotto trovato con questo filtro</div></div>';
            }} else {{
                // For demo, just show/hide existing products
                document.querySelectorAll('.product-item').forEach((item, index) => {{
                    if (filteredProducts.some(p => p.id === products[index].id)) {{
                        item.style.display = 'block';
                    }} else {{
                        item.style.display = 'none';
                    }}
                }});
            }}
        }});
    }});
    </script>
    """
    
    page.add_to_body(Div(content))
    page.add_to_body(js_code)
    return page.build().render()


@app.get('/product/<int:product_id>')
def product_detail(request, product_id):
    """Dettaglio prodotto"""
    
    product = get_product_by_id(product_id)
    if not product:
        return Response("Prodotto non trovato", status_code=404)
    
    category = get_category_by_id(product['category_id'])
    
    # Prodotti correlati
    related_products = get_products_by_category(product['category_id'])
    related_products = [p for p in related_products if p['id'] != product['id']][:3]
    
    page = app.create_page(f"{product['name']} - ShopLib")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    page.add_js("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
    
    # Calcoli
    stars = "⭐" * int(product['rating'])
    discount_percent = 0
    if product['original_price'] > product['price']:
        discount_percent = int(((product['original_price'] - product['price']) / product['original_price']) * 100)
    
    content = [
        ShoppingNavbar(len(CART_ITEMS)).render(),
        
        Div([
            # Breadcrumb
            Nav([
                Ol([
                    Li(A("Home", href="/"), classes=["breadcrumb-item"]),
                    Li(A(category['name'], href=f"/category/{category['id']}"), classes=["breadcrumb-item"]),
                    Li(product['name'], classes=["breadcrumb-item", "active"])
                ], classes=["breadcrumb"])
            ]),
            
            # Prodotto principale
            Div([
                Div([
                    # Immagine
                    Img(src=product['image_url'] or "https://via.placeholder.com/500x400",
                       alt=product['name'],
                       classes=["img-fluid", "rounded"],
                       style="max-height: 400px; object-fit: cover;")
                ], classes=[CSS.get_col_size(6, 'md')]),
                
                Div([
                    # Info prodotto
                    H1(product['name']),
                    Div([
                        Span(stars + f" ({product['reviews_count']} recensioni)", 
                             classes=["text-muted"]),
                        Badge(text=f"Stock: {product['stock_quantity']}", 
                             variant="success" if product['stock_quantity'] > 10 else "warning").render()
                    ], classes=["mb-3"]),
                    
                    # Prezzo
                    Div([
                        H2(f"€{product['price']:.2f}", classes=["text-primary", "d-inline"]),
                        (" " + Span(f"€{product['original_price']:.2f}", 
                                   classes=["text-muted", "text-decoration-line-through", "ms-2"]) + 
                         " " + Badge(text=f"-{discount_percent}%", variant="danger").render()
                        ) if discount_percent > 0 else ""
                    ], classes=["mb-4"]),
                    
                    # Descrizione
                    P(product['description'], classes=["lead", "mb-4"]),
                    
                    # Tags
                    Div([
                        Badge(text=tag, variant="secondary").render() + " "
                        for tag in product['tags']
                    ], classes=["mb-4"]) if product['tags'] else "",
                    
                    # Azioni
                    Div([
                        Div([
                            Label("Quantità:", classes=["form-label"]),
                            Input(type="number", value="1", min="1", max=str(product['stock_quantity']),
                                 id="quantity", classes=[CSS.FORM_CONTROL])
                        ], classes=["mb-3", CSS.get_col_size(3)]),
                        
                        Div([
                            Button("🛒 Aggiungi al Carrello", 
                                  classes=[CSS.BTN_PRIMARY, "btn-lg", "me-2"],
                                  id="add-to-cart-btn"),
                            Button("❤️ Wishlist", 
                                  classes=[CSS.BTN, CSS.get_color_class('light', 'bg')])
                        ], classes=[CSS.get_col_size(9)])
                    ], classes=[CSS.ROW])
                    
                ], classes=[CSS.get_col_size(6, 'md')])
            ], classes=[CSS.ROW, "mb-5"]),
            
            # Prodotti correlati
            H3("🔗 Prodotti Correlati", classes=["mb-4"]) if related_products else "",
            Div([
                Div([
                    ProductCard(product, show_actions=False).render()
                ], classes=[CSS.get_col_size(4)])
                for product in related_products
            ], classes=[CSS.ROW]) if related_products else ""
            
        ], classes=[CSS.CONTAINER])
    ]
    
    # JavaScript
    js_code = f"""
    <script>
    document.getElementById('add-to-cart-btn').addEventListener('click', function() {{
        const quantity = parseInt(document.getElementById('quantity').value);
        
        fetch('/api/cart/add', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{product_id: {product['id']}, quantity: quantity}})
        }})
        .then(response => response.json())
        .then(data => {{
            if (data.success) {{
                alert('✅ Prodotto aggiunto al carrello!');
                window.location.href = '/cart';
            }} else {{
                alert('❌ Errore: ' + data.message);
            }}
        }})
        .catch(error => {{
            console.error('Errore:', error);
            alert('❌ Errore di connessione');
        }});
    }});
    </script>
    """
    
    page.add_to_body(Div(content))
    page.add_to_body(js_code)
    return page.build().render()


@app.get('/cart')
def cart_page(request):
    """Pagina carrello"""
    
    page = app.create_page("Carrello - ShopLib")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    page.add_js("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
    
    cart_total = sum(item['price'] * item['quantity'] for item in CART_ITEMS)
    
    content = [
        ShoppingNavbar(len(CART_ITEMS)).render(),
        
        Div([
            H1("🛒 Il tuo Carrello"),
            
            # Elementi carrello
            Div([
                Card(
                    content=[
                        Div([
                            H5(f"Totale: €{cart_total:.2f}", classes=["card-title"]),
                            P(f"Prodotti nel carrello: {len(CART_ITEMS)}", classes=["card-text"]),
                            Button("💳 Procedi al Checkout", classes=[CSS.BTN_SUCCESS]) if CART_ITEMS else ""
                        ], classes=[CSS.CARD_BODY])
                    ]
                ).render()
            ], classes=["mb-4"]) if CART_ITEMS else Alert(
                message="Il tuo carrello è vuoto. Inizia a fare shopping!",
                type="info"
            ).render(),
            
            Div([
                A("🛍️ Continua Shopping", href="/", classes=[CSS.BTN_PRIMARY, "me-2"]),
                A("📱 Elettronica", href="/category/1", classes=[CSS.BTN_SECONDARY])
            ])
            
        ], classes=[CSS.CONTAINER])
    ]
    
    page.add_to_body(Div(content))
    return page.build().render()


# === API ENDPOINTS ===
@app.post('/api/cart/add')
def api_add_to_cart(request):
    """API per aggiungere prodotti al carrello"""
    try:
        import json
        
        # Parse request data
        content = request.data.decode('utf-8') if hasattr(request, 'data') else '{}'
        data = json.loads(content) if content else {}
        
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Trova prodotto
        product = get_product_by_id(product_id)
        if not product:
            return Response(
                content=json.dumps({"success": False, "message": "Prodotto non trovato"}),
                headers={'Content-Type': 'application/json'},
                status_code=404
            )
        
        # Aggiungi al carrello
        cart_item = {
            'product_id': product_id,
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity,
            'image_url': product['image_url']
        }
        CART_ITEMS.append(cart_item)
        
        response_data = {"success": True, "message": "Prodotto aggiunto al carrello!"}
        
        return Response(
            content=json.dumps(response_data),
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        import json
        return Response(
            content=json.dumps({"success": False, "message": str(e)}),
            headers={'Content-Type': 'application/json'},
            status_code=400
        )


@app.get('/admin')
def admin_dashboard(request):
    """Dashboard amministrativo"""
    
    # Statistiche
    total_products = len(PRODUCTS)
    total_categories = len(CATEGORIES)
    total_orders = 0
    
    page = app.create_page("Admin Dashboard - ShopLib")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    page.add_js("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
    
    content = [
        NavBar(
            brand="🔧 ShopLib Admin",
            theme="dark",
            classes=[CSS.get_color_class('dark', 'bg'), "mb-4"],
            links=[
                {"text": "📊 Dashboard", "url": "/admin"},
                {"text": "📦 Prodotti", "url": "/admin/products"},
                {"text": "📂 Categorie", "url": "/admin/categories"},
                {"text": "🛒 Ordini", "url": "/admin/orders"},
                {"text": "👥 Clienti", "url": "/admin/customers"}
            ],
            children=[
                A("🏠 Vai al Sito", href="/", classes=[CSS.BTN, CSS.get_color_class('light', 'bg')])
            ]
        ).render(),
        
        Div([
            H1("📊 Dashboard Amministrativo"),
            
            # KPI Cards
            Div([
                Div([
                    Card(
                        content=[
                            Div([
                                H2(str(total_products), classes=["card-title", "text-primary"]),
                                P("📦 Prodotti Totali", classes=["card-text"])
                            ], classes=[CSS.CARD_BODY, CSS.TEXT_CENTER])
                        ],
                        classes=[CSS.get_color_class('light', 'bg')]
                    ).render()
                ], classes=[CSS.get_col_size(3)]),
                
                Div([
                    Card(
                        content=[
                            Div([
                                H2(str(total_categories), classes=["card-title", "text-success"]),
                                P("📂 Categorie", classes=["card-text"])
                            ], classes=[CSS.CARD_BODY, CSS.TEXT_CENTER])
                        ],
                        classes=[CSS.get_color_class('light', 'bg')]
                    ).render()
                ], classes=[CSS.get_col_size(3)]),
                
                Div([
                    Card(
                        content=[
                            Div([
                                H2(str(len(CART_ITEMS)), classes=["card-title", "text-warning"]),
                                P("🛒 Items Carrello", classes=["card-text"])
                            ], classes=[CSS.CARD_BODY, CSS.TEXT_CENTER])
                        ],
                        classes=[CSS.get_color_class('light', 'bg')]
                    ).render()
                ], classes=[CSS.get_col_size(3)]),
                
                Div([
                    Card(
                        content=[
                            Div([
                                H2("€12,450", classes=["card-title", "text-info"]),
                                P("💰 Revenue Demo", classes=["card-text"])
                            ], classes=[CSS.CARD_BODY, CSS.TEXT_CENTER])
                        ],
                        classes=[CSS.get_color_class('light', 'bg')]
                    ).render()
                ], classes=[CSS.get_col_size(3)])
            ], classes=[CSS.ROW, "mb-4"]),
            
            # Lista prodotti
            H3("📦 Lista Prodotti"),
            Div([
                Table([
                    Tr([
                        Th("ID"),
                        Th("Nome"),
                        Th("Categoria"),
                        Th("Prezzo"),
                        Th("Stock"),
                        Th("Rating")
                    ], classes=["table-dark"]),
                    [Tr([
                        Td(str(p['id'])),
                        Td(p['name']),
                        Td(get_category_by_id(p['category_id'])['name']),
                        Td(f"€{p['price']:.2f}"),
                        Td(str(p['stock_quantity'])),
                        Td("⭐" * int(p['rating']))
                    ]) for p in PRODUCTS]
                ], classes=["table", "table-striped"]).render()
            ], classes=["mb-4"]),
            
            # Azioni rapide
            H3("⚡ Azioni Rapide"),
            Div([
                Button("➕ Nuovo Prodotto", classes=[CSS.BTN_PRIMARY, CSS.ME_2]),
                Button("📂 Nuova Categoria", classes=[CSS.BTN_SUCCESS, CSS.ME_2]),
                Button("📊 Report Vendite", classes=[CSS.BTN_INFO, CSS.ME_2]),
                Button("⚙️ Impostazioni", classes=[CSS.BTN_SECONDARY])
            ], classes=["mb-4"])
            
        ], classes=[CSS.CONTAINER])
    ]
    
    page.add_to_body(Div(content))
    return page.build().render()


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🛍️ ShopLib Simple E-commerce App Avviata!")
    print("=" * 50)
    print("🌐 Server: http://127.0.0.1:5004")
    print("🎨 Framework CSS: Bootstrap (modifica set_css_framework)")
    print("💾 Dati: In memoria (niente database)")
    
    print("\n📋 Pagine disponibili:")
    print("  • / - Homepage con prodotti in evidenza")
    print("  • /category/1 - Elettronica")
    print("  • /category/2 - Abbigliamento") 
    print("  • /category/3 - Casa & Giardino")
    print("  • /category/4 - Sport & Tempo Libero")
    print("  • /product/1 - Dettaglio prodotto")
    print("  • /cart - Carrello funzionante")
    print("  • /admin - Dashboard amministrativo")
    
    print("\n✨ Funzionalità ShopLib Simple:")
    print("  • 🎨 Multi-Framework CSS (Bootstrap/Tailwind/Bulma)")
    print("  • 📱 Design Responsive")
    print("  • 🛒 Gestione Carrello Completa")
    print("  • 📊 Dashboard Admin")
    print("  • 🔍 Filtri Prodotti Dinamici")
    print("  • 💾 Dati in Memoria (niente errori DB)")
    print("  • 🧩 Componenti Riutilizzabili")
    print("  • 🚀 Prestazioni Ottimizzate")
    
    try:
        app.run(debug=True, port=5004, host='127.0.0.1')
    except KeyboardInterrupt:
        print("\n👋 ShopLib Simple fermato dall'utente")
    except Exception as e:
        print(f"\n❌ Errore server: {e}")
