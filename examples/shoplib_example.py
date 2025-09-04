#!/usr/bin/env python3
"""
🛍️ ShopLib - E-commerce App con WebLib v2.0
Versione corretta senza errori di database e type conversion
"""

from weblib import *
import json

print("🛍️ Inizializzazione ShopLib - E-commerce App")
print("=" * 50)

# Configurazione
set_css_framework('bootstrap')

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
def safe_float(value, default=0.0):
    """Converte in modo sicuro a float"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def safe_int(value, default=0):
    """Converte in modo sicuro a int"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def get_product_by_id(product_id):
    """Trova prodotto per ID"""
    for product in PRODUCTS:
        if product['id'] == int(product_id):
            return product
    return None

def get_category_by_id(category_id):
    """Trova categoria per ID"""
    for category in CATEGORIES:
        if category['id'] == int(category_id):
            return category
    return None

def get_products_by_category(category_id):
    """Trova prodotti per categoria"""
    return [p for p in PRODUCTS if p['category_id'] == int(category_id)]

def get_featured_products():
    """Prodotti in evidenza"""
    return [p for p in PRODUCTS if p.get('is_featured', False)]

# === COMPONENTI CUSTOM ===
def ProductCard(product, show_actions=True):
    """Card prodotto riutilizzabile - VERSIONE SICURA"""
    
    # Conversioni sicure
    price = safe_float(product.get('price', 0))
    original_price = safe_float(product.get('original_price', 0))
    rating = safe_float(product.get('rating', 0))
    reviews_count = safe_int(product.get('reviews_count', 0))
    
    # Badge sconto (controllo sicuro)
    discount_badge = ""
    if original_price > price and price > 0:
        discount = int(((original_price - price) / original_price) * 100)
        discount_badge = Badge(text=f"-{discount}%", variant="danger").render()
    
    # Stelle rating
    stars = "⭐" * int(rating)
    
    # Prezzo (formattazione sicura)
    price_html = f"€{price:.2f}"
    if original_price > price:
        price_html += f" <small class='text-muted'><del>€{original_price:.2f}</del></small>"
    
    # Azioni
    actions = ""
    if show_actions:
        actions = Div([
            Button("🛒 Aggiungi", 
                  classes=["btn", "btn-primary", "btn-sm", "add-to-cart"],
                  data_product_id=str(product.get('id', 0)),
                  data_product_name=str(product.get('name', ''))),
            A("👁️ Dettagli", href=f"/product/{product.get('id', 0)}", 
              classes=["btn", "btn-secondary", "btn-sm", "me-2"])
        ], classes=["mt-2"]).render()
    
    return Card(
        content=[
            Div([
                Img(src=product.get('image_url', "https://via.placeholder.com/300x200"), 
                   alt=product.get('name', ''),
                   classes=["card-img-top"],
                   style="height: 200px; object-fit: cover;"),
                discount_badge
            ], classes=["position-relative"]),
            
            Div([
                H5(product.get('name', 'Prodotto'), classes=["card-title"]),
                P(product.get('description', '')[:100] + ("..." if len(product.get('description', '')) > 100 else ""), 
                  classes=["card-text", "text-muted"]),
                Div([
                    Span(stars + f" ({reviews_count})", classes=["small", "text-muted"]),
                    "<br>",
                    H4(price_html, classes=["text-primary", "mb-2"])
                ]),
                actions
            ], classes=["card-body"])
        ],
        classes=["mb-4", "product-card"]
    )

