"""Cria cinco contas fictícias com senhas exclusivas. Execute UMA vez no banco vazio."""
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from database import conectar, criar_banco

load_dotenv()
CONTAS = [
    ('Rafael Martins', 'rafael@nuvempay.test', 125075),
    ('Beatriz Oliveira', 'beatriz@nuvempay.test', 38540),
    ('Lucas Ferreira', 'lucas@nuvempay.test', 218090),
    ('Mariana Ribeiro', 'mariana@nuvempay.test', 9765),
    ('Gabriel Almeida', 'gabriel@nuvempay.test', 74020),
]

def main():
    criar_banco()
    arquivo = Path(__file__).parent / 'credenciais_demo_privadas.txt'
    if arquivo.exists():
        raise RuntimeError('Arquivo de credenciais já existe. Não executar novamente.')
    with conectar() as banco:
        qtd = banco.execute('SELECT COUNT(*) AS total FROM usuarios').fetchone()['total']
        if qtd:
            raise RuntimeError('O banco não está vazio; nenhuma conta foi alterada.')
        linhas = []
        for nome, email, saldo in CONTAS:
            senha = secrets.token_urlsafe(18)
            banco.execute('INSERT INTO usuarios (nome, email, senha, saldo_centavos) VALUES (%s, %s, %s, %s)',
                          (nome, email, generate_password_hash(senha), saldo))
            linhas.append(f'{nome} | {email} | {senha}')
        arquivo.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
        try:
            os.chmod(arquivo, 0o600)
        except OSError:
            pass
    print('Contas criadas. Guarde credenciais_demo_privadas.txt em local seguro; NÃO publique no GitHub.')

if __name__ == '__main__':
    main()
