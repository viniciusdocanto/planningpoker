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

## Licença

MIT © [Vinicius](https://github.com/viniciusdocanto)
