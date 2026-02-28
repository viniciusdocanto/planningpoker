# Changelog

## [0.6.2] - 2026-02-28

### Corrigido
- **Interface:** Refactor completo das cores do Modo Claro para contraste máximo e melhor acessibilidade.
- **Interface:** Rodapé da sala movido para o final da página (posição relativa) para evitar sobreposição com as cartas selecionadas.
- **Design:** Ajustes de bordas, placeholders e labels para maior nitidez em telas claras.

---

## [0.6.1] - 2026-02-28

### Corrigido
- **Interface:** Melhorado o contraste de textos e rodapés no modo claro para melhor legibilidade.
- **Bugs:** Corrigido erro no botão "Compartilhar" que ignorava o ID da sala.
- **Bugs:** Corrigida reconexão automática do WebSocket que falhava após a última atualização.

---

## [0.6.0] - 2026-02-28

### Adicionado
- **Interface:** Sistema de Tema Claro/Escuro com detecção automática do sistema e alternância manual via botão.
- **Persistência:** O navegador agora lembra o último nome usado e a preferência de tema (`localStorage`).
- **Design:** Ajustes de contraste e cores para garantir acessibilidade e beleza tanto no tema claro quanto no escuro.

---

## [0.5.3] - 2026-02-28

### Adicionado
- **Interface:** Adicionado rodapé com créditos e links (GitHub e site pessoal) nas telas Home e Sala.

---

## [0.5.2] - 2026-02-28

### Adicionado
- **Licença:** Adicionado arquivo `LICENSE` (MIT) e cabeçalhos de licença nos arquivos principais.
- **Autor:** Atualizado nome e e-mail do autor para consistência em todo o projeto.

---

## [0.5.1] - 2026-02-28

### Corrigido
- **Segurança:** Atualizada a validação de nome de usuário para aceitar caracteres acentuados (ex: "João", "André").

---

## [0.5.0] - 2026-02-28

### Adicionado
- **CI/CD:** Workflow `.github/workflows/deploy-frontend.yml` para deploy automático via FTP para Hostinger
- **CI/CD:** Suporte a segredo `FTP_SERVER_DIR` para configurar diretório de destino no servidor

### Corrigido
- **Deploy:** Suporte a subpastas (ex: `/planningpoker/`) via `base` no `vite.config.js` e `.htaccess` atualizado
- **Deploy:** Geração do link de convite em `RoomView.vue` agora inclui corretamente a subpasta
- **Deploy:** Comandos do `render.yaml` e README ajustados para funcionar a partir da raiz do repositório no Render.com

---

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
