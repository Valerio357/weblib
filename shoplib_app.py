#!/usr/bin/env python3
"""
🛍️ ShopLib - E-commerce App con WebLib v2.0
Esempio completo di shopping app con:
- Catalogo prodotti
- Carrello
- Checkout
- Admin panel
- Multi-framework CSS
- Multi-database
"""

import os
import json
from datetime import datetime, timedelta
from weblib import *

print("🛍️ Inizializzazione ShopLib - E-commerce App")
print("=" * 50)

# Configurazione
set_css_framework('bootstrap')  # Cambia in 'tailwind' o 'bulma' per diversi stili
db = get_db('sqlite:///shoplib.db')

# Inizializza app
app = WebApp(__name__)

# === MODELLI DATABASE ===
class Category(Model):
    """Categoria prodotti"""
    name = CharField(max_length=100)
    description = TextField()
    image_url = CharField(max_length=255, default="")
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)

class Product(Model):
    """Prodotto"""
    name = CharField(max_length=200)
    description = TextField()
    price = FloatField()
    original_price = FloatField()  # Per sconti
    image_url = CharField(max_length=255, default="")
    category_id = IntegerField()
    stock_quantity = IntegerField(default=0)
    is_active = BooleanField(default=True)
    is_featured = BooleanField(default=False)
    rating = FloatField(default=0.0)
    reviews_count = IntegerField(default=0)
    tags = JSONField(default=[])
    created_at = DateTimeField(auto_now_add=True)

class Customer(Model):
    """Cliente"""
    email = CharField(max_length=255, unique=True)
    first_name = CharField(max_length=100)
    last_name = CharField(max_length=100)
    phone = CharField(max_length=20, default="")
    address = TextField(default="")
    city = CharField(max_length=100, default="")
    postal_code = CharField(max_length=10, default="")
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)

class Order(Model):
    """Ordine"""
    customer_id = IntegerField()
    total_amount = FloatField()
    status = CharField(max_length=20, default="pending")  # pending, confirmed, shipped, delivered, cancelled
    payment_method = CharField(max_length=20, default="card")
    shipping_address = TextField()
    order_items = JSONField(default=[])
    notes = TextField(default="")
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

# Registra modelli
db.register_model(Category)
db.register_model(Product)
db.register_model(Customer)
db.register_model(Order)

