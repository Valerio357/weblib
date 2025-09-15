CLI

La CLI fornisce comandi minimi utili in sviluppo.

Comandi disponibili

- `weblib new <nome>`: crea una cartella con un `app.py` esempio.
- `weblib dev`: suggerimento su come avviare il dev server con Uvicorn.
- `weblib routes`: placeholder per ispezionare le rotte.

Esempio

```
weblib new mysite
cd mysite
uvicorn app:asgi --reload
```

