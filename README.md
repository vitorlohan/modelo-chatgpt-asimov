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
   cd modelo-chatgpt-asimov
   ```
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
uv run uvicorn main:app --reload
```

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

## Trocando o modelo

Edite a variável `MODELO` no topo do [main.py](main.py). Ela aceita qualquer ID da [lista de modelos do OpenRouter](https://openrouter.ai/models), por exemplo `openai/gpt-4o-mini` ou `anthropic/claude-sonnet-4.5`.

Os modelos com sufixo `:free` usam uma cota compartilhada entre todos os usuários e costumam retornar **429 (Too Many Requests)** em horários de pico. Nesse caso, tente de novo mais tarde ou use um modelo pago.

## Estrutura

| Arquivo | Para que serve |
|---|---|
| `main.py` | A API: o endpoint `send_message` e a chamada ao OpenRouter |
| `pyproject.toml` / `uv.lock` | Dependências gerenciadas pelo uv |
| `.env.example` | Modelo do `.env` (sem a chave real) |

## Comandos úteis do uv

- `uv add <pacote>` adiciona uma dependência.
- `uv remove <pacote>` remove uma dependência.
- `uv sync` reinstala tudo conforme o `uv.lock`.