def ShoppingNavbar(cart_count=0):
    """Navbar personalizzata per shop"""
    return NavBar(
        brand="🛍️ ShopLib",
        theme="light",
        classes=["bg-light", "mb-4"],
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
                  classes=["btn", "btn-success", "me-2"]),
                A("👤 Login", href="/login", classes=["btn", "btn-secondary"])
            ], classes=["d-flex"])
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
                H1("🛍️ Benvenuto in ShopLib", classes=["text-center"]),
                P("Il tuo negozio online con i migliori prodotti ai prezzi più convenienti", 
                  classes=["text-center", "lead"]),
                Div([
                    A("Scopri i Prodotti", href="#featured", classes=["btn", "btn-primary", "btn-lg", "me-2"]),
                    A("Vedi Categorie", href="#categories", classes=["btn", "btn-light"])
                ], classes=["text-center"])
            ], classes=["container"])
        ], classes=["bg-primary", "text-white", "py-5", "mb-5"]),
        
        # Prodotti in evidenza
        Div([
            H2("⭐ Prodotti in Evidenza", classes=["text-center", "mb-3"], id="featured"),
            
            Div([
                Div([
                    ProductCard(product).render()
                ], classes=["col-md-4"]) 
                for product in featured_products
            ], classes=["row"]) if featured_products else Alert(
                message="Nessun prodotto in evidenza al momento", 
                type="info"
            ).render()
            
        ], classes=["container", "mb-5"]),
        
        # Categorie
        Div([
            H2("📂 Categorie", classes=["text-center", "mb-3"], id="categories"),
            
            Div([
                Div([
                    Card(
                        content=[
                            Img(src=cat.get('image_url', "https://via.placeholder.com/300x200"),
                               alt=cat.get('name', ''),
                               classes=["card-img-top"],
                               style="height: 200px; object-fit: cover;"),
                            Div([
                                H5(cat.get('name', ''), classes=["card-title"]),
                                P(cat.get('description', ''), classes=["card-text"]),
                                A("Esplora", href=f"/category/{cat.get('id', 0)}", 
                                  classes=["btn", "btn-primary"])
                            ], classes=["card-body"])
                        ]
                    ).render()
                ], classes=["col-md-6", "mb-4"])
                for cat in CATEGORIES
            ], classes=["row"])
            
        ], classes=["container", "mb-5"])
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
                        location.reload(); // Refresh per aggiornare contatore
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
    """Pagina categoria con prodotti"""
    
    category = get_category_by_id(category_id)
    products = get_products_by_category(category_id)
    
    if not category:
        category = {"name": "Categoria non trovata", "description": "Categoria non disponibile"}
    
    page = app.create_page(f"{category['name']} - ShopLib")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    
    content = [
        ShoppingNavbar(len(CART_ITEMS)).render(),
        
        Div([
            H1(f"📂 {category['name']}"),
            P(category.get('description', ''), classes=["lead", "text-muted"]),
            
            H3(f"🛍️ Prodotti ({len(products)})"),
            Div([
                Div([
                    ProductCard(product).render()
                ], classes=["col-md-4", "mb-4"])
                for product in products
            ], classes=["row"]) if products else Alert(
                message="Nessun prodotto trovato in questa categoria", 
                type="info"
            ).render()
            
        ], classes=["container"])
    ]
    
    page.add_to_body(Div(content))
    return page.build().render()

