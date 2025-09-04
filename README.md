# 🚀 WebLib v2.0 - Documentazione Completa

## 📋 Panoramica

WebLib v2.0 è un framework web Python completo con supporto **multi-framework CSS** e **multi-database**. Permette di sviluppare applicazioni web moderne che possono adattarsi dinamicamente a diversi framework CSS (Bootstrap, Tailwind, Bulma) e database (SQLite, PostgreSQL, MySQL, MongoDB).

## ⭐ Caratteristiche Principali

### 🎨 Multi-Framework CSS
- **Bootstrap 5.1.3** - Framework CSS più popolare
- **Tailwind CSS 3.0** - CSS utility-first moderno  
- **Bulma 0.9.4** - CSS framework modulare
- **Switching dinamico** - Cambia framework a runtime
- **Classi unificate** - API consistente tra framework

### 💾 Multi-Database
- **SQLite** - Database embedded (default, zero config)
- **PostgreSQL** - Database enterprise avanzato
- **MySQL** - Database relazionale popolare
- **MongoDB** - Database NoSQL flessibile
- **ORM unificato** - Stessa API per tutti i database

### 🧩 Componenti Avanzati
- **Forms** - Validazione automatica e rendering
- **Components** - Card, Alert, Badge, NavBar, ecc.
- **Authentication** - Sistema autenticazione completo
- **Charts** - Grafici interattivi integrati
- **API** - REST API pronto per l'uso

## 🚀 Quick Start

### Installazione Base
```bash
# Clone repository
git clone <repo-url>
cd webapp

# Installa dipendenze base (SQLite incluso)
pip install -r requirements.txt  # Se disponibile
```

### Dipendenze Opzionali per Database
```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL  
pip install PyMySQL

# MongoDB
pip install pymongo
```

### Primo Esempio
```python
from weblib import *
from weblib.css_frameworks import set_css_framework, CSS

# Scegli framework CSS
set_css_framework('bootstrap')  # o 'tailwind', 'bulma'

# Inizializza app
app = WebApp(__name__)
db = get_db('sqlite:///myapp.db')

@app.get('/')
def home(request):
    page = app.create_page("La mia app")
    
    content = [
        Card(
            title="Benvenuto in WebLib v2.0!",
            text="Framework multi-CSS e multi-database",
            classes=[CSS.get_color_class('primary', 'border')]
        ).render()
    ]
    
    page.add_to_body(Div(content, classes=[CSS.CONTAINER]))
    return page.build().render()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

## 🎨 Framework CSS

### Configurazione Framework
```python
from weblib.css_frameworks import set_css_framework, get_css_framework, FrameworkManager

# Imposta framework globale
set_css_framework('bootstrap')  # Default
set_css_framework('tailwind')   # Tailwind CSS
set_css_framework('bulma')      # Bulma

# Ottieni framework attivo
framework = get_css_framework()
print(f"Framework: {framework.name} v{framework.version}")

# Lista framework supportati
frameworks = FrameworkManager.list_frameworks()
print(frameworks)  # ['bootstrap', 'tailwind', 'bulma']
```

### Utilizzo Classi CSS Unificate
```python
from weblib.css_frameworks import CSS

# Classi funzionano con tutti i framework
button_primary = CSS.BTN_PRIMARY    # Bottone principale
container = CSS.CONTAINER           # Container responsive
text_center = CSS.TEXT_CENTER       # Testo centrato
card = CSS.CARD                     # Card component

# Classi colori dinamiche
bg_primary = CSS.get_color_class('primary', 'bg')    # Sfondo primario
text_danger = CSS.get_color_class('danger', 'text')  # Testo rosso
border_success = CSS.get_color_class('success', 'border')  # Bordo verde

# Classi grid responsive
col_6 = CSS.get_col_size(6)         # Colonna metà larghezza
col_md_4 = CSS.get_col_size(4, 'md') # Colonna 1/3 su medium+
```

### Esempio Multi-Framework
```python
# Stessa pagina, diversi framework
for framework in ['bootstrap', 'tailwind', 'bulma']:
    set_css_framework(framework)
    
    page = app.create_page(f"Demo {framework.title()}")
    
    content = Card(
        title=f"Card {framework.title()}",
        text="Stessa API, diverso styling!",
        classes=[CSS.get_color_class('info', 'border')]
    ).render()
    
    page.add_to_body(content)
    # Ogni framework avrà styling diverso ma API identica!
