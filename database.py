
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "nuvempay.db"


def conectar():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_banco():
    with conectar() as banco:
        banco.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                saldo_centavos INTEGER NOT NULL DEFAULT 0
                    CHECK (saldo_centavos >= 0)
            )
        """)

        banco.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remetente_id INTEGER NOT NULL,
                destinatario_id INTEGER NOT NULL,
                valor_centavos INTEGER NOT NULL
                    CHECK (valor_centavos > 0),
                data TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (remetente_id) REFERENCES usuarios(id),
                FOREIGN KEY (destinatario_id) REFERENCES usuarios(id)
            )
        """)

        quantidade = banco.execute(
            "SELECT COUNT(*) FROM usuarios"
        ).fetchone()[0]

        if quantidade == 0:
            usuarios = [
                ("Ana Silva", "ana@nuvempay.test", 500000),
                ("Bruno Costa", "bruno@nuvempay.test", 350000),
                ("Carla Souza", "carla@nuvempay.test", 720000),
                ("Daniel Lima", "daniel@nuvempay.test", 180000),
                ("Eduarda Rocha", "eduarda@nuvempay.test", 950000)
            ]

            senha_hash = generate_password_hash(
                "Nuvem@2026"
            )

            banco.executemany("""
                INSERT INTO usuarios
                    (nome, email, senha, saldo_centavos)
                VALUES (?, ?, ?, ?)
            """, [
                (nome, email, senha_hash, saldo)
                for nome, email, saldo in usuarios
            ])

        print("Banco de dados preparado!")


if __name__ == "__main__":
    criar_banco()
