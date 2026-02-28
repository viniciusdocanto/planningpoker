# 🃏 Planning Poker

> Estime tarefas com seu time em tempo real, sem recarregar a página.

[![version](https://img.shields.io/badge/version-0.3.0-indigo.svg)](CHANGELOG.md)
[![license](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.8+ · FastAPI · WebSockets · CORS |
| Frontend | Vue 3 · Vite · TailwindCSS v4 · Vue Router |
| Estilização | Glassmorphism · Inter (Google Fonts) · gradientes |

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

- 🚪 **Criar/entrar em sala** — ID aleatório de 20 caracteres
- 🔗 **Link de convite** — compartilhe com um clique
- 👑 **Host da sala** — criador controla quando revelar as cartas
- 🔑 **Passagem de host** — se o host sair, o próximo assume
- 🃏 **Baralho Fibonacci** — 0, ½, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ?, ☕
- 🕵️ **Votos ocultos** — revelados todos ao mesmo tempo
- 📊 **Média automática** — calculada ao revelar
- 🔄 **Reconexão automática** — resiste a quedas de conexão
- 🎨 **Design premium** — glassmorphism, gradientes, mesa de feltro verde
- 🔒 **Segurança** — validação server + client, CORS, whitelist de votos, limite de sala

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
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
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
| `VITE_WS_URL` | URL do backend no Render (ex: `wss://planning-poker-api.onrender.com`) |

> Os segredos são usados no build e no upload — nunca ficam expostos no código.

## Licença

MIT © [Vinicius](https://github.com/viniciusdocanto)
