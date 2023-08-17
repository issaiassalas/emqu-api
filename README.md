
# EMQU-API

Prueba tecnica de aplicacion.

Para instalar las dependencias se recomienda usar un entorno virtual con python en su version 3.11




## Installation

Install project dependencies

```bash
    pip install -r requirements.txt
```

Setup the database in scr/config.py, by default SQLite3

```bash
    flask db init
    flask db migrate
    flask db upgrade
```

Run the server

```bash
    flask run
```


## Acknowledgements

 - The Api works with jwt auth
 - Related endpoints in endpoints.txt
 - All the endpoint require header 'Authorization: Bearer token'