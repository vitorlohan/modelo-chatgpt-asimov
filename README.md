# modelo-chatgpt-asimov

API em FastAPI com um único endpoint, `POST /send_message`. Ela recebe a mensagem do usuário, envia para um modelo de IA via [OpenRouter](https://openrouter.ai/docs/api_reference/overview) e devolve a resposta.

## Pré-requisitos

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/). No Windows (PowerShell):
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
  O uv baixa o Python sozinho se ele não estiver instalado.
- Uma chave de API do OpenRouter: https://openrouter.ai/keys

## Configurando em um PC novo

1. Clone o repositório:
   ```powershell
   git clone https://github.com/vitorlohan/modelo-chatgpt-asimov.git
   cd modelo-chatgpt-asimov\backend
   ```
   Todos os comandos abaixo são executados dentro da pasta `backend/`.
2. Crie o arquivo `.env` a partir do exemplo e coloque a sua chave nele:
   ```powershell
   copy .env.example .env
   ```
   ```
   OPENROUTER_API_KEY=sk-or-v1-...
   ```
   O `.env` está no `.gitignore` e **nunca** deve ser commitado.
3. Instale as dependências. O comando cria o `.venv` a partir do `uv.lock`:
   ```powershell
   uv sync
   ```

## Rodando

```powershell
cd backend
uv run start
```

O comando `start` está definido em `[project.scripts]` no `pyproject.toml`. Ele equivale a `uv run uvicorn main:app --reload`.

Abra **http://127.0.0.1:8000/docs**, clique em `POST /send_message`, depois em **Try it out**, escreva a mensagem e clique em **Execute**.

A raiz (`http://127.0.0.1:8000/`) retorna 404 de propósito, porque a API só tem o endpoint `/send_message`.

### Exemplo de requisição

```
POST /send_message
{"mensagem": "Qual é o sentido da vida?"}
```

Resposta:

```json
{"resposta": "..."}
```

## Banco de dados (PostgreSQL)

O `docker-compose.yml` na raiz sobe um PostgreSQL 16 na porta **5435** do host. Essa porta foi escolhida para não conflitar com outros Postgres na máquina.

1. Crie o `.env` da raiz e defina uma senha:
   ```powershell
   copy .env.example .env
   ```
2. Suba o container:
   ```powershell
   docker compose up -d
   ```

| | |
|---|---|
| Host | `localhost` |
| Porta | `5435` |
| Usuário / Banco | definidos no `.env` (padrão `chatgpt` / `modelo_chatgpt`) |
| Container | `modelo-chatgpt-db` |

Os dados ficam no volume `modelo-chatgpt_pgdata`. O comando `docker compose down` mantém os dados; `docker compose down -v` apaga tudo.

## Autenticação (usuário, senha e JWT)

O chat exige login. Os usuários ficam na tabela `usuarios` do PostgreSQL, que é criada automaticamente quando o backend sobe. As senhas são salvas com hash Argon2.

| Endpoint | O que faz |
|---|---|
| `POST /register` | Cria uma conta. Recebe o JSON `{"usuario": "...", "senha": "..."}`. A senha precisa ter no mínimo 8 caracteres. |
| `POST /login` | Recebe um formulário OAuth2 (`username`, `password`) e devolve `{"access_token": "...", "token_type": "bearer"}`. |
| `GET /me` | Devolve o usuário dono do token. |
| `POST /send_message` | Exige o header `Authorization: Bearer <token>`. |

O token expira em `JWT_EXPIRE_MINUTES` minutos (padrão 60). No `/docs`, use o botão **Authorize** para testar as rotas protegidas.

Variáveis necessárias no `backend/.env` (veja o `backend/.env.example`):
- `DATABASE_URL`: URL do Postgres do compose.
- `JWT_SECRET`: segredo longo e aleatório para assinar os tokens.

Antes de subir o backend, o banco precisa estar rodando (`docker compose up -d` na raiz).

## Trocando o modelo

Edite a variável `MODELO` no topo do [backend/main.py](backend/main.py). Ela aceita qualquer ID da [lista de modelos do OpenRouter](https://openrouter.ai/models), por exemplo `openai/gpt-4o-mini` ou `anthropic/claude-sonnet-4.5`.

Os modelos com sufixo `:free` usam uma cota compartilhada entre todos os usuários e costumam retornar **429 (Too Many Requests)** em horários de pico. Nesse caso, tente de novo mais tarde ou use um modelo pago.

## Estrutura

| Arquivo | Para que serve |
|---|---|
| `backend/main.py` | A API: o endpoint `send_message` e a chamada ao OpenRouter |
| `backend/pyproject.toml` / `backend/uv.lock` | Dependências gerenciadas pelo uv |
| `backend/.env.example` | Modelo do `.env` (sem a chave real) |

## Comandos úteis do uv

Rode-os dentro de `backend/`.

- `uv add <pacote>` adiciona uma dependência.
- `uv remove <pacote>` remove uma dependência.
- `uv sync` reinstala tudo conforme o `uv.lock`.
