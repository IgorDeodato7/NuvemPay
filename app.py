
import os
import secrets
from decimal import Decimal, InvalidOperation
from functools import wraps

from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort
)

from werkzeug.security import check_password_hash

from database import conectar, criar_banco


# ==========================================
# CONFIGURAÇÕES INICIAIS
# ==========================================

# Carrega as variáveis do arquivo .env
load_dotenv()

# Inicializa a aplicação Flask
app = Flask(__name__)

# Chave secreta obtida do ambiente
app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "A variável SECRET_KEY não foi configurada."
    )

# Configurações de segurança da sessão
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get(
        "FLASK_ENV"
    ) == "production"
)

# Inicializa o banco de dados
criar_banco()


# ==========================================
# PROTEÇÃO DE ROTAS
# ==========================================

def login_obrigatorio(funcao):

    @wraps(funcao)
    def verificar(*args, **kwargs):

        if "usuario_id" not in session:
            return redirect(url_for("login"))

        return funcao(*args, **kwargs)

    return verificar


# ==========================================
# PROTEÇÃO CSRF
# ==========================================

def token_csrf():

    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)

    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = token_csrf


@app.before_request
def verificar_csrf():

    if request.method == "POST":

        token_enviado = request.form.get(
            "csrf_token", ""
        )

        token_sessao = session.get(
            "csrf_token", ""
        )

        if not token_sessao or not secrets.compare_digest(
            token_enviado,
            token_sessao
        ):
            abort(
                400,
                description="Token CSRF inválido."
            )


# ==========================================
# FORMATAÇÃO DE MOEDA
# ==========================================

def formatar_moeda(centavos):

    valor = centavos / 100

    return "R$ " + (
        f"{valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


app.jinja_env.filters["moeda"] = formatar_moeda


# ==========================================
# LOGIN
# ==========================================

@app.route("/", methods=["GET", "POST"])
def login():

    if "usuario_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        senha = request.form.get(
            "senha", ""
        )

        with conectar() as banco:

            usuario = banco.execute(
                """
                SELECT *
                FROM usuarios
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

        if usuario and check_password_hash(
            usuario["senha"],
            senha
        ):

            session.clear()

            session["usuario_id"] = usuario["id"]

            token_csrf()

            return redirect(url_for("dashboard"))

        flash("E-mail ou senha inválidos.")

    return render_template("login.html")


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/dashboard")
@login_obrigatorio
def dashboard():

    with conectar() as banco:

        usuario = banco.execute(
            """
            SELECT
                id,
                nome,
                email,
                saldo_centavos
            FROM usuarios
            WHERE id = ?
            """,
            (session["usuario_id"],)
        ).fetchone()

        if usuario is None:

            session.clear()

            return redirect(url_for("login"))

        # Lista de destinatários
        destinatarios = banco.execute(
            """
            SELECT id, nome, email
            FROM usuarios
            WHERE id != ?
            ORDER BY nome
            """,
            (usuario["id"],)
        ).fetchall()

        # Histórico de transações
        transacoes = banco.execute(
            """
            SELECT
                t.id,
                t.remetente_id,
                t.destinatario_id,
                t.valor_centavos,
                t.data,
                r.nome AS remetente,
                d.nome AS destinatario

            FROM transacoes t

            JOIN usuarios r
                ON r.id = t.remetente_id

            JOIN usuarios d
                ON d.id = t.destinatario_id

            WHERE t.remetente_id = ?
               OR t.destinatario_id = ?

            ORDER BY t.id DESC

            LIMIT 20
            """,
            (
                usuario["id"],
                usuario["id"]
            )
        ).fetchall()

    return render_template(
        "dashboard.html",
        usuario=usuario,
        saldo=usuario["saldo_centavos"] / 100,
        destinatarios=destinatarios,
        transacoes=transacoes
    )


# ==========================================
# TRANSFERÊNCIAS
# ==========================================

@app.route("/transferir", methods=["POST"])
@login_obrigatorio
def transferir():

    try:

        destinatario_id = int(
            request.form.get(
                "destinatario_id", ""
            )
        )

        valor_texto = request.form.get(
            "valor", ""
        ).strip().replace(",", ".")

        valor = Decimal(valor_texto)

        # Impede valores infinitos ou NaN
        if not valor.is_finite():
            raise ValueError()

        # Impede valores zerados, negativos
        # ou com mais de duas casas decimais
        if (
            valor <= 0
            or valor.as_tuple().exponent < -2
        ):
            raise ValueError()

        valor_centavos = int(valor * 100)

        # Limite por operação para a demonstração
        if valor_centavos > 100_000_000:
            raise ValueError()

    except (
        ValueError,
        InvalidOperation,
        OverflowError
    ):

        flash(
            "Informe um destinatário e valor válidos."
        )

        return redirect(
            url_for("dashboard") + "#transferencia"
        )

    remetente_id = session["usuario_id"]

    # Impede transferência para si mesmo
    if remetente_id == destinatario_id:

        flash(
            "Você não pode transferir para sua própria conta."
        )

        return redirect(
            url_for("dashboard") + "#transferencia"
        )

    banco = conectar()

    try:

        # Inicia transação atômica
        banco.execute("BEGIN IMMEDIATE")

        # Verifica destinatário
        destinatario = banco.execute(
            """
            SELECT id
            FROM usuarios
            WHERE id = ?
            """,
            (destinatario_id,)
        ).fetchone()

        if destinatario is None:
            raise ValueError(
                "Destinatário não encontrado."
            )

        # Debita o remetente
        resultado = banco.execute(
            """
            UPDATE usuarios
            SET saldo_centavos = saldo_centavos - ?
            WHERE id = ?
              AND saldo_centavos >= ?
            """,
            (
                valor_centavos,
                remetente_id,
                valor_centavos
            )
        )

        if resultado.rowcount != 1:

            raise ValueError(
                "Saldo insuficiente ou conta inválida."
            )

        # Credita o destinatário
        resultado_destino = banco.execute(
            """
            UPDATE usuarios
            SET saldo_centavos = saldo_centavos + ?
            WHERE id = ?
            """,
            (
                valor_centavos,
                destinatario_id
            )
        )

        if resultado_destino.rowcount != 1:
            raise ValueError(
                "Não foi possível creditar o destinatário."
            )

        # Registra a transferência
        banco.execute(
            """
            INSERT INTO transacoes (
                remetente_id,
                destinatario_id,
                valor_centavos
            )
            VALUES (?, ?, ?)
            """,
            (
                remetente_id,
                destinatario_id,
                valor_centavos
            )
        )

        # Confirma todas as operações
        banco.commit()

        flash(
            "Transferência realizada com sucesso!"
        )

    except ValueError as erro:

        banco.rollback()

        flash(str(erro))

    except Exception:

        banco.rollback()

        app.logger.exception(
            "Erro ao realizar transferência"
        )

        flash(
            "Não foi possível realizar a transferência."
        )

    finally:

        banco.close()

    return redirect(
        url_for("dashboard") + "#extrato"
    )


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout", methods=["POST"])
@login_obrigatorio
def logout():

    session.clear()

    return redirect(url_for("login"))


# ==========================================
# INICIALIZAÇÃO DO SERVIDOR
# ==========================================

if __name__ == "__main__":

    # Debug permitido somente no ambiente local
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=os.environ.get("FLASK_DEBUG") == "1"
    )
