# 🃏 Planning Poker

Aplicação de Planning Poker em tempo real para times ágeis. Crie uma sala, compartilhe o link e vote com seu time sem recarregar a página.

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend | Python + FastAPI + WebSockets |
| Frontend | Vue 3 + Vite + TailwindCSS v4 |
| Estilização | Glassmorphism, Inter (Google Fonts), gradientes |

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

## Estrutura

```
planpoker/
├── backend/
│   ├── main.py           # FastAPI + WebSocket server
│   └── requirements.txt
└── frontend/
    └── src/
        ├── views/
        │   ├── HomeView.vue   # Tela de entrada
        │   └── RoomView.vue   # Mesa de votação
        └── router/index.js
```
