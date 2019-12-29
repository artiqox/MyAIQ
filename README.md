# [MyAIQ](https://www.artiqox.com)

**[Open-Source Web Service for ArtiqoxEnergy Blockchain](https://www.artiqox.com)** coded in **Flask Framework** on top of **Adminator Dashboard** design. **Features**:

- MySQL database
- SQLAlchemy ORM
- Session-Based authentication flow (login, register)
- UI Kit: [Adminator Free Dashboard](https://github.com/app-generator/fork-adminator-admin-dashboard) by **ColorLib**

<br />

![Flask Dashboard Adminator - Open-Source Flask Dashboard.](https://raw.githubusercontent.com/app-generator/static/master/products/flask-dashboard-adminator-intro.gif)

<br />

## Build from sources

```bash
$ # Clone the sources
$ git clone https://github.com/artiqox/MyAIQ.git
$ cd flask-dashboard-adminator
$
$ # Virtualenv modules installation (Unix based systems)
$ virtualenv --no-site-packages env
$ source env/bin/activate
$
$ # Virtualenv modules installation (Windows based systems)
$ # virtualenv --no-site-packages env
$ # .\env\Scripts\activate
$ 
$ # Install requirements
$ pip3 install -r requirements.txt
$
$ # Set the FLASK_APP environment variable
$ (Unix/Mac) export FLASK_APP=run.py
$ (Windows) set FLASK_APP=run.py
$ (Powershell) $env:FLASK_APP = ".\run.py"
$
$ # Set up the DEBUG environment
$ # (Unix/Mac) export FLASK_ENV=development
$ # (Windows) set FLASK_ENV=development
$ # (Powershell) $env:FLASK_ENV = "development"
$
$ # Run the application
$ # --host=0.0.0.0 - expose the app on all network interfaces (default 127.0.0.1)
$ # --port=5000    - specify the app port (default 5000)  
$ flask run --host=0.0.0.0 --port=5000
$
$ # Access the app in browser: http://127.0.0.1:5000/
```

<br />

## Want more? Hold your horses, we are building it

<br />

## License

@MIT

<br />

---
[Artiqox](https://www.artiqox.com)
