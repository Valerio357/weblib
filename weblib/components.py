"""
Sistema di Componenti per WebLib
Permette di creare componenti HTML riutilizzabili
"""

from typing import Dict, Any, List, Optional, Callable
from .html import *
from typing import List, Union, Optional, Dict, Any
from .config import CSSClasses


class Component:
    """Classe base per componenti riutilizzabili"""
    
    def __init__(self, **props):
        self.props = props
        self._children = []
    
    def render(self) -> HtmlElement:
        """Deve essere implementato dalle sottoclassi"""
        raise NotImplementedError("Component must implement render() method")
    
    def add_child(self, child):
        """Aggiunge un figlio al componente"""
        self._children.append(child)
        return self
    
    def get_prop(self, key: str, default=None):
        """Ottiene una proprietà del componente"""
        return self.props.get(key, default)


class Card(Component):
    """Componente Card Bootstrap"""
    
    def render(self) -> HtmlElement:
        title = self.get_prop('title')
        text = self.get_prop('text')
        content_prop = self.get_prop('content', [])  # Aggiungi supporto per content
        footer = self.get_prop('footer')
        classes = self.get_prop('classes', [])
        
        card_classes = [CSSClasses.CARD] + classes
        
        content = []
        
        # Header se presente
        if self.get_prop('header'):
            header_div = Div(self.get_prop('header'), classes=[CSSClasses.CARD_HEADER])
            content.append(header_div)
        
        # Body
        body_content = []
        if title:
            if isinstance(title, str):
                body_content.append(H5(title, classes=[CSSClasses.CARD_TITLE]))
            else:
                body_content.append(title)
        
        if text:
            if isinstance(text, str):
                body_content.append(P(text, classes=[CSSClasses.CARD_TEXT]))
            else:
                body_content.append(text)
        
        # Aggiungi contenuto dal prop content
        if content_prop:
            if isinstance(content_prop, list):
                body_content.extend(content_prop)
            else:
                body_content.append(content_prop)
        
        # Aggiungi figli personalizzati
        body_content.extend(self._children)
        
        if body_content:
            content.append(Div(body_content, classes=[CSSClasses.CARD_BODY]))
        
        # Footer se presente
        if footer:
            footer_div = Div(footer, classes=[CSSClasses.CARD_FOOTER])
            content.append(footer_div)
        
        return Div(content, classes=card_classes)


class Alert(Component):
    """Componente Alert Bootstrap"""
    
    def render(self) -> HtmlElement:
        message = self.get_prop('message', '')
        alert_type = self.get_prop('type', 'info')  # info, success, warning, danger
        dismissible = self.get_prop('dismissible', False)
        classes = self.get_prop('classes', [])
        
        alert_classes = [CSSClasses.ALERT, f"alert-{alert_type}"] + classes
        
        content = [message] + self._children
        
        if dismissible:
            alert_classes.append('alert-dismissible')
            close_btn = Button([
                Span("&times;", **{"aria-hidden": "true"})
            ], classes=["btn-close"], **{"data-bs-dismiss": "alert", "aria-label": "Close"})
            content.append(close_btn)
        
        return Div(content, classes=alert_classes, role="alert")


class NavBar(Component):
    """Componente NavBar Bootstrap"""
    
    def render(self) -> HtmlElement:
        brand = self.get_prop('brand')
        links = self.get_prop('links', [])
        theme = self.get_prop('theme', 'light')  # light, dark
        expand = self.get_prop('expand', 'lg')
        classes = self.get_prop('classes', [])
        
        navbar_classes = [
            CSSClasses.NAVBAR,
            f"navbar-expand-{expand}",
            f"navbar-{theme}"
        ] + classes
        
        content = []
        
        # Brand
        if brand:
            if isinstance(brand, str):
                brand_element = A(brand, classes=[CSSClasses.NAVBAR_BRAND], href="/")
            else:
                brand_element = brand
            content.append(brand_element)
        
        # Links
        if links:
            nav_links = []
            for link in links:
                if isinstance(link, dict):
                    nav_links.append(
                        Li(A(link['text'], href=link['url'], classes=[CSSClasses.NAV_LINK]))
                    )
                else:
                    nav_links.append(Li(link))
            
            nav_ul = Ul(nav_links, classes=["navbar-nav", "me-auto"])
            content.append(nav_ul)
        
        # Figli personalizzati
        content.extend(self._children)
        
        return Nav(content, classes=navbar_classes)


