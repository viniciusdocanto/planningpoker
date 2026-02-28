# Changelog

## [0.4.0] - 2026-02-28

### Adicionado
- `public/favicon.svg` — ícone personalizado do Planning Poker (cartas com gradiente indigo/purple)
- Seção de variáveis de ambiente no `README.md`
- Seção de licença no `README.md`
- Badges de versão e licença no `README.md`

### Alterado
- `package.json`: nome (`frontend` → `planning-poker`), versão (`0.0.0` → `0.3.0`), description, author, license e homepage adicionados
- `index.html`: título, lang, favicon e meta description atualizados
- `README.md`: estrutura do projeto atualizada, `.env.example`, favicon e segurança adicionados
- `frontend/.gitignore`: simplificado (a raiz já cobre tudo)

### Removido
- `src/components/HelloWorld.vue` — componente de exemplo do Vite
- `src/assets/vue.svg` — logo padrão do Vue
- `public/vite.svg` — logo padrão do Vite (substituído pelo favicon personalizado)

---

## [0.3.0] - 2026-02-28

### Segurança
- **Backend:** Adicionado middleware CORS — somente origens do frontend são aceitas (`localhost:5173`)
- **Backend:** Validação de `room_id` e `user_name` com regex antes de aceitar conexão WebSocket
- **Backend:** Prevenção de colisão de nomes — usuário com nome duplicado na mesma sala é rejeitado com código `1008`
- **Backend:** Limite de 20 usuários por sala — sala lotada retorna erro ao tentar conectar
- **Backend:** Whitelist de votos válidos — apenas as cartas do baralho são aceitas; valores arbitrários são ignorados
- **Backend:** Bloqueio de re-votação após revelar — votos não podem ser alterados após revelação
- **Backend:** Try/except em torno de `receive_json()` — JSON inválido fecha a conexão de forma controlada
- **Backend:** Limpeza de conexões mortas no broadcast — remove silenciosamente sockets que falharam
- **Frontend:** URL do WebSocket extraída para variável de ambiente `VITE_WS_URL` (arquivo `.env`)
- **Frontend:** Validação client-side de nome e ID de sala espelhando as regras do servidor (regex + limites de tamanho)
- **Frontend:** Room ID do parâmetro de URL (`?room=`) é validado antes de ser usado
- **Frontend:** `JSON.parse` no `onmessage` envolto em try/catch — mensagens malformadas são descartadas sem crash
- **Frontend:** Mensagem de erro exibida ao usuário para entradas inválidas

### Adicionado
- Arquivo `.env.example` documentando a variável `VITE_WS_URL`

---

## [0.2.0] - 2026-02-28

### Adicionado
- Design premium com estética glassmorphism (cards e header com efeito vidro)
- Fonte Inter (Google Fonts) para tipografia refinada
- Fundo escuro com gradiente radial sutil em indigo e purple
- Logo animado com gradiente indigo → purple → fuchsia e efeito float
- Botões com gradiente e sombra colorida (indigo/purple para revelar, rose/pink para resetar)
- Mesa oval de feltro verde com indicador de progresso (X/Y votaram)
- Media dos votos exibida na mesa ao revelar
- Baralho premium: cards brancos com efeito hover elevado e glow ao selecionar
- Badge visual de status de conexão (ponto verde/amarelo animado)

### Alterado
- Migração do TailwindCSS para integração via `@tailwindcss/vite` (v4), corrigindo compilação no Vite
- Refatoração completa das views `HomeView.vue` e `RoomView.vue`
- `style.css` atualizado com utilitários `.glass`, `.glass-hover`, `.glow-blue`, `.glow-purple`, `.text-gradient`, `.card-hover`

---

## [0.1.0] - 2026-02-28

### Adicionado
- Criação de salas com ID aleatório de 20 caracteres alfanuméricos
- Entrada em sala existente via ID ou link de convite
- Tela inicial diferenciada ao acessar por link de convite (modo "Join Room")
- Botão de copiar link de convite (`/?room=ID`) diretamente na sala
- Baralho Fibonacci: `0, ½, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ?, ☕`
- Votos ocultos até revelação pelo host
- Somente o criador da sala (host) pode revelar e resetar os votos
- Passagem automática de host quando o criador abandona a sala
- Badge de host (👑) visível na lista de jogadores
- Destaque do próprio jogador como "Você"
- Média automática dos votos numéricos exibida ao revelar
- Painel de resultados pós-revelação
- Empty state quando a sala está sem jogadores
- Status de conexão WebSocket em tempo real (Conectado / Reconectando...)
- Reconexão automática com tentativa a cada 3 segundos em caso de queda
- Limpeza automática de salas vazias no servidor