@app.get('/product/<int:product_id>')
def product_detail(request, product_id):
    """Dettaglio prodotto"""
    
    product = get_product_by_id(product_id)
    
    if not product:
        return "<h1>Prodotto non trovato</h1>"
    
    category = get_category_by_id(product.get('category_id', 1))
    
    page = app.create_page(f"{product['name']} - ShopLib")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    
    # Calcoli sicuri
    price = safe_float(product.get('price', 0))
    original_price = safe_float(product.get('original_price', 0))
    rating = safe_float(product.get('rating', 0))
    stars = "⭐" * int(rating)
    discount_percent = 0
    if original_price > price and price > 0:
        discount_percent = int(((original_price - price) / original_price) * 100)
    
    content = [
        ShoppingNavbar(len(CART_ITEMS)).render(),
        
        Div([
            Div([
                Div([
                    # Immagine
                    Img(src=product.get('image_url', "https://via.placeholder.com/500x400"),
                       alt=product.get('name', ''),
                       classes=["img-fluid", "rounded"],
                       style="max-height: 400px; object-fit: cover;")
                ], classes=["col-md-6"]),
                
                Div([
                    # Info prodotto
                    H1(product.get('name', 'Prodotto')),
                    P(stars + f" ({product.get('reviews_count', 0)} recensioni)", 
                      classes=["text-muted"]),
                    
                    # Prezzo
                    Div([
                        H2(f"€{price:.2f}", classes=["text-primary", "d-inline"]),
                        (f" <del class='text-muted'>€{original_price:.2f}</del> <span class='badge bg-danger'>-{discount_percent}%</span>"
                        ) if discount_percent > 0 else ""
                    ], classes=["mb-4"]),
                    
                    # Descrizione
                    P(product.get('description', ''), classes=["lead", "mb-4"]),
                    
                    # Azioni
                    Button("🛒 Aggiungi al Carrello", 
                          classes=["btn", "btn-primary", "btn-lg"],
                          onclick=f"alert('Prodotto {product.get('name', '')} aggiunto!')")
                    
                ], classes=["col-md-6"])
            ], classes=["row"])
            
        ], classes=["container"])
    ]
    
    page.add_to_body(Div(content))
    return page.build().render()

@app.get('/cart')
def cart_page(request):
    """Pagina carrello"""
    
    page = app.create_page("Carrello - ShopLib")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    
    content = [
        ShoppingNavbar(len(CART_ITEMS)).render(),
        
        Div([
            H1("🛒 Il tuo Carrello"),
            
            # Carrello vuoto per demo
            Alert(
                message="Il tuo carrello è vuoto. Inizia a fare shopping!",
                type="info"
            ).render(),
            
            Div([
                A("🛍️ Continua Shopping", href="/", classes=["btn", "btn-primary", "me-2"]),
                A("📱 Elettronica", href="/category/1", classes=["btn", "btn-secondary"])
            ])
            
        ], classes=["container"])
    ]
    
    page.add_to_body(Div(content))
    return page.build().render()

# === API ENDPOINTS ===
@app.post('/api/cart/add')
def api_add_to_cart(request):
    """API per aggiungere prodotti al carrello"""
    try:
        # Simula aggiunta (in produzione usare sessioni reali)
        data = {"success": True, "message": "Prodotto aggiunto al carrello!"}
        
        return Response(
            content=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        return Response(
            content=json.dumps({"success": False, "message": str(e)}),
            headers={'Content-Type': 'application/json'},
            status_code=400
        )

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🛍️ ShopLib E-commerce App Avviata!")
    print("=" * 50)
    print("🌐 Server: http://127.0.0.1:5002")
    print("🎨 Framework CSS: Bootstrap")
    print("💾 Dati: In memoria (no database)")
    
    print("\n📋 Pagine disponibili:")
    print("  • / - Homepage con prodotti in evidenza")
    print("  • /category/1 - Elettronica")
    print("  • /category/2 - Abbigliamento") 
    print("  • /category/3 - Casa & Giardino")
    print("  • /category/4 - Sport & Tempo Libero")
    print("  • /product/1 - Dettaglio prodotto")
    print("  • /cart - Carrello")
    
    print("\n✨ Correzioni apportate:")
    print("  • 🔧 Conversioni sicure con safe_float() e safe_int()")
    print("  • 🛡️ Controlli su valori null/undefined")
    print("  • 📱 Uso corretto delle classi CSS Bootstrap")
    print("  • 💾 Dati completamente in memoria")
    print("  • 🚫 Rimosso database SQLite problematico")
    
    try:
        app.run(debug=True, port=5002, host='127.0.0.1')
    except KeyboardInterrupt:
        print("\n👋 ShopLib fermato dall'utente")
    except Exception as e:
        print(f"\n❌ Errore server: {e}")
        import traceback
        traceback.print_exc()
