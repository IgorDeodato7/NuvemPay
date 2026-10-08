
# 💙 NuvemPay

### Sistema Financeiro Fictício | Projeto Acadêmico de Segurança Cibernética

O **NuvemPay** é uma aplicação web que simula uma plataforma bancária digital, desenvolvida para fins educacionais.

O projeto permite realizar operações financeiras fictícias, gerenciar contas de demonstração e consultar históricos de transferências.

Seu principal objetivo é aplicar conhecimentos de desenvolvimento web, banco de dados e segurança de aplicações.

> ⚠️ **Aviso:** O NuvemPay é um ambiente acadêmico e fictício. Não realiza operações bancárias reais e não deve ser utilizado para armazenar informações financeiras verdadeiras.

---

## 🚀 Funcionalidades

- 🔐 Autenticação de usuários
- 👤 Contas fictícias de demonstração
- 💰 Visualização de saldo disponível
- 💸 Transferências entre usuários
- 📋 Histórico de transações
- 🛡️ Proteção de rotas autenticadas
- 🔒 Proteção CSRF em formulários
- ✅ Validação de valores e saldo disponível
- 📱 Interface web organizada e responsiva

---

## 🛠️ Tecnologias utilizadas

**Backend**
- Python
- Flask

**Frontend**
- HTML5
- CSS3
- JavaScript

**Banco de dados**
- SQLite

**Segurança**
- Hash de senhas com Werkzeug
- Gerenciamento de sessões
- Tokens CSRF
- Consultas SQL parametrizadas
- Variáveis de ambiente
- Validação de transferências

**Ferramentas**
- Visual Studio Code
- Git e GitHub

---

## 📸 Demonstração

O sistema possui uma interface de login e um painel financeiro com informações de contas fictícias.

### Tela de login

Imagem em preparação.

### Dashboard

Imagem em preparação.

### Transferências e extrato

Imagem em preparação.

---

## ⚙️ Como executar localmente

### 1. Clonar o repositório

```bash
git clone URL_DO_REPOSITORIO
cd NuvemPay
```

### 2. Criar o ambiente virtual

```bash
python -m venv venv
```

### 3. Ativar o ambiente virtual

No Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 5. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```dotenv
SECRET_KEY=INSIRA_UMA_CHAVE_ALEATORIA
FLASK_DEBUG=0
```

Para gerar uma chave aleatória:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Executar a aplicação

```bash
python app.py
```

Acesse:

http://127.0.0.1:5000

> O banco de dados local não acompanha o repositório. As contas de demonstração devem ser configuradas separadamente.

---

## 🛡️ Segurança da aplicação

O NuvemPay implementa mecanismos básicos de proteção, incluindo:

- Autenticação e controle de acesso
- Proteção contra CSRF
- Validação de dados no servidor
- Verificação de saldo antes das transferências
- Operações financeiras fictícias com transações atômicas
- Consultas parametrizadas para reduzir riscos de SQL Injection
- Proteção de configurações sensíveis por variáveis de ambiente

Esses mecanismos fazem parte do aprendizado e não representam uma certificação de segurança da aplicação.

---

## 🎓 Objetivo acadêmico

O projeto foi desenvolvido para colocar em prática conhecimentos relacionados a:

- Desenvolvimento de aplicações web
- Fundamentos de Segurança Cibernética
- Autenticação e sessões
- Segurança de banco de dados
- Validação de entradas
- Testes de segurança em ambiente controlado

---

## 📌 Status do projeto

**Em desenvolvimento acadêmico.**

Funcionalidades principais implementadas e testadas localmente. Publicação e implantação em nuvem em preparação.

---

## 👨‍💻 Autor

**Igor Deodato Gregorio**

Estudante de Tecnologia em Segurança Cibernética — SENAI.

Projeto desenvolvido para fins acadêmicos e de aprendizado.
