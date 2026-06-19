import os
import sys

# Adicionar o diretório src ao path para permitir importações dos módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import create_app

app = create_app()


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(host="0.0.0.0",debug=app.config.get("DEBUG", True))