```

## 💾 Multi-Database

### Configurazione Database
```python
from weblib import get_db
from weblib.multi_database import DatabaseManager

# SQLite (default - zero config)
db = get_db('sqlite:///myapp.db')

# PostgreSQL  
db = get_db('postgresql://user:password@localhost:5432/mydb', 'postgresql')

# MySQL
db = get_db('mysql://user:password@localhost:3306/mydb', 'mysql')

# MongoDB
db = get_db('mongodb://localhost:27017/mydb', 'mongodb')

# Lista database supportati
supported_dbs = DatabaseManager.list_supported_databases()
print(supported_dbs)  # ['sqlite', 'postgresql', 'mysql', 'mongodb']
```

### Modelli Unificati
```python
# Stesso modello funziona con tutti i database
class User(Model):
    username = CharField(max_length=100, unique=True)
    email = CharField(max_length=255)
    password_hash = CharField(max_length=255)
    is_admin = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    profile_data = JSONField()  # JSON nativamente supportato

class Post(Model):
    title = CharField(max_length=200)
    content = TextField()
    author_id = IntegerField()
    created_at = DateTimeField(auto_now_add=True)
    tags = JSONField()

# Registra modelli
db.register_model(User)
db.register_model(Post)
```

### Query Unificate
```python
# Stesso codice query per tutti i database
users = User.objects(db).all()
admin_users = User.objects(db).filter(is_admin=True).all()
new_user = User.objects(db).filter(created_at__gte='2025-01-01').first()

# Operazioni CRUD
user = User(username='mario', email='mario@email.com')
user.save(db)

user = User.objects(db).get(id=1)
user.username = 'mario_updated'
user.save(db)

User.objects(db).filter(id=1).delete()

# Query complesse
posts = Post.objects(db).filter(
    title__contains='Python'
).order_by('-created_at').limit(10).all()

# Aggregazioni (supporto varia per database)
total_posts = Post.objects(db).count()
```

## 🧩 Componenti

### Card Component
```python
# Card semplice
card = Card(
    title="Titolo Card",
    text="Contenuto della card",
    footer="Footer opzionale"
)

# Card avanzata
card = Card(
    header="Header personalizzato",
    title="Titolo con Badge",
    content=[
        P("Paragrafo di contenuto"),
        Badge(text="Nuovo", variant="success").render(),
        Ul([Li("Item 1"), Li("Item 2")])
    ],
    footer=Div([
        Button("Azione", classes=[CSS.BTN_PRIMARY]),
        A("Link", href="/link", classes=[CSS.BTN_SECONDARY])
    ]),
    classes=[CSS.get_color_class('primary', 'border')]
)
```

### Form e Validazione
```python
class UserForm(FormValidator):
    username = StringField(required=True, min_length=3, max_length=50)
    email = StringField(required=True)
    password = StringField(required=True, min_length=6)
    age = NumberField(min_value=18, max_value=120)
    
    def clean(self):
        # Validazione personalizzata
        if self.data['username'].lower() in ['admin', 'root']:
            raise ValidationError("Username non permesso")

# Uso nel route
@app.post('/user')
def create_user(request):
    form = UserForm()
    
    if form.validate(request.form_data):
        # Dati validi, crea utente
        user = User(**form.cleaned_data)
        user.save(db)
        return "✅ Utente creato!"
    else:
        # Errori validazione
        return f"❌ Errori: {form.errors}"
```

### NavBar
```python
navbar = NavBar(
    brand="🚀 La Mia App",
    theme="dark",  # o "light"
    classes=[CSS.get_color_class('primary', 'bg')],
    links=[
        {"text": "Home", "url": "/"},
        {"text": "About", "url": "/about"},
        {"text": "Contact", "url": "/contact"}
    ]
)

