# Hermes v0.4-beta Pixel Office Vivo Implementation Plan

> **For Hermes:** implementar somente após autorização explícita de Favini. Não alterar schema/seed salvo correção mínima indispensável; manter SQLite, endpoints e dados atuais.

**Goal:** transformar a tela atual de dashboard com salas abstratas em um Pixel Office vivo/top-down, com salas mobiliadas, agentes maiores, balões de estado, cliques contextuais e status bar operacional.

**Architecture:** patch incremental sobre `hermes-visual/web/`. Backend e SQLite permanecem como estão. O frontend passa a criar uma planta visual mais rica usando CSS puro e os dados já retornados por `/api/rooms`, `/api/agents`, `/api/tasks`, `/api/decisions`, `/api/alerts` e `/api/cycle`.

**Tech Stack:** HTML/CSS/JS puro, Python stdlib server existente, SQLite existente.

---

## Current Context

Arquivos atuais inspecionados:

- `web/index.html`: já contém sidebar, header, badge, `#office-map`, painéis e status bar simples.
- `web/styles.css`: já tem grid de salas e avatares, mas ainda parece card/dashboard.
- `web/app.js`: já carrega APIs, renderiza salas/agentes/tarefas/decisões/alertas e roda ciclo.

Servidor/API/SQLite não precisam mudar para esta etapa.

---

## Files Likely to Change

### Modify

- `C:\Users\cefav\Documents\My Web Sites\Site\hermes-visual\web\index.html`
- `C:\Users\cefav\Documents\My Web Sites\Site\hermes-visual\web\styles.css`
- `C:\Users\cefav\Documents\My Web Sites\Site\hermes-visual\web\app.js`
- `C:\Users\cefav\Documents\My Web Sites\Site\hermes-visual\README.md` apenas se Favini quiser registrar v0.4-beta.

### Do not modify

- `db/schema.sql`
- `db/seeds/001_initial_seed.sql`
- `db/private/hermes_v04.sqlite`
- `app/server.py`
- `docs/DATA_POLICY.md`

---

## Proposed Approach

1. Trocar a leitura visual do mapa: de “rooms como cards” para “floorplan top-down”.
2. Adicionar móveis CSS gerados dinamicamente por tipo de sala.
3. Dar aos agentes aparência de mini-personagens corporativos em pixel, maiores e com estado.
4. Posicionar agentes em coordenadas internas da sala, não apenas flex-bottom.
5. Adicionar balão curto acima do agente.
6. Adicionar animações por estado real do agente.
7. Implementar seleção de agente e sala no frontend.
8. Usar clique na sala para filtrar tarefas no `TaskPanel`.
9. Reforçar status bar inferior com resumo operacional real.
10. Manter backend e DB intactos.

---

## Step-by-Step Plan

### Task 1: Update HTML structure for living office

**Objective:** criar alvos de UI para ficha lateral, filtro de sala e status operacional robusto.

**Files:**
- Modify: `web/index.html`

**Changes:**

- Em `.right-panels`, adicionar painel:

```html
<section class="panel agent-inspector-panel">
  <div class="panel-title-row">
    <h3>Ficha do Agente</h3>
    <span id="selected-agent-tag" class="panel-tag">nenhum</span>
  </div>
  <div id="agent-inspector" class="agent-inspector empty">
    Clique em um agente no escritório.
  </div>
</section>
```

- No painel de tarefas, adicionar indicador de filtro:

```html
<span id="task-filter-tag" class="panel-tag">todas as salas</span>
```

- Substituir status bar simples por itens com IDs:

```html
<footer class="status-bar live-status-bar">
  <span>Hermes v0.4-beta</span>
  <span id="cycle-status">Ciclo: ainda não rodado</span>
  <span id="critical-company-status">Empresa crítica: n/d</span>
  <span id="p0-task-status">P0: n/d</span>
  <span id="pending-decisions-status">Decisões: 0</span>
  <span id="open-alerts-status">Alertas: 0</span>
</footer>
```

---

### Task 2: Convert office map into true top-down floorplan

**Objective:** fazer o mapa parecer planta de escritório, não cards.

**Files:**
- Modify: `web/styles.css`

**CSS direction:**

```css
.office-map {
  grid-template-columns: repeat(12, minmax(56px, 1fr));
  grid-template-rows: repeat(9, 76px);
  gap: 0;
  padding: 18px;
  min-height: 720px;
  border: 4px solid #36556a;
  background:
    linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px),
    linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
    repeating-linear-gradient(45deg, rgba(214,173,96,.05) 0 6px, transparent 6px 12px),
    #0b1722;
  background-size: 32px 32px, 32px 32px, 18px 18px, 100% 100%;
}

.room {
  margin: -1px;
  border-radius: 0;
  border: 4px solid #486a7e;
  min-height: 120px;
  overflow: visible;
  background: var(--floor-texture);
}
```