class Modal(Component):
    """Componente Modal Bootstrap"""
    
    def render(self) -> HtmlElement:
        modal_id = self.get_prop('id', 'modal')
        title = self.get_prop('title', 'Modal')
        size = self.get_prop('size', '')  # '', 'sm', 'lg', 'xl'
        
        modal_classes = ["modal", "fade"]
        dialog_classes = ["modal-dialog"]
        
        if size:
            dialog_classes.append(f"modal-{size}")
        
        # Header
        header = Div([
            H5(title, classes=["modal-title"]),
            Button([Span("&times;")], classes=["btn-close"], **{"data-bs-dismiss": "modal"})
        ], classes=["modal-header"])
        
        # Body
        body = Div(self._children, classes=["modal-body"])
        
        # Footer (se specificato)
        footer_content = self.get_prop('footer')
        content = [header, body]
        
        if footer_content:
            footer = Div(footer_content, classes=["modal-footer"])
            content.append(footer)
        
        modal_content = Div(content, classes=["modal-content"])
        modal_dialog = Div([modal_content], classes=dialog_classes)
        
        return Div([modal_dialog], 
                  classes=modal_classes, 
                  id=modal_id, 
                  tabindex="-1",
                  **{"aria-hidden": "true"})


class Breadcrumb(Component):
    """Componente Breadcrumb Bootstrap"""
    
    def render(self) -> HtmlElement:
        items = self.get_prop('items', [])
        
        breadcrumb_items = []
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            
            if isinstance(item, dict):
                text = item['text']
                url = item.get('url')
                
                if is_last or not url:
                    # Ultimo elemento o senza link
                    breadcrumb_items.append(Li(text, classes=["breadcrumb-item", "active"]))
                else:
                    # Elemento con link
                    breadcrumb_items.append(Li(A(text, href=url), classes=["breadcrumb-item"]))
            else:
                # Stringa semplice
                classes = ["breadcrumb-item"]
                if is_last:
                    classes.append("active")
                breadcrumb_items.append(Li(item, classes=classes))
        
        return Nav([
            Ul(breadcrumb_items, classes=["breadcrumb"])
        ], **{"aria-label": "breadcrumb"})


class Pagination(Component):
    """Componente Paginazione Bootstrap"""
    
    def render(self) -> HtmlElement:
        current_page = self.get_prop('current_page', 1)
        total_pages = self.get_prop('total_pages', 1)
        base_url = self.get_prop('base_url', '?page=')
        
        pages = []
        
        # Previous
        if current_page > 1:
            pages.append(Li(
                A("Previous", href=f"{base_url}{current_page-1}"),
                classes=["page-item"]
            ))
        else:
            pages.append(Li(
                Span("Previous"),
                classes=["page-item", "disabled"]
            ))
        
        # Pagine numeriche
        start = max(1, current_page - 2)
        end = min(total_pages + 1, current_page + 3)
        
        for page in range(start, end):
            if page == current_page:
                pages.append(Li(
                    Span(str(page)),
                    classes=["page-item", "active"]
                ))
            else:
                pages.append(Li(
                    A(str(page), href=f"{base_url}{page}"),
                    classes=["page-item"]
                ))
        
        # Next
        if current_page < total_pages:
            pages.append(Li(
                A("Next", href=f"{base_url}{current_page+1}"),
                classes=["page-item"]
            ))
        else:
            pages.append(Li(
                Span("Next"),
                classes=["page-item", "disabled"]
            ))
        
        return Nav([
            Ul(pages, classes=["pagination"])
        ])


class Badge(Component):
    """Componente Badge Bootstrap"""
    
    def render(self) -> HtmlElement:
        text = self.get_prop('text', '')
        variant = self.get_prop('variant', 'primary')
        pill = self.get_prop('pill', False)
        classes = self.get_prop('classes', [])
        
        badge_classes = [f"badge", f"bg-{variant}"] + classes
        if pill:
            badge_classes.append("rounded-pill")
        
        return Span([text] + self._children, classes=badge_classes)


# Decorator per registrare componenti
_registered_components = {}

def component(name: str = None):
    """Decorator per registrare un componente personalizzato"""
    def decorator(cls):
        component_name = name or cls.__name__.lower()
        _registered_components[component_name] = cls
        return cls
    return decorator


def get_component(name: str) -> Optional[type]:
    """Ottiene un componente registrato"""
    return _registered_components.get(name)


def list_components() -> List[str]:
    """Lista tutti i componenti registrati"""
    return list(_registered_components.keys())


# Registra i componenti predefiniti
_registered_components.update({
    'card': Card,
    'alert': Alert,
    'navbar': NavBar,
    'modal': Modal,
    'breadcrumb': Breadcrumb,
    'pagination': Pagination,
    'badge': Badge,
})