# Con menu utente
if request.user:
    navbar.add_child(
        Div([
            Span(f"Ciao {request.user.username}!"),
            A("Logout", href="/logout", classes=[CSS.BTN_SECONDARY])
        ], classes=[CSS.D_FLEX])
    )
```

### Alert e Badge
```python
# Alert
alert = Alert(message="Operazione completata!", type="success")
warning = Alert(message="Attenzione!", type="warning")
error = Alert(message="Errore critico", type="danger")

# Badge
badge = Badge(text="Nuovo", variant="primary")
counter = Badge(text="5", variant="secondary")
status = Badge(text="Attivo", variant="success")
```

## 🔐 Autenticazione

### Setup Sistema Auth
```python
from weblib import AuthManager, AuthMiddleware

# Manager autenticazione
auth_manager = AuthManager()

# Middleware per proteggere routes
auth_middleware = AuthMiddleware(auth_manager=auth_manager)

@app.get('/protected')
def protected_page(request):
    request = auth_middleware.process_request(request)
    
    if not request.user:
        return Response(
            content='<script>window.location.href="/login";</script>',
            status_code=302
        )
    
    return f"Benvenuto {request.user.username}!"

# Login
@app.post('/login')  
def login(request):
    username = request.form_data['username']
    password = request.form_data['password']
    
    user = User.objects(db).filter(username=username).first()
    if user and auth_manager.verify_password(password, user.password_hash):
        # Login OK
        session_token = auth_manager.create_session(user.id)
        # Imposta cookie/sessione...
        return "Login OK!"
    else:
        return "Login fallito!"
```

## 📊 Charts e API

### REST API
```python
import json

@app.get('/api/users')
def api_users(request):
    users = User.objects(db).all()
    data = [{'id': u.id, 'username': u.username, 'email': u.email} for u in users]
    
    return Response(
        content=json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )

@app.post('/api/users')
def api_create_user(request):
    try:
        user_data = json.loads(request.body)
        user = User(**user_data)
        user.save(db)
        
        return Response(
            content=json.dumps({'success': True, 'user_id': user.id}),
            headers={'Content-Type': 'application/json'}
        )
    except Exception as e:
        return Response(
            content=json.dumps({'success': False, 'error': str(e)}),
            headers={'Content-Type': 'application/json'},
            status_code=400
        )
```

## 🛠️ Configurazione Avanzata

### Variabili Ambiente
```bash
# Framework CSS
export CSS_FRAMEWORK=bootstrap  # o tailwind, bulma

# Database
export DATABASE_TYPE=postgresql  # o mysql, mongodb, sqlite
export DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Debug
export DEBUG=true
export PORT=5000
```

### Configurazione Python
```python
import os

# Configurazione da ambiente
CSS_FRAMEWORK = os.getenv('CSS_FRAMEWORK', 'bootstrap')
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
PORT = int(os.getenv('PORT', '5000'))

# Applica configurazione
set_css_framework(CSS_FRAMEWORK)

if DATABASE_TYPE == 'postgresql':
    db = get_db(os.getenv('DATABASE_URL'), 'postgresql')
elif DATABASE_TYPE == 'mysql':
    db = get_db(os.getenv('DATABASE_URL'), 'mysql')
# ... etc
```

## 🧪 Testing

### Test Runner
```bash
# Demo rapido
python test_weblib_runner.py

# Seleziona opzioni:
# 1. Demo veloce (Bootstrap + SQLite)
# 2. Test interattivo
# 3. Test completi (12 combinazioni)
```

### Test Manuale Framework
```python
# Test switching framework
frameworks = ['bootstrap', 'tailwind', 'bulma']

for fw in frameworks:
    set_css_framework(fw)
    print(f"Testing {fw}...")
    
    # Test componenti
    card = Card(title="Test", text="Content").render()
    alert = Alert(message="Test", type="info").render()
    
    # Verifica CSS classes
    assert CSS.BTN_PRIMARY is not None
    assert CSS.CARD is not None
    print(f"✅ {fw} OK")
```

### Test Database
```python
# Test multi-database
databases = [
    ('sqlite:///test.db', 'sqlite'),
    ('postgresql://test:test@localhost:5432/test', 'postgresql'),
    # ... altri DB
]

