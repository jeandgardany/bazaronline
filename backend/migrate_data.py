from flask import Flask
from backend import create_app, db
from backend.utils.data_migration import migrar_dados

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        migrar_dados()