---

### Task 3: Add CSS furniture primitives

**Objective:** criar móveis visuais sem assets externos.

**Files:**
- Modify: `web/styles.css`
- Modify: `web/app.js`

**CSS primitives:**

```css
.furniture { position:absolute; border:2px solid rgba(255,255,255,.18); box-shadow: inset 0 0 0 2px rgba(0,0,0,.25); }
.desk { width:52px; height:28px; background:#6b4a2e; border-radius:4px; }
.table-round { width:70px; height:46px; background:#263c4d; border-radius:50%; }
.server-rack { width:30px; height:58px; background:linear-gradient(#101820,#23384a); }
.vault-core { width:64px; height:64px; border-radius:50%; background:radial-gradient(circle,#6b4cff,#120821); }
.bookshelf { width:30px; height:72px; background:repeating-linear-gradient(0deg,#7a4b2b 0 8px,#d6ad60 8px 10px); }
.radar-dish { width:62px; height:38px; border-radius:50% 50% 8px 8px; background:#0e5360; }
.sofa { width:80px; height:34px; background:#294052; border-radius:12px; }
```

**JS mapping:**

```js
const furnitureByRoomType = {
  executive: ['desk','chair','plant'],
  meeting: ['table-round','chair','chair','screen'],
  server_vault: ['server-rack','server-rack','vault-core'],
  compliance: ['war-table','alert-screen'],
  incubation: ['desk','whiteboard'],
  library: ['bookshelf','bookshelf','reading-table'],
  radar: ['radar-dish','signal-screen'],
  lab: ['workbench','server-rack'],
  lounge: ['sofa','coffee-table']
};
```

---

### Task 4: Render bigger living agents inside rooms

**Objective:** avatares maiores, legíveis, posicionados fisicamente.

**Files:**
- Modify: `web/styles.css`
- Modify: `web/app.js`

**CSS direction:**

```css
.agent-token {
  position: absolute;
  width: 44px;
  height: 52px;
  border-radius: 14px 14px 10px 10px;
  font-size: 18px;
  z-index: 5;
}
.agent-token::after {
  content: attr(data-name);
  position:absolute;
  left:50%; top:54px;
  transform:translateX(-50%);
  white-space:nowrap;
  font-size:10px;
  color:#eaf6ff;
}
.agent-bubble {
  position:absolute;
  left:50%; bottom:56px;
  transform:translateX(-50%);
  font-size:10px;
  padding:4px 7px;
  border-radius:999px;
  background:rgba(4,8,13,.92);
  border:1px solid rgba(255,255,255,.18);
}
```

**JS positioning:**

```js
function agentPosition(index, total) {
  const positions = [
    [18, 62], [42, 58], [66, 64], [28, 38], [58, 36], [78, 42]
  ];
  return positions[index % positions.length];
}
```

---

### Task 5: Add state animation classes

**Objective:** estado operacional visível no personagem.

**Files:**
- Modify: `web/styles.css`
- Modify: `web/app.js`

**Classes:**

```css
.agent-idle { animation: idleBreath 2.4s infinite; }
.agent-working { animation: workBob 1.2s infinite; }
.agent-auditing { animation: auditScan 1.7s infinite; }
.agent-blocked { filter: grayscale(.5); box-shadow: 0 0 0 3px var(--red); }
.agent-waiting { animation: waitingPulse 2s infinite; }
.agent-quarantine { animation: quarantineGlow 1.6s infinite; }
```

**State mapping in JS:**

```js
function stateClass(agent) {
  const s = agent.state || '';
  if (agent.is_blocked) return 'agent-blocked';
  if (s.includes('quarentena')) return 'agent-quarantine';
  if (s.includes('aguardando')) return 'agent-waiting';
  if (s.includes('auditando') || s.includes('red_team')) return 'agent-auditing';
  if (s.includes('trabalhando')) return 'agent-working';
  return 'agent-idle';
}
```

---

### Task 6: Add click agent inspector

**Objective:** clique no agente abre ficha lateral curta.

**Files:**
- Modify: `web/app.js`
- Modify: `web/styles.css`

**JS:**