for db_url, db_type in databases:
    try:
        db = get_db(db_url, db_type)
        
        # Test modello
        test_user = User(username='test', email='test@test.com')
        test_user.save(db)
        
        # Test query
        users = User.objects(db).all()
        assert len(users) > 0
        
        print(f"✅ {db_type} OK")
        
    except Exception as e:
        print(f"❌ {db_type} Error: {e}")
```

## 🔧 Personalizzazione

### Nuovo Framework CSS
```python
from weblib.css_frameworks import CSSFramework, register_framework

class MyCustomFramework(CSSFramework):
    name = "mycustom"
    version = "1.0.0"
    cdn_css = "https://cdn.example.com/mycustom.css"
    
    # Mapping classi
    BTN_PRIMARY = "my-btn-primary"
    CARD = "my-card"
    CONTAINER = "my-container"
    # ... altre classi

# Registra framework
register_framework('mycustom', MyCustomFramework())

# Usa framework personalizzato  
set_css_framework('mycustom')
```

### Nuovo Database Adapter
```python
from weblib.multi_database import DatabaseAdapter

class MyDatabaseAdapter(DatabaseAdapter):
    db_type = "mydatabase"
    
    def connect(self, connection_string):
        # Implementa connessione
        pass
        
    def execute_query(self, query, params=None):
        # Implementa esecuzione query
        pass
    
    def create_table(self, model_class):
        # Implementa creazione tabelle
        pass

# Registra adapter
DatabaseManager.register_adapter('mydatabase', MyDatabaseAdapter)
```

## 📚 Esempi Completi

### App Blog Completa
```python
from weblib import *
from weblib.css_frameworks import set_css_framework, CSS

# Configurazione
set_css_framework('bootstrap')
app = WebApp(__name__)
db = get_db('sqlite:///blog.db')
auth_manager = AuthManager()

# Modelli
class User(Model):
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255)
    password_hash = CharField(max_length=255)

class Post(Model):
    title = CharField(max_length=200)
    content = TextField()
    author_id = IntegerField()
    created_at = DateTimeField(auto_now_add=True)

db.register_model(User)
db.register_model(Post)

# Routes
@app.get('/')
def home(request):
    posts = Post.objects(db).order_by('-created_at').limit(5).all()
    
    page = app.create_page("Il Mio Blog")
    page.add_css("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
    
    content = [
        NavBar(brand="📝 Blog", links=[
            {"text": "Home", "url": "/"},
            {"text": "Scrivi", "url": "/write"}
        ]).render(),
        
        Div([
            H1("Ultimi Post", classes=[CSS.TEXT_CENTER]),
            Div([
                Card(
                    title=post.title,
                    text=post.content[:200] + "...",
                    footer=f"📅 {post.created_at}"
                ).render()
                for post in posts
            ])
        ], classes=[CSS.CONTAINER])
    ]
    
    page.add_to_body(Div(content))
    return page.build().render()

if __name__ == "__main__":
    app.run(debug=True)
```

## 🚀 Deploy

### Produzione
```python
# config.py
import os

class Config:
    CSS_FRAMEWORK = os.getenv('CSS_FRAMEWORK', 'bootstrap')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.getenv('PORT', '5000'))

# app.py
from config import Config

set_css_framework(Config.CSS_FRAMEWORK)
db = get_db(Config.DATABASE_URL, Config.DATABASE_TYPE)

if __name__ == "__main__":
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )
```

### Docker
```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV CSS_FRAMEWORK=bootstrap
ENV DATABASE_TYPE=postgresql
ENV PORT=5000

EXPOSE 5000
CMD ["python", "app.py"]
```

## 🤝 Contribuire

1. Fork del repository
2. Crea branch feature (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Apri Pull Request

## 📄 Licenza

WebLib v2.0 è rilasciato sotto licenza MIT.

## 📞 Supporto

- 📧 Email: support@weblib.dev
- 🐛 Bug Reports: [GitHub Issues](https://github.com/weblib/issues)
- 💬 Discussioni: [GitHub Discussions](https://github.com/weblib/discussions)

---

⭐ **WebLib v2.0** - Framework Python multi-database e multi-CSS per applicazioni web moderne!
# weblib