# === DATI DEMO ===
def populate_demo_data():
    """Popola database con dati demo"""
    
    # Controlla se dati esistono già
    try:
        if Category.objects(db).count() > 0:
            return
    except Exception as e:
        print(f"⚠️  Errore controllo dati esistenti: {e}")
        print("📦 Procedendo con il popolamento...")
    
    print("📦 Popolamento dati demo...")
    
    # Categorie
    categories = [
        {"name": "Elettronica", "description": "Smartphone, laptop, accessori tech", "image_url": "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=300"},
        {"name": "Abbigliamento", "description": "Moda uomo, donna e bambini", "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300"},
        {"name": "Casa & Giardino", "description": "Arredamento, decorazioni, giardinaggio", "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300"},
        {"name": "Sport & Tempo Libero", "description": "Attrezzature sportive, hobby", "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300"}
    ]
    
    for cat_data in categories:
        try:
            category = Category(**cat_data)
            category.save(db)
        except Exception as e:
            print(f"⚠️  Errore salvataggio categoria {cat_data.get('name', 'Unknown')}: {e}")
    
    # Prodotti
    products = [
        # Elettronica
        {"name": "iPhone 15 Pro", "description": "Ultimo iPhone con chip A17 Pro", "price": 1199.99, "original_price": 1299.99, "category_id": 1, "stock_quantity": 50, "is_featured": True, "rating": 4.8, "reviews_count": 245, "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=300", "tags": ["smartphone", "apple", "new"]},
        {"name": "MacBook Air M3", "description": "Laptop ultra-sottile con chip M3", "price": 1499.99, "original_price": 1599.99, "category_id": 1, "stock_quantity": 30, "is_featured": True, "rating": 4.9, "reviews_count": 189, "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=300", "tags": ["laptop", "apple", "ultrabook"]},
        {"name": "AirPods Pro", "description": "Cuffie wireless con cancellazione rumore", "price": 249.99, "original_price": 279.99, "category_id": 1, "stock_quantity": 100, "rating": 4.7, "reviews_count": 567, "image_url": "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=300", "tags": ["audio", "wireless", "apple"]},
        
        # Abbigliamento  
        {"name": "Giacca Denim Classica", "description": "Giacca jeans unisex in cotone premium", "price": 79.99, "original_price": 99.99, "category_id": 2, "stock_quantity": 75, "rating": 4.5, "reviews_count": 123, "image_url": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=300", "tags": ["jeans", "unisex", "casual"]},
        {"name": "Sneakers Sportive", "description": "Scarpe running professionali", "price": 129.99, "original_price": 149.99, "category_id": 2, "stock_quantity": 60, "is_featured": True, "rating": 4.6, "reviews_count": 298, "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300", "tags": ["scarpe", "sport", "running"]},
        
        # Casa & Giardino
        {"name": "Pianta Monstera", "description": "Pianta d'appartamento tropicale", "price": 34.99, "original_price": 39.99, "category_id": 3, "stock_quantity": 25, "rating": 4.4, "reviews_count": 89, "image_url": "https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=300", "tags": ["piante", "decorazione", "verde"]},
        {"name": "Lampada Designer", "description": "Lampada da tavolo moderna LED", "price": 89.99, "original_price": 109.99, "category_id": 3, "stock_quantity": 40, "rating": 4.3, "reviews_count": 156, "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300", "tags": ["illuminazione", "design", "led"]},
        
        # Sport
        {"name": "Tappetino Yoga", "description": "Tappetino antiscivolo per yoga e fitness", "price": 29.99, "original_price": 34.99, "category_id": 4, "stock_quantity": 80, "rating": 4.5, "reviews_count": 234, "image_url": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=300", "tags": ["yoga", "fitness", "sport"]},
    ]
    
    for prod_data in products:
        try:
            product = Product(**prod_data)
            product.save(db)
        except Exception as e:
            print(f"⚠️  Errore salvataggio prodotto {prod_data.get('name', 'Unknown')}: {e}")
    
    print("✅ Dati demo caricati!")

# Inizializza dati con gestione errori
try:
    populate_demo_data()
except Exception as e:
    print(f"❌ Errore inizializzazione dati demo: {e}")
    print("🔄 L'app continuerà senza dati demo")

# === UTILITÀ ===
class Cart:
    """Gestione carrello (in session)"""
    
    def __init__(self, session_data=None):
        self.items = session_data.get('cart', []) if session_data else []
    
    def add_item(self, product_id, quantity=1):
        """Aggiungi prodotto al carrello"""
        for item in self.items:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                return
        
        # Nuovo prodotto
        product = Product.objects(db).get(id=product_id)
        self.items.append({
            'product_id': product_id,
            'name': product.name,
            'price': product.price,
            'quantity': quantity,
            'image_url': product.image_url
        })
    
    def remove_item(self, product_id):
        """Rimuovi prodotto dal carrello"""
        self.items = [item for item in self.items if item['product_id'] != product_id]
    
    def get_total(self):
        """Calcola totale carrello"""
        return sum(item['price'] * item['quantity'] for item in self.items)
    
    def get_count(self):
        """Conta prodotti in carrello"""
        return sum(item['quantity'] for item in self.items)
    
    def clear(self):
        """Svuota carrello"""
        self.items = []

# === COMPONENTI CUSTOM ===
def ProductCard(product, show_actions=True):
    """Card prodotto riutilizzabile"""
    
    # Badge sconto
    discount_badge = ""
    if product.original_price > product.price:
        discount = int(((product.original_price - product.price) / product.original_price) * 100)
        discount_badge = Badge(text=f"-{discount}%", variant="danger").render()
    
    # Stelle rating
    stars = "⭐" * int(product.rating)
    
    # Prezzo
    price_html = f"€{product.price:.2f}"
    if product.original_price > product.price:
        price_html += f" <small class='text-muted'><del>€{product.original_price:.2f}</del></small>"
    
    # Azioni
    actions = ""
    if show_actions:
        actions = Div([
            Button("🛒 Aggiungi", 
                  classes=[CSS.BTN_PRIMARY, "btn-sm", "add-to-cart"],
                  data_product_id=str(product.id),
                  data_product_name=product.name),
            A("👁️ Dettagli", href=f"/product/{product.id}", classes=[CSS.BTN_SECONDARY, "btn-sm", CSS.ME_2])
        ], classes=["mt-2"]).render()
    
    return Card(
        content=[
            Div([
                Img(src=product.image_url or "https://via.placeholder.com/300x200", 
                   alt=product.name,
                   classes=["card-img-top"],
                   style="height: 200px; object-fit: cover;"),
                discount_badge
            ], classes=["position-relative"]),
            
            Div([
                H5(product.name, classes=["card-title"]),
                P(product.description[:100] + ("..." if len(product.description) > 100 else ""), 
                  classes=["card-text", "text-muted"]),
                Div([
                    Span(stars + f" ({product.reviews_count})", classes=["small", "text-muted"]),
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
    
    try:
        # Prodotti in evidenza
        featured_products = Product.objects(db).filter(is_featured=True).all()
        featured_products = featured_products[:6]  # Limita manualmente
        
        # Categorie
        categories = Category.objects(db).filter(is_active=True).all()
    except Exception as e:
        print(f"❌ Errore database homepage: {e}")
        featured_products = []
        categories = []
    
    page = app.create_page("ShopLib - Il tuo negozio online")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    page.add_js("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
    
    content = [
        ShoppingNavbar().render(),
        
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
                            Img(src=cat.image_url or "https://via.placeholder.com/300x200",
                               alt=cat.name,
                               classes=["card-img-top"],
                               style="height: 200px; object-fit: cover;"),
                            Div([
                                H5(cat.name, classes=["card-title"]),
                                P(cat.description, classes=["card-text"]),
                                A("Esplora", href=f"/category/{cat.id}", 
                                  classes=[CSS.BTN_PRIMARY])
                            ], classes=[CSS.CARD_BODY])
                        ]
                    ).render()
                ], classes=[CSS.get_col_size(6, 'md'), "mb-4"])
                for cat in categories
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
    """Pagina categoria con filtri"""
    
    try:
        category = Category.objects(db).get(id=category_id)
        products = Product.objects(db).filter(category_id=category_id, is_active=True).all()
    except Exception as e:
        print(f"❌ Errore database categoria {category_id}: {e}")
        # Dati fallback
        category = type('Category', (), {'name': 'Categoria', 'description': 'Categoria non trovata'})()
        products = []
    
    page = app.create_page(f"{category.name} - ShopLib")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    page.add_js("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
    
    content = [
        ShoppingNavbar().render(),
        
        Div([
            # Breadcrumb
            Nav([
                Ol([
                    Li(A("Home", href="/"), classes=["breadcrumb-item"]),
                    Li(category.name, classes=["breadcrumb-item", "active"])
                ], classes=["breadcrumb"])
            ]),
            
            # Header categoria
            Div([
                H1(f"📂 {category.name}"),
                P(category.description, classes=["lead", CSS.get_color_class('muted', 'text')])
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
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'original_price': p.original_price,
        'rating': p.rating,
        'reviews_count': p.reviews_count,
        'image_url': p.image_url or "",
        'description': p.description,
        'has_discount': p.original_price > p.price,
        'is_popular': p.reviews_count > 200,
        'is_new': True  # Simplified
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
    
    try:
        product = Product.objects(db).get(id=product_id)
        category = Category.objects(db).get(id=product.category_id)
        
        # Prodotti correlati
        related_products = Product.objects(db).filter(
            category_id=product.category_id,
            is_active=True
        ).all()
        related_products = [p for p in related_products if p.id != product.id][:3]
    except Exception as e:
        print(f"❌ Errore database prodotto {product_id}: {e}")
        # Dati fallback
        product = type('Product', (), {
            'name': 'Prodotto non trovato',
            'description': 'Prodotto non disponibile',
            'price': 0.0,
            'original_price': 0.0,
            'image_url': '',
            'stock_quantity': 0,
            'rating': 0.0,
            'reviews_count': 0,
            'tags': []
        })()
        category = type('Category', (), {'name': 'Categoria', 'id': 1})()
        related_products = []
    
    page = app.create_page(f"{product.name} - ShopLib")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    page.add_js("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
    
    # Calcoli
    stars = "⭐" * int(product.rating)
    discount_percent = 0
    if product.original_price > product.price:
        discount_percent = int(((product.original_price - product.price) / product.original_price) * 100)
    
    content = [
        ShoppingNavbar().render(),
        
        Div([
            # Breadcrumb
            Nav([
                Ol([
                    Li(A("Home", href="/"), classes=["breadcrumb-item"]),
                    Li(A(category.name, href=f"/category/{category.id}"), classes=["breadcrumb-item"]),
                    Li(product.name, classes=["breadcrumb-item", "active"])
                ], classes=["breadcrumb"])
            ]),
            
            # Prodotto principale
            Div([
                Div([
                    # Immagine
                    Img(src=product.image_url or "https://via.placeholder.com/500x400",
                       alt=product.name,
                       classes=["img-fluid", "rounded"],
                       style="max-height: 400px; object-fit: cover;")
                ], classes=[CSS.get_col_size(6, 'md')]),
                
                Div([
                    # Info prodotto
                    H1(product.name),
                    Div([
                        Span(stars + f" ({product.reviews_count} recensioni)", 
                             classes=["text-muted"]),
                        Badge(text=f"Stock: {product.stock_quantity}", 
                             variant="success" if product.stock_quantity > 10 else "warning").render()
                    ], classes=["mb-3"]),
                    
                    # Prezzo
                    Div([
                        H2(f"€{product.price:.2f}", classes=["text-primary", "d-inline"]),
                        (" " + Span(f"€{product.original_price:.2f}", 
                                   classes=["text-muted", "text-decoration-line-through", "ms-2"]) + 
                         " " + Badge(text=f"-{discount_percent}%", variant="danger").render()
                        ) if discount_percent > 0 else ""
                    ], classes=["mb-4"]),
                    
                    # Descrizione
                    P(product.description, classes=["lead", "mb-4"]),
                    
                    # Tags
                    Div([
                        Badge(text=tag, variant="secondary").render() + " "
                        for tag in product.tags
                    ], classes=["mb-4"]) if product.tags else "",
                    
                    # Azioni
                    Div([
                        Div([
                            Label("Quantità:", classes=["form-label"]),
                            Input(type="number", value="1", min="1", max=str(product.stock_quantity),
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
            body: JSON.stringify({{product_id: {product.id}, quantity: quantity}})
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
    
    # Simula sessione (in produzione usare vere sessioni)
    cart = Cart()  # Carrello vuoto per demo
    
    page = app.create_page("Carrello - ShopLib")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    page.add_js("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js")
    
    content = [
        ShoppingNavbar(cart.get_count()).render(),
        
        Div([
            H1("🛒 Il tuo Carrello"),
            
            # Carrello vuoto per demo
            Alert(
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
        # Simula aggiunta (in produzione usare sessioni reali)
        data = {"success": True, "message": "Prodotto aggiunto al carrello!"}
        
        import json
        return Response(
            content=json.dumps(data),
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
    
    try:
        # Statistiche
        total_products = Product.objects(db).count()
        total_categories = Category.objects(db).count()
        total_orders = Order.objects(db).count()
        
        # Prodotti recenti
        recent_products = Product.objects(db).all()[:5]  # Limita manualmente
    except Exception as e:
        print(f"❌ Errore database admin: {e}")
        total_products = 0
        total_categories = 0
        total_orders = 0
        recent_products = []
    
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
                                H2(str(total_orders), classes=["card-title", "text-warning"]),
                                P("🛒 Ordini", classes=["card-text"])
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
                                P("💰 Revenue", classes=["card-text"])
                            ], classes=[CSS.CARD_BODY, CSS.TEXT_CENTER])
                        ],
                        classes=[CSS.get_color_class('light', 'bg')]
                    ).render()
                ], classes=[CSS.get_col_size(3)])
            ], classes=[CSS.ROW, "mb-4"]),
            
            # Grafici (demo con Chart.js)
            Div([
                Div([
                    Card(
                        header="📈 Vendite Ultimi 7 Giorni",
                        content=[
                            Div("<canvas id='salesChart'></canvas>", style="height: 300px;")
                        ]
                    ).render()
                ], classes=[CSS.get_col_size(8)]),
                
                Div([
                    Card(
                        header="🏆 Top Prodotti",
                        content=[
                            Ul([
                                Li(f"{p.name} - €{p.price:.2f}")
                                for p in recent_products[:5]
                            ])
                        ]
                    ).render()
                ], classes=[CSS.get_col_size(4)])
            ], classes=[CSS.ROW, "mb-4"]),
            
            # Azioni rapide
            H3("⚡ Azioni Rapide"),
            Div([
                A("➕ Nuovo Prodotto", href="/admin/products/new", classes=[CSS.BTN_PRIMARY, CSS.ME_2]),
                A("📂 Nuova Categoria", href="/admin/categories/new", classes=[CSS.BTN_SUCCESS, CSS.ME_2]),
                A("📊 Report Vendite", href="/admin/reports", classes=[CSS.BTN_INFO, CSS.ME_2]),
                A("⚙️ Impostazioni", href="/admin/settings", classes=[CSS.BTN_SECONDARY])
            ], classes=["mb-4"])
            
        ], classes=[CSS.CONTAINER])
    ]
    
    # Chart.js per grafici
    js_code = """
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
    // Demo chart
    const ctx = document.getElementById('salesChart').getContext('2d');
    const salesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'],
            datasets: [{
                label: 'Vendite €',
                data: [1200, 1900, 800, 1500, 2000, 2200, 1800],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    </script>
    """
    
    page.add_to_body(Div(content))
    page.add_to_body(js_code)
    return page.build().render()


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🛍️ ShopLib E-commerce App Avviata!")
    print("=" * 50)
    print("🌐 Server: http://127.0.0.1:5003")
    print("🎨 Framework CSS: Bootstrap (modifica set_css_framework)")
    print("💾 Database: SQLite con dati demo")
    
    print("\n📋 Pagine disponibili:")
    print("  • / - Homepage con prodotti in evidenza")
    print("  • /category/1 - Elettronica")
    print("  • /category/2 - Abbigliamento") 
    print("  • /category/3 - Casa & Giardino")
    print("  • /category/4 - Sport & Tempo Libero")
    print("  • /product/1 - Dettaglio prodotto")
    print("  • /cart - Carrello (demo)")
    print("  • /admin - Dashboard amministrativo")
    
    print("\n✨ Funzionalità ShopLib:")
    print("  • 🎨 Multi-Framework CSS (Bootstrap/Tailwind/Bulma)")
    print("  • 📱 Design Responsive")
    print("  • 🛒 Gestione Carrello JavaScript")
    print("  • 📊 Dashboard Admin con Chart.js")
    print("  • 🔍 Filtri Prodotti Dinamici")
    print("  • 💾 Database SQLite con ORM")
    print("  • 🧩 Componenti Riutilizzabili")
    print("  • 📦 Dati Demo Auto-generati")
    
    try:
        app.run(debug=True, port=5003, host='127.0.0.1')
    except KeyboardInterrupt:
        print("\n👋 ShopLib fermato dall'utente")
        db.close()
    except Exception as e:
        print(f"\n❌ Errore server: {e}")
        db.close()