```js
function selectAgent(agentId) {
  state.selectedAgentId = agentId;
  const agent = state.agents.find(a => a.id === agentId);
  const box = $('#agent-inspector');
  $('#selected-agent-tag').textContent = agent ? agent.name : 'nenhum';
  box.classList.remove('empty');
  box.innerHTML = agent ? `
    <div class="inspector-avatar" style="--agent-color:${agent.visual_color}">${escapeHtml(agent.avatar_symbol)}</div>
    <strong>${escapeHtml(agent.name)}</strong>
    <p>${escapeHtml(agent.role)}</p>
    <small>Estado: ${escapeHtml(agent.state)} · Sala: ${escapeHtml(agent.room_name || 'n/d')}</small>
    <small>Acesso: ${escapeHtml(agent.data_access_level)} · XP: ${agent.xp}</small>
  ` : 'Clique em um agente.';
  renderOffice();
}
```

---

### Task 7: Add click room task filter

**Objective:** clique na sala filtra tarefas do painel.

**Files:**
- Modify: `web/app.js`

**JS:**

```js
function selectRoom(roomId) {
  state.selectedRoomId = state.selectedRoomId === roomId ? null : roomId;
  const room = state.rooms.find(r => r.id === state.selectedRoomId);
  $('#task-filter-tag').textContent = room ? room.name : 'todas as salas';
  renderOffice();
  renderTasks();
}
```

`renderTasks()` passa a usar:

```js
const tasks = state.selectedRoomId
  ? state.tasks.filter(t => t.room_id === state.selectedRoomId)
  : state.tasks;
```

---

### Task 8: Status bar operational summary

**Objective:** status inferior precisa resumir o sistema vivo.

**Files:**
- Modify: `web/app.js`
- Modify: `web/index.html`

**JS:**

```js
function renderStatusBar() {
  const p0 = state.tasks.find(t => t.priority === 'P0');
  const critical = state.lastCycle?.critical_company || state.companies[0];
  $('#critical-company-status').textContent = `Empresa crítica: ${critical?.name || 'n/d'}`;
  $('#p0-task-status').textContent = `P0: ${p0?.title || 'n/d'}`;
  $('#pending-decisions-status').textContent = `Decisões: ${state.decisions.filter(d => d.status === 'pending').length}`;
  $('#open-alerts-status').textContent = `Alertas: ${state.alerts.filter(a => a.status === 'open').length}`;
}
```

---

### Task 9: Preserve cycle behavior but make it visible

**Objective:** quando rodar ciclo, mover atenção visual para empresa/sala/agente críticos.

**Files:**
- Modify: `web/app.js`
- Modify: `web/styles.css`

**Behavior:**

- `runCycle()` mantém `POST /api/cycle`.
- Depois de resposta:
  - `state.lastCycle = data.cycle`;
  - destaca `critical_company` e `critical_task.room_id`;
  - seleciona `blocked_agent` automaticamente;
  - atualiza status bar;
  - toast com diagnóstico.

---

## Risks

1. **Risco de virar brinquedo:** mitigação: manter paleta executiva e labels de segurança.
2. **Risco de virar dashboard novamente:** mitigação: salas com móveis e agentes posicionados fisicamente no mapa.
3. **Risco de complexidade visual excessiva:** mitigação: CSS puro, sem assets pesados, sem canvas, sem biblioteca.
4. **Risco de quebrar APIs existentes:** mitigação: não alterar backend nem schema.
5. **Risco de texto ilegível:** mitigação: avatares maiores, nomes curtos e inspector lateral.
6. **Risco de mobile ruim:** aceitável nesta fase; prioridade é desktop local.

---

## Validation Commands

Run from:

```bash
cd '/c/Users/cefav/Documents/My Web Sites/Site/hermes-visual'
```

Check syntax:

```bash
node --check web/app.js
python3 -m py_compile app/server.py scripts/init_db.py scripts/backup_db.py
```

Check HTTP/API:

```bash
python3 app/server.py
```

Open:

```text
http://127.0.0.1:8040/
```

Manual visual validation:

- escritório parece planta top-down;
- salas têm móveis;
- agentes parecem personagens, não bolinhas;
- balões de estado aparecem;
- clique no agente abre ficha;
- clique na sala filtra tarefas;
- Ciclo Hermes destaca COS/tarefa/alerta;
- status bar mostra ciclo, P0, empresa crítica, decisões e alertas.

---

## Acceptance Criteria

Favini abre a tela e em 10 segundos percebe:

- existe um escritório top-down;
- as salas têm função visual clara;
- há agentes fisicamente dentro das salas;
- os agentes parecem vivos por estado/animação;
- COS/risco aparece com tensão visual;
- Cofre S4 parece cofre/server room, não card;
- o clique em agente/sala responde;
- status bar resume a operação;
- continua tudo local/simulado/sem pessoa jurídica/sem ação externa.

---

## Recommendation

Implementar como **v0.4-beta visual patch**, alterando apenas `web/index.html`, `web/styles.css` e `web/app.js`, com README opcional. Não tocar no banco nem no backend.
