# 🃏 Planning Poker

> Estime tarefas com seu time em tempo real, sem recarregar a página.

[![version](https://img.shields.io/badge/version-0.18.0-indigo.svg)](CHANGELOG.md)
[![license](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 · FastAPI · WebSockets · Pydantic v2 · Redis |
| Frontend | Vue 3 · Vite · TypeScript · TailwindCSS v4 · Vue Router · **Vue I18n** |
| Testes | **Playwright (E2E)** |
| Estilização | Glassmorphism · Inter (Google Fonts) · gradientes |
| Deploy | Render (backend + Redis) · GitHub Pages (frontend) |

## Pré-requisitos

- Python 3.8+
- Node.js 18+

## Como rodar

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
cp .env.example .env   # configure VITE_WS_URL se necessário
npm install
npm run dev
```

Acesse em: **http://localhost:5173**

## Funcionalidades

- 🚩 **Criar/entrar em sala** — ID aleatório de 20 caracteres ou ID personalizado
- 🔗 **Link de convite** — compartilhe a sala com um clique
- 👑 **Host da sala** — criador controla quando revelar as cartas
- 🔑 **Passagem de host** — se o host sair, o próximo assume
- 🃏 **Baralhos customizáveis** — Fibonacci, Potências de 2 ou T-Shirt Sizes
- 🕵️ **Votos ocultos** — revelados todos ao mesmo tempo
- 📊 **Média automática** — calculada ao revelar (ignora ?, ☕)
- ⏱️ **Temporizador** — host pode iniciar countdown para agilizar estimativas
- 📋 **Histórico de rodadas** — dropdown no header com todas as estimativas da sessão
- 🔔 **Notificações toast** — alertas ao entrar/sair da sala e mudanças de conexão
- 🔄 **Reconexão automática** — resiste a quedas de conexão
- 💾 **Persistência** — estado das salas sobrevive a reinicializações (Redis)
- 🎨 **Design premium** — glassmorphism, gradientes, tema claro/escuro
- 🔒 **Segurança** — validação server + client, CORS, whitelist de votos, limite de sala
- 🔊 **Feedback Sensorial** — sons sutis ao revelar cartas e vibração (mobile) ao votar
- 🌍 **Internacionalização (I18n)** — suporte para Português, Inglês e Espanhol
- 🧪 **Testes E2E** — suíte de testes robusta com Playwright para garantir fluxos críticos
- 🛡️ **Robustez** — tratamento de erros defensivos para evitar falhas de interface em produção

## Estrutura

```
planpoker/
├── .gitignore
├── README.md
├── CHANGELOG.md
├── backend/
│   ├── main.py           # FastAPI + WebSocket server
│   └── requirements.txt
└── frontend/
    ├── .env.example      # configuração de ambiente
    ├── public/
    │   └── favicon.svg   # ícone personalizado
    └── src/
        ├── views/
        │   ├── HomeView.vue   # tela de entrada
        │   └── RoomView.vue   # mesa de votação
        ├── router/index.js
        ├── App.vue
        └── style.css
```

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `VITE_WS_URL` | `ws://localhost:8000` | URL base do servidor WebSocket |

## Deploy (Render + Hostinger)

### 1. Backend no Render

1. Acesse [render.com](https://render.com) e crie uma conta
2. Clique em **New → Web Service** e conecte ao repositório do GitHub
3. Configure:
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Em **Environment Variables**, adicione:
   - `ALLOWED_ORIGINS` → `https://seusite.com.br,https://www.seusite.com.br`
5. Clique em **Deploy** e anote a URL gerada (ex: `https://planning-poker-api.onrender.com`)

### 2. Frontend para a Hostinger

1. Atualize `frontend/.env.production` com a URL do Render:
```
VITE_WS_URL=wss://planning-poker-api.onrender.com
```
2. Gere o build de produção:
```bash
cd frontend
npm run build
```
3. Faça upload da pasta `frontend/dist/` para o **Gerenciador de Arquivos** da Hostinger (pasta `public_html`)

> ⚠️ O plano gratuito do Render hiberna o servidor após 15 min de inatividade. A primeira conexão pode demorar ~30s para acordar.

## CI/CD — Deploy automático

O repositório inclui um workflow em `.github/workflows/deploy-frontend.yml` que faz build e deploy automático do frontend para a Hostinger sempre que um push é feito na branch `main` com alterações na pasta `frontend/`.

### Segredos necessários (GitHub → Settings → Secrets → Actions)

| Secret | Descrição |
|---|---|
| `FTP_SERVER` | Endereço FTP da Hostinger (ex: `ftp.seusite.com.br`) |
| `FTP_USERNAME` | Usuário FTP |
| `FTP_PASSWORD` | Senha FTP |
| `FTP_SERVER_DIR` | Diretório de destino no servidor (padrão: `public_html/`) |
| `VITE_WS_URL` | URL do backend no Render (ex: `wss://planning-poker-api.onrender.com`) |

> Os segredos são usados no build e no upload — nunca ficam expostos no código.

## Licença

Este projeto está sob a licença [MIT](LICENSE).

MIT © [Vinicius do Canto](https://github.com/viniciusdocanto)
