# config.py

class Config:
    # Secret Key
    SECRET_KEY = "grocery_secret_key_2026"

    # MySQL Configuration
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "Nishu@15"
    MYSQL_DB = "grocery_db"
    MYSQL_CURSORCLASS = "DictCursor"
    

    # Upload Folder
    UPLOAD_FOLDER = "static/images/products"

    # Maximum Upload Size (5 MB)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024