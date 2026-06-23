/* ════════ ARCONTE SUPREMO — Living Command Office v0.4.4 (vanilla, no CDN) ════════ */
"use strict";

const world = {
  rooms: [], agents: [], tasks: [], decisions: [], alerts: [],
  source: "seed",                 // seed | partial | api
  identity: null,
  knowledge: { sources: 0, claims: 0, byAgent: {} },
  sim: { playing: true, speed: 1, mode: null, showNames: false, plan: false, demo: false },
  selected: { type: null, key: null, id: null },
};

const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));

/* ── Almas dos 12 agentes (preservadas) ── */
const SOULS = {
  1:{name:"Arconte Supremo",role:"coordenador, sintetizador e guardião do foco",mission:"manter o foco de Favini e sintetizar o Conselho",question:"Isso avança a decisão de Favini ou cria ruído?",controls:"dispersão de energia e confusão entre simulação e realidade",ritual:"revisar prioridades; checar bloqueios; atualizar o Conselho"},
  2:{name:"Auditor Zero",role:"evidência, integridade e anti-teatro",mission:"exigir prova antes de qualquer 'sucesso'",question:"Onde está a prova?",controls:"ilusão de progresso e métrica vazia",ritual:"checar fontes, métricas e versões"},
  3:{name:"Cerberus",role:"fronteira, acesso e proteção de dado sensível",mission:"guardar o Cofre Genoma e as fronteiras",question:"Esta ação respeita a fronteira permitida?",controls:"exposição indevida e breach conceitual",ritual:"inspecionar acessos; confirmar permissões"},
  4:{name:"Cassandra",role:"radar de risco e sinais fracos",mission:"antecipar o pior cenário plausível",question:"Qual é o pior cenário plausível?",controls:"silêncio antes do incidente e otimismo cego",ritual:"varrer sinais fracos; atualizar cenários"},
  5:{name:"Chronos",role:"tempo, cadência e ritmo sustentável",mission:"proteger o ritmo e revelar atrasos invisíveis",question:"O que está atrasado sem ninguém perceber?",controls:"velocidade imprudente e ilusão de prazo",ritual:"revisar prazos; sinalizar atraso invisível"},
  6:{name:"Sophia",role:"curadoria, síntese e contexto mínimo",mission:"entregar o contexto mínimo que Favini precisa",question:"Qual é a informação mínima necessária agora?",controls:"conhecimento como decoração",ritual:"revisar fontes; limitar ruído; atualizar índice"},
  7:{name:"Nomos",role:"regras, mandato, alçada e governança interna",mission:"manter ações dentro do mandato",question:"Esta ação está dentro do mandato?",controls:"poder sem mandato",ritual:"checar mandatos; atualizar regras"},
  8:{name:"Themis",role:"equilíbrio decisório e arbitragem de conflito",mission:"achar o meio-termo que preserva o objetivo",question:"Qual é o meio-termo que preserva o objetivo?",controls:"abuso de maioria e ruído no Conselho",ritual:"checar tensões; registrar fricções"},
  9:{name:"Atlas",role:"execução, dependências e entrega",mission:"destravar o que impede a entrega",question:"O que está parado e impede a entrega?",controls:"execução como teatro e heroísmo sem base",ritual:"revisar backlog; limpar dependência"},
  10:{name:"Midas",role:"valor, custo de oportunidade e patrimônio",mission:"separar valor real de mero movimento",question:"Isso gera valor ou só movimento?",controls:"crescimento a qualquer custo e métrica vaidosa",ritual:"checar retorno; propor corte/foco"},
  11:{name:"Daedalus",role:"arquitetura, construção e prototipação",mission:"saber o que está sendo construído de fato",question:"O que estamos construindo realmente?",controls:"arquitetura sem produto e forma sem função",ritual:"revisar arquitetura; atualizar hipóteses"},
  12:{name:"Argos",role:"vigilância operacional e saúde sistêmica",mission:"distinguir saúde real de aparência de normalidade",question:"O sistema está saudável ou só aparenta?",controls:"operação cega e dashboard sem vida",ritual:"checar saúde; revisar alertas"},
};

const PALETTE = {1:"#bf9233",2:"#2f9e6e",3:"#6e54e6",4:"#d8483f",5:"#3f73c9",6:"#1ea391",7:"#d98a1f",8:"#c65a86",9:"#2f9e6e",10:"#bf9233",11:"#3f73c9",12:"#1ea391"};
const SYMBOL  = {1:"Ω",2:"0",3:"C",4:"!",5:"T",6:"S",7:"§",8:"=",9:"A",10:"$",11:"D",12:"@"};
const SEED_HOME = {1:"council",2:"library",3:"vault",4:"radar",5:"work",6:"library",7:"war",8:"council",9:"work",10:"founder",11:"lab",12:"vault"};
const SEED_STATE = {1:"trabalhando",2:"auditando",3:"quarentena",4:"aguardando_favini",5:"trabalhando",6:"lendo",7:"trabalhando",8:"idle",9:"trabalhando",10:"idle",11:"trabalhando",12:"trabalhando"};
const PREF = {
  1:["council","founder"],2:["library","lab","war"],3:["vault","war"],4:["radar","war"],
  5:["council","work"],6:["library","council"],7:["war","council"],8:["council","lounge"],
  9:["work","incubation","lab"],10:["founder","council"],11:["lab","sandbox","incubation","work"],12:["vault","radar"],
};

/* ── 12 salas canônicas (ambientes habitáveis) ── */
const CANONICAL_ROOMS = [
  {key:"founder",name:"Founder’s Office",sub:"Favini · decisão final",type:"founder",apiType:"executive",accent:"var(--gold)",col:1,w:3,row:1,h:3,
   fur:[{k:"f-rug",x:52,y:58},{k:"f-deskL",x:60,y:50},{k:"f-chair",x:60,y:70},{k:"f-plant",x:85,y:26}]},
  {key:"council",name:"Conselho do Arconte",sub:"Governança viva",type:"council",apiType:"meeting",accent:"var(--violet)",col:4,w:4,row:1,h:3,
   fur:[{k:"f-round",x:50,y:54},{k:"f-chair",x:32,y:50},{k:"f-chair",x:68,y:50},{k:"f-chair",x:32,y:70},{k:"f-chair",x:68,y:70},{k:"f-screen",x:85,y:24}]},
  {key:"radar",name:"Radar Mundial",sub:"Sinais & cenários",type:"radar",apiType:"radar",accent:"var(--blue)",col:8,w:2,row:1,h:3,
   fur:[{k:"f-radar",x:50,y:52},{k:"f-screen",x:80,y:26}]},
  {key:"library",name:"Biblioteca dos Originais",sub:"O Genoma Digital",type:"library",apiType:"library",accent:"var(--green)",col:10,w:3,row:1,h:3,
   fur:[{k:"f-shelf",x:16,y:48},{k:"f-shelf",x:26,y:48},{k:"f-shelf",x:36,y:48},{k:"f-readtable",x:68,y:58}]},
  {key:"work",name:"Work Room",sub:"Aitherion",type:"work",apiType:"work",accent:"var(--teal)",col:1,w:3,row:4,h:2,
   fur:[{k:"f-desk",x:34,y:52},{k:"f-desk",x:66,y:52},{k:"f-monitorrow",x:50,y:30}]},
  {key:"lab",name:"Laboratório",sub:"Vantion / LUNA",type:"lab",apiType:"lab",accent:"var(--teal)",col:4,w:2,row:4,h:2,
   fur:[{k:"f-bench",x:50,y:56},{k:"f-beaker",x:30,y:40},{k:"f-beaker",x:40,y:40},{k:"f-screen",x:78,y:30}]},
  {key:"incubation",name:"Incubação",sub:"Novas hipóteses",type:"incubation",apiType:"incubation",accent:"var(--green)",col:6,w:2,row:4,h:2,
   fur:[{k:"f-pod",x:36,y:56},{k:"f-pod",x:58,y:56},{k:"f-whiteboard",x:80,y:28}]},
  {key:"war",name:"War Room",sub:"COS Virtual · regulado",type:"war",apiType:"compliance",accent:"var(--red)",col:8,w:2,row:4,h:2,regulated:true,
   fur:[{k:"f-wartable",x:50,y:54},{k:"f-redscreen",x:80,y:26},{k:"f-redscreen",x:22,y:26}]},
  {key:"sandbox",name:"Sandbox de Novas Empresas",sub:"Protótipos",type:"sandbox",apiType:"sandbox",accent:"var(--amber)",col:10,w:3,row:4,h:2,
   fur:[{k:"f-blocks",x:38,y:52},{k:"f-whiteboard",x:74,y:30},{k:"f-pod",x:60,y:60}]},
  {key:"vault",name:"Server Room / Cofre Digital",sub:"Cofre Genoma · quarentena",type:"vault",apiType:"server_vault",accent:"var(--violet)",col:1,w:3,row:6,h:3,quarantine:true,
   fur:[{k:"f-rack",x:24,y:42},{k:"f-rack",x:36,y:42},{k:"f-vault",x:68,y:56}]},
  {key:"lounge",name:"Lounge",sub:"Status & pausa",type:"lounge",apiType:"lounge",accent:"var(--rose)",col:4,w:4,row:6,h:3,
   fur:[{k:"f-sofa",x:38,y:58},{k:"f-coffee",x:66,y:58},{k:"f-plant",x:86,y:28}]},
  {key:"redteam",name:"Red Team",sub:"Adversarial interno",type:"redteam",apiType:null,accent:"var(--red)",col:8,w:2,row:6,h:3,regulated:true,
   fur:[{k:"f-desk",x:40,y:54},{k:"f-redscreen",x:40,y:32},{k:"f-redscreen",x:66,y:44}]},
];

const MODES = {
  product:{label:"Produto/MVP",rooms:["work","lab","incubation","sandbox"],agents:[6,9,11]},
  redteam:{label:"Red Team",rooms:["redteam","war","vault"],agents:[2,3,4,12]},
  council:{label:"Conselho",rooms:["council","founder"],agents:[1,8,10,5]},
  risk:{label:"Risco",rooms:["war","redteam","radar","vault"],agents:[4,3,2,12]},
};

const MOOD = {
  trabalhando:{label:"focado",color:"var(--green)"},
  lendo:{label:"curioso",color:"var(--teal)"},
  auditando:{label:"cético",color:"var(--amber)"},
  aguardando:{label:"em espera",color:"var(--amber)"},
  quarentena:{label:"contido",color:"var(--violet)"},
  red_team:{label:"adversarial",color:"var(--red)"},
  idle:{label:"observando",color:"var(--blue)"},
};
function moodFor(stateStr){
  const s=String(stateStr||"idle");
  if(s.includes("aguardando"))return MOOD.aguardando;
  if(s.includes("quarentena"))return MOOD.quarentena;
  if(s.includes("auditando"))return MOOD.auditando;
  if(s.includes("red_team"))return MOOD.red_team;
  if(s.includes("lendo"))return MOOD.lendo;
  if(s.includes("trabalhando"))return MOOD.trabalhando;
  return MOOD.idle;
}

/* ════════ CAMADA DE DADOS (API local defensiva + adaptadores) ════════ */
async function apiGet(path){
  const res = await fetch(path, {headers:{"Content-Type":"application/json"}});
  const data = await res.json();
  if(!res.ok || data.ok===false) throw new Error(data.error||("falha "+path));
  return data;
}

async function fetchWorld(){
  const endpoints = {
    identity:"/api/_debug/identity", companies:"/api/companies", rooms:"/api/rooms",
    agents:"/api/agents", tasks:"/api/tasks", decisions:"/api/decisions", alerts:"/api/alerts",
    sources:"/api/knowledge/sources", claims:"/api/knowledge/claims",
  };
  const keys = Object.keys(endpoints);
  const settled = await Promise.allSettled(keys.map(k=>apiGet(endpoints[k])));
  const out={};
  settled.forEach((r,i)=>{ out[keys[i]] = r.status==="fulfilled" ? r.value : null; });
  return out;
}

// Mapeia status livres do banco para classes visuais.
function statusClass(raw){
  const s=String(raw||"normal").toLowerCase();
  if(s.includes("crit")||s.includes("crít"))return "critico";
  if(s.includes("bloq")||s.includes("block"))return "bloqueado";
  if(s.includes("quar"))return "bloqueado";
  if(s.includes("aten"))return "atencao";
  if(s.includes("ativ")||s.includes("activ"))return "ativo";
  return "normal";
}

// Constrói o mundo canônico, sobrepondo dados da API quando existirem.
function buildWorld(api){
  const apiRooms = Array.isArray(api?.rooms?.rooms) ? api.rooms.rooms.slice() : [];
  const usedApi = new Set();
  const apiIdToKey = {};

  world.rooms = CANONICAL_ROOMS.map((c)=>{
    let match=null;
    if(c.apiType){
      match = apiRooms.find(r=>r && r.room_type===c.apiType && !usedApi.has(r.id));
      if(match) usedApi.add(match.id);
    }
    const status = match ? statusClass(match.status) : (c.quarantine?"bloqueado":c.regulated?"atencao":"normal");
    const room = {
      ...c,
      apiId: match?match.id:null,
      status,
      rawStatus: match?match.status:(c.quarantine?"quarentena":c.regulated?"regulado":"operacional"),
      security: match?match.security_level:(c.quarantine?"S4":c.regulated?"S3":"S1"),
      company: match?(match.company_name||c.sub):c.sub,
      accent: c.accent,
      is_quarantine: c.quarantine ? 1 : (match?match.is_quarantine:0),
      source: match ? "api" : "seed",
    };
    if(match) apiIdToKey[match.id]=c.key;
    return room;
  });

  // AGENTES
  const apiAgents = Array.isArray(api?.agents?.agents) ? api.agents.agents : null;
  if(apiAgents && apiAgents.length){
    world.agents = apiAgents.map((a)=>{
      const id = a.id;
      const soul = SOULS[id] || {name:a.name||("Agente "+id),role:a.role||"função operacional",mission:"operar dentro do mandato",controls:"ruído operacional",ritual:"revisar estado"};
      const homeKey = apiIdToKey[a.current_room_id] || SEED_HOME[id] || "council";
      return {
        id, name:a.name||soul.name, role:a.role||soul.role,
        symbol:a.avatar_symbol||SYMBOL[id]||"•", color:a.visual_color||PALETTE[id]||"#3f73c9",
        state:a.state||SEED_STATE[id]||"idle", is_blocked:a.is_blocked?1:0,
        can_block:a.can_block?1:0, homeKey, source:"api",
      };
    });
  } else {
    world.agents = Object.keys(SOULS).map((k)=>{
      const id=+k;
      return { id, name:SOULS[id].name, role:SOULS[id].role, symbol:SYMBOL[id], color:PALETTE[id],
        state:SEED_STATE[id], is_blocked: SEED_STATE[id].includes("aguardando")?1:0,
        can_block:[1,2,3,4,7].includes(id)?1:0, homeKey:SEED_HOME[id], source:"seed" };
    });
  }

  // TASKS / DECISIONS / ALERTS (defensivos)
  const apiTasks = Array.isArray(api?.tasks?.tasks) ? api.tasks.tasks : null;
  world.tasks = (apiTasks || SEED.tasks).map((t)=>({
    id:t.id, title:t.title||"(tarefa)", priority:(t.priority||"P2"), status:t.status||"pending",
    company_name:t.company_name||"", agent_name:t.agent_name||"", roomKey: apiIdToKey[t.room_id] || t.roomKey || null,
    source: apiTasks ? "api":"seed",
  }));

  const apiDec = Array.isArray(api?.decisions?.decisions) ? api.decisions.decisions : null;
  world.decisions = (apiDec || SEED.decisions).map((d)=>({
    id:d.id, code:d.decision_code||("DEC-"+d.id), title:d.title||"(decisão)",
    priority:d.priority||"P1", status:d.status||"pending", required_by:d.required_by||"Favini",
    source: apiDec ? "api":"seed",
  }));

  const apiAlerts = Array.isArray(api?.alerts?.alerts) ? api.alerts.alerts : null;
  world.alerts = (apiAlerts || SEED.alerts).map((a)=>({
    id:a.id, title:a.title||"(alerta)", severity:a.severity??3, message:a.message||"",
    company_name:a.company_name||"sistema", status:a.status||"open", agent_id:a.agent_id||null,
    blocks_progress:a.blocks_progress?1:0, source: apiAlerts ? "api":"seed",
  }));

  // CONHECIMENTO
  world.knowledge.sources = Array.isArray(api?.sources?.sources) ? api.sources.sources.length : 0;
  world.knowledge.claims  = Array.isArray(api?.claims?.claims)  ? api.claims.claims.length  : 0;
  world.identity = api?.identity || null;

  // FONTE GLOBAL
  const hasRooms = apiRooms.length>0, hasAgents = !!(apiAgents&&apiAgents.length);
  world.source = (hasRooms && hasAgents) ? "api" : (api?.identity||hasRooms||hasAgents ? "partial" : "seed");
}

/* ── Seed visual local (secundário) ── */
const SEED = {
  tasks:[
    {id:1,title:"Estabilizar seed-round LUNA/Vantion",priority:"P0",status:"blocked",company_name:"Aitherion",agent_name:"Atlas",roomKey:"war"},
    {id:2,title:"Validar evidências do ciclo",priority:"P1",status:"in_progress",company_name:"Aitherion",agent_name:"Auditor Zero",roomKey:"library"},
    {id:3,title:"Protótipo office-live",priority:"P1",status:"in_progress",company_name:"Aitherion",agent_name:"Daedalus",roomKey:"lab"},
    {id:4,title:"Varredura de sinais fracos",priority:"P2",status:"pending",company_name:"Aitherion",agent_name:"Cassandra",roomKey:"radar"},
    {id:5,title:"Curar Biblioteca dos Originais",priority:"P2",status:"in_progress",company_name:"Aitherion",agent_name:"Sophia",roomKey:"library"},
  ],
  decisions:[
    {id:1,decision_code:"DEC-001",title:"Aprovar quarentena do Cofre Genoma",priority:"P0",status:"pending",required_by:"Favini"},
    {id:2,decision_code:"DEC-002",title:"Liberar foco Produto/MVP",priority:"P1",status:"pending",required_by:"Favini"},
    {id:3,decision_code:"DEC-003",title:"Mandato do COS Virtual",priority:"P1",status:"pending",required_by:"Favini"},
  ],
  alerts:[
    {id:1,title:"Risco existencial sem mitigação",severity:4,message:"Cenário pior caso não coberto",company_name:"Aitherion",status:"open",agent_id:4,blocks_progress:1},
    {id:2,title:"Acesso sensível em revisão",severity:3,message:"Cofre Genoma em quarentena",company_name:"Aitherion",status:"open",agent_id:3,blocks_progress:1},
  ],
};

/* ════════ BOOT + RENDER DO MUNDO ════════ */
async function boot(){
  bindHud();
  setConn("waiting","conectando ao SQLite local…");
  let api={};
  try { api = await fetchWorld(); } catch(_) { api={}; }
  buildWorld(api);
  renderConn();
  renderFloor();
  syncSim();
  renderConsole();
  renderInspectorWelcome();
  renderWorldStats();
}

function setConn(kind,text){
  const pill=$("#conn-pill"); pill.className="conn-pill "+kind;
  $("#conn-text").textContent=text;
}
function renderConn(){
  if(world.source==="api"){
    const v=world.identity?.version?(" · "+world.identity.version):"";
    setConn("live","SQLite local · API local"+v);
  } else if(world.source==="partial"){
    setConn("partial","modo visual local · API parcial (SQLite pendente)");
  } else {
    setConn("waiting","modo visual local · API aguardando (SQLite pendente)");
  }
}
function renderWorldStats(){
  const blocked=world.rooms.filter(r=>r.is_quarantine||r.status==="bloqueado").length;
  const fromApi=world.rooms.filter(r=>r.source==="api").length;
  $("#world-stats").textContent=`${world.rooms.length} salas · ${world.agents.length} agentes vivos · ${blocked} em quarentena/bloqueio · ${fromApi}/${world.rooms.length} salas via API`;
}

function roomByKey(key){ return world.rooms.find(r=>r.key===key)||null; }
function agentById(id){ return world.agents.find(a=>a.id===id)||null; }

function renderFloor(){
  const floor=$("#floor");
  floor.classList.toggle("blueprint", world.sim.plan);
  // preserva camada de agentes
  floor.innerHTML="";
  world.rooms.forEach((room)=>{
    const occ = world.agents.filter(a=>a.homeKey===room.key).length;
    const el=document.createElement("article");
    el.className=["room","st-"+room.status,room.quarantine?"quarantine":"",room.regulated?"regulated":"",
      world.selected.type==="room"&&world.selected.key===room.key?"selected":""].filter(Boolean).join(" ");
    el.dataset.key=room.key;
    el.style.gridColumn=`${room.col} / span ${room.w}`;
    el.style.gridRow=`${room.row} / span ${room.h}`;
    el.style.setProperty("--accent",room.accent);
    el.addEventListener("click",()=>selectRoom(room.key));
    el.innerHTML=`
      <div class="furniture-layer">${room.fur.map(f=>`<span class="furniture ${f.k}" style="--fx:${f.x}%;--fy:${f.y}%${f.rot?`;--rot:${f.rot}deg`:""}"></span>`).join("")}</div>
      ${room.quarantine?`<div class="vault-lock"><div class="lock-badge"><div class="lock-ring"></div>COFRE PROTEGIDO<br>CONTEÚDO OCULTO</div></div>`:""}
      <div class="room-tag"><span class="rt-name">${esc(room.name)}</span><span class="rt-sub">${esc(room.company||room.sub)} · ${esc(room.security||"")}</span></div>
      <div class="room-foot">
        <span class="room-state"><span class="sdot"></span>${esc(room.rawStatus||room.status)}</span>
        <span class="room-occ">👤 ${occ}</span>
      </div>`;
    floor.appendChild(el);
  });
}

/* ════════ MOTOR DE VIDA (avatares) ════════ */
const sims=new Map(), avEls=new Map(), rects=new Map();
let raf=null, lastTs=0;

function layer(){ return $("#agents"); }
function measure(){
  const lr=layer().getBoundingClientRect();
  rects.clear();
  $$("#floor .room").forEach(el=>{
    const r=el.getBoundingClientRect();
    rects.set(el.dataset.key,{x:r.left-lr.left,y:r.top-lr.top,w:r.width,h:r.height});
  });
}
function ptIn(key){
  const r=rects.get(key); if(!r) return null;
  const pad=26;
  return {x:r.x+pad+Math.random()*Math.max(8,r.w-pad*2), y:r.y+r.h*0.42+Math.random()*Math.max(8,r.h*0.42)};
}
function centerOf(key){ const r=rects.get(key); return r?{x:r.x+r.w/2,y:r.y+r.h*0.55}:null; }

function syncSim(){
  requestAnimationFrame(()=>{
    measure(); seedSims(); renderAvatars();
    if(world.sim.playing) start();
  });
}
function seedSims(){
  const ids=new Set();
  world.agents.forEach(a=>{
    ids.add(a.id);
    const home=rects.has(a.homeKey)?a.homeKey:(world.rooms[0]&&world.rooms[0].key);
    if(!sims.has(a.id)){
      const p=ptIn(home)||{x:80,y:80};
      sims.set(a.id,{id:a.id,x:p.x,y:p.y,tx:p.x,ty:p.y,speed:50+Math.random()*30,moving:false,
        dwell:performance.now()+Math.random()*1600,cur:home,dest:home,face:1});
    } else {
      const s=sims.get(a.id);
      if(!rects.has(s.cur)){ const p=ptIn(home)||{x:80,y:80}; Object.assign(s,{x:p.x,y:p.y,tx:p.x,ty:p.y,cur:home,dest:home}); }
    }
  });
  [...sims.keys()].forEach(id=>{ if(!ids.has(id)){ avEls.get(id)?.remove(); avEls.delete(id); sims.delete(id);} });
}
function roomsForMode(){ const m=world.sim.mode&&MODES[world.sim.mode]; return m?m.rooms.filter(k=>rects.has(k)):[]; }
function agentInMode(id){ const m=world.sim.mode&&MODES[world.sim.mode]; return m?m.agents.includes(id):false; }

function chooseDest(sim){
  const a=agentById(sim.id); if(!a) return;
  const home=rects.has(a.homeKey)?a.homeKey:(world.rooms[0]&&world.rooms[0].key);
  let pool=[];
  if(world.sim.mode && agentInMode(sim.id)){ pool=roomsForMode(); }
  else if(Math.random()<0.56){ pool=[home]; }
  else { pool=(PREF[sim.id]||[home]).filter(k=>rects.has(k)); }
  if(a.is_blocked||/aguardando|quarentena/.test(String(a.state))){
    if(rects.has("war")&&Math.random()<0.5) pool=["war"];
  }
  pool=pool.filter(k=>rects.has(k)); if(!pool.length) pool=[home];
  const target=pool[Math.floor(Math.random()*pool.length)];
  const p=ptIn(target); if(!p) return;
  sim.tx=p.x; sim.ty=p.y; sim.dest=target; sim.moving=true;
}
function tick(dt){
  const now=performance.now(), k=world.sim.speed;
  sims.forEach(sim=>{
    if(!sim.moving && now>=sim.dwell) chooseDest(sim);
    if(sim.moving){
      const dx=sim.tx-sim.x, dy=sim.ty-sim.y, d=Math.hypot(dx,dy), step=sim.speed*dt*k;
      if(d<=step||d<1.5){ sim.x=sim.tx; sim.y=sim.ty; sim.moving=false; sim.cur=sim.dest; sim.dwell=now+1200+Math.random()*3200; }
      else { sim.x+=dx/d*step; sim.y+=dy/d*step; sim.face=dx<-0.4?-1:(dx>0.4?1:sim.face); }
    }
    paint(sim);
  });
}
function frame(ts){ if(!world.sim.playing){raf=null;return;} const dt=Math.min(0.05,lastTs?(ts-lastTs)/1000:0.016); lastTs=ts; tick(dt); raf=requestAnimationFrame(frame); }
function start(){ if(raf!=null)return; lastTs=0; raf=requestAnimationFrame(frame); }
function stop(){ if(raf!=null){cancelAnimationFrame(raf);raf=null;} }

function renderAvatars(){
  const lay=layer();
  world.agents.forEach(a=>{
    if(!sims.has(a.id)) return;
    let el=avEls.get(a.id);
    if(!el){
      el=document.createElement("button"); el.type="button"; el.className="avatar"; el.dataset.id=a.id;
      el.addEventListener("click",(e)=>{e.stopPropagation();selectAgent(a.id);});
      lay.appendChild(el); avEls.set(a.id,el);
    }
    const mood=moodFor(a.state);
    el.style.setProperty("--c",a.color);
    el.style.setProperty("--mood",mood.color);
    el.title=`${a.name} — ${a.role} — ${mood.label}`;
    el.innerHTML=`
      <span class="av-shadow"></span>
      <span class="av-bubble">${esc(SOULS[a.id]?.question? mood.label : mood.label)}</span>
      <span class="av-name">${esc(shortName(a.name))}</span>
      <span class="av-figure"><span class="av-head">${esc(a.symbol)}<span class="av-mood"></span></span><span class="av-body"></span></span>`;
    paint(sims.get(a.id));
  });
}
function paint(sim){
  const el=avEls.get(sim.id); if(!el) return;
  const a=agentById(sim.id);
  el.style.transform=`translate(${(sim.x-19).toFixed(1)}px,${(sim.y-24).toFixed(1)}px)`;
  el.style.setProperty("--face",sim.face<0?"-1":"1");
  const isCrit = a?.is_blocked===1;
  el.className=["avatar", a?.id===1?"arconte":"", sim.moving?"moving":"resting",
    world.selected.type==="agent"&&world.selected.id===sim.id?"selected":"",
    isCrit?"critical":"",
    world.sim.mode&&!agentInMode(sim.id)?"dim":"",
    world.sim.mode&&agentInMode(sim.id)?"focus":"",
    world.sim.showNames?"":""].filter(Boolean).join(" ");
}

/* ════════ HUD / MODOS / TEMA ════════ */
function setActive(el,on){ if(el) el.classList.toggle("active",!!on); }

function togglePlay(){
  world.sim.playing=!world.sim.playing;
  const b=$("#hud-play"); b.textContent=world.sim.playing?"⏸ Pausar vida":"▶ Retomar vida"; setActive(b,!world.sim.playing);
  $("#board").classList.toggle("paused",!world.sim.playing);
  if(world.sim.playing) start(); else stop();
}
function setSpeed(v){
  world.sim.speed=v;
  $$("#speed-group .speed-btn").forEach(b=>b.classList.toggle("active",+b.dataset.speed===v));
}
function applyMode(){
  const m=world.sim.mode;
  const board=$("#board");
  ["mode-product","mode-redteam","mode-council","mode-risk"].forEach(c=>board.classList.remove(c));
  if(m) board.classList.add("mode-"+m);
  const focusRooms = m?new Set(MODES[m].rooms):null;
  $$("#floor .room").forEach(el=>{
    el.classList.remove("dim","mode-focus");
    if(focusRooms){ if(focusRooms.has(el.dataset.key)) el.classList.add("mode-focus"); else el.classList.add("dim"); }
  });
  sims.forEach(paint);
}
function setMode(name){
  world.sim.mode = world.sim.mode===name ? null : name;
  ["product","redteam","council","risk"].forEach(k=>setActive($("#mode-"+k),world.sim.mode===k));
  applyMode();
  sims.forEach(s=>{ s.moving=false; s.dwell=performance.now(); });
  toast(world.sim.mode?`Modo ${MODES[name].label} ativo.`:"Modo livre.");
}
function toggleTheme(){
  const html=document.documentElement;
  const dark=html.getAttribute("data-theme")==="dark";
  html.setAttribute("data-theme",dark?"light":"dark");
  $("#toggle-theme").textContent=dark?"☀ Tema":"☾ Tema";
  requestAnimationFrame(()=>{ measure(); sims.forEach(paint); });
}
function togglePlan(){
  world.sim.plan=!world.sim.plan; setActive($("#toggle-plan"),world.sim.plan);
  renderFloor(); requestAnimationFrame(()=>{ measure(); applyMode(); if(world.selected.type==="room") markRoom(); });
}
function toggleConsole(force){
  const c=$("#console"); const show = force!=null?force:c.hasAttribute("hidden");
  if(show) c.removeAttribute("hidden"); else c.setAttribute("hidden","");
  setActive($("#toggle-console"),show);
}
function focusArconte(){ focusAgent(1); toast("Foco no Arconte Supremo — coordenação central."); }

function focusRoom(key){ const el=$(`#floor .room[data-key="${key}"]`); el?.scrollIntoView({behavior:"smooth",block:"center"}); selectRoom(key,true); }
function focusAgent(id){
  selectAgent(id);
  const el=avEls.get(id); el?.scrollIntoView?.({behavior:"smooth",block:"center"});
  const s=sims.get(id); if(s){ s.moving=false; s.dwell=performance.now()+2600; }
}

/* ════════ DEMO GUIADA (≈50s, 6 etapas) ════════ */
let demoT=[];
function clearDemo(){ demoT.forEach(t=>clearTimeout(t)); demoT=[]; $("#demo-banner").setAttribute("hidden",""); }
function banner(step,text){ const b=$("#demo-banner"); b.removeAttribute("hidden"); b.innerHTML=`<span class="db-step">ETAPA ${step}/6</span><span>${esc(text)}</span>`; }
function toggleDemo(){
  if(world.sim.demo){ stopDemo(); return; }
  world.sim.demo=true; setActive($("#hud-demo"),true); if(!world.sim.playing) togglePlay();
  const at=(ms,fn)=>demoT.push(setTimeout(fn,ms));
  banner(1,"Arconte Supremo & Founder’s Office — onde a decisão de Favini nasce.");
  focusAgent(1);
  at(1500,()=>focusRoom("founder"));
  at(8000,()=>{ banner(2,"Conselho do Arconte — governança viva em sessão."); focusRoom("council"); });
  at(16000,()=>{ banner(3,"Salas de Produto/MVP — Aitherion, Vantion/LUNA construindo."); setMode("product"); focusRoom("lab"); });
  at(25000,()=>{ banner(4,"Red Team & Riscos — adversarial interno e War Room."); setMode("redteam"); focusRoom("redteam"); });
  at(34000,()=>{ banner(5,"Cofre Genoma — protegido e em quarentena, conteúdo oculto."); if(world.sim.mode)setMode(world.sim.mode); focusRoom("vault"); });
  at(42000,()=>{ banner(6,"Decisão pendente para Favini — nada executa sem aval humano."); const d=world.decisions.find(x=>x.status==="pending"); if(d){ toggleConsole(true); } focusRoom("council"); });
  at(50000,()=>{ toast("Fim do tour. Estado preservado — nenhuma ação externa executada."); stopDemo(); });
}
function stopDemo(){ clearDemo(); world.sim.demo=false; setActive($("#hud-demo"),false); }

/* ════════ INSPECTOR PREMIUM ════════ */
function showInspector(html){ $("#insp-empty").setAttribute("hidden",""); const b=$("#insp-body"); b.removeAttribute("hidden"); b.innerHTML=html; b.scrollTop=0; }
function renderInspectorWelcome(){ $("#insp-empty").removeAttribute("hidden"); const b=$("#insp-body"); b.setAttribute("hidden",""); b.innerHTML=""; }

function srcTag(src){ return src==="api"?`<span class="source-tag api">dados: API local</span>`:`<span class="source-tag seed">dados: seed visual</span>`; }
function naBlock(text,seal){ return `<div class="next-action"><div class="na-h">Próxima ação sugerida</div><p>${esc(text)}</p>${seal?`<small>${esc(seal)}</small>`:""}</div>`; }

function renderAgentInspector(id){
  const a=agentById(id); if(!a) return;
  const soul=SOULS[id]||{}; const sim=sims.get(id); const cur=roomByKey(sim?.cur||a.homeKey);
  const mood=moodFor(a.state);
  const task=world.tasks.find(t=>t.agent_name&&t.agent_name===a.name);
  let rec;
  if(a.is_blocked) rec="Aguardar liberação de Favini antes de seguir. Decisão humana obrigatória.";
  else if(String(a.state).includes("quarentena")) rec="Manter quarentena e confirmar perímetro de acesso (Cerberus).";
  else rec=`${soul.ritual||"revisar estado e atualizar contexto"}.`;
  showInspector(`
    <div class="insp-hero" style="--accent:${a.color}">
      <div class="ih-avatar">${esc(a.symbol)}</div>
      <div class="ih-kicker">Agente${a.id===1?" · central":""}</div>
      <div class="ih-title">${esc(a.name)}</div>
      <div class="ih-sub">${esc(soul.role||a.role)}</div>
    </div>
    <div class="insp-sec"><div class="kv">
      <div class="kv-row"><span class="k">Estado / humor</span><span class="v">${esc(a.state)} · ${esc(mood.label)}</span></div>
      <div class="kv-row"><span class="k">Sala atual</span><span class="v">${esc(cur?cur.name:"—")}</span></div>
      <div class="kv-row"><span class="k">Missão</span><span class="v">${esc(soul.mission||"operar no mandato")}</span></div>
      <div class="kv-row"><span class="k">Tarefa</span><span class="v">${esc(task?`${task.title} (${task.priority})`:"sem tarefa")}</span></div>
    </div></div>
    <div class="insp-sec"><h4>Risco que controla</h4>
      <div class="chips"><span class="chip danger">${esc(soul.controls||"ruído operacional")}</span>
      <span class="chip">${esc(soul.question||"qual a próxima decisão útil?")}</span>
      ${a.can_block?`<span class="chip warn">poder de veto</span>`:`<span class="chip ok">apoio</span>`}</div>
    </div>
    <div class="insp-sec"><h4>Origem</h4><div class="chips">${srcTag(a.source)}</div></div>
    ${naBlock(rec,"simulação local · decisão humana obrigatória")}
  `);
}

function renderRoomInspector(key){
  const room=roomByKey(key); if(!room) return;
  const occ=world.agents.filter(a=>(sims.get(a.id)?.cur||a.homeKey)===key);
  const rts=world.tasks.filter(t=>t.roomKey===key);
  const dec=world.decisions.filter(d=>d.status==="pending");
  const focus=rts[0]?.title||"rotina operacional";
  let rec;
  if(room.quarantine) rec="Manter quarentena; revisar acessos e exceções (Cerberus). Conteúdo do Cofre permanece oculto.";
  else if(room.status==="critico") rec="Escalar foco do Conselho e atribuir mitigação imediata (Cassandra + Atlas).";
  else if(room.regulated) rec="Operar dentro do mandato regulatório (Nomos). Sem ação externa real.";
  else rec="Manter rotina operacional. Sem escalonamento necessário.";
  showInspector(`
    <div class="insp-hero" style="--accent:${room.accent}">
      <div class="ih-kicker">Ambiente</div>
      <div class="ih-title">${esc(room.name)}</div>
      <div class="ih-sub">${esc(room.company||room.sub)}</div>
    </div>
    <div class="insp-sec"><div class="kv">
      <div class="kv-row"><span class="k">Status</span><span class="v">${esc(room.rawStatus||room.status)}</span></div>
      <div class="kv-row"><span class="k">Ocupação</span><span class="v">${occ.length} agente(s)</span></div>
      <div class="kv-row"><span class="k">Segurança / risco</span><span class="v">${esc(room.security||"—")}${room.is_quarantine?" · QUARENTENA":""}</span></div>
      <div class="kv-row"><span class="k">Foco operacional</span><span class="v">${esc(focus)}</span></div>
    </div></div>
    <div class="insp-sec"><h4>Quem está aqui</h4><div class="chips">
      ${occ.map(a=>`<span class="chip clickable" data-agent="${a.id}">${esc(shortName(a.name))}</span>`).join("")||`<span class="chip">sala vazia agora</span>`}
    </div></div>
    ${dec.length?`<div class="insp-sec"><h4>Decisões relacionadas</h4><div class="chips"><span class="chip warn">${dec.length} pendente(s) para Favini</span></div></div>`:""}
    <div class="insp-sec"><h4>Origem</h4><div class="chips">${srcTag(room.source)}</div></div>
    ${naBlock(rec, room.regulated||room.quarantine?"simulação local · decisão humana obrigatória":"")}
  `);
  $$("#insp-body .chip.clickable").forEach(c=>c.addEventListener("click",()=>selectAgent(+c.dataset.agent)));
}

function renderTaskInspector(id){
  const t=world.tasks.find(x=>x.id===id); if(!t) return;
  const room=roomByKey(t.roomKey);
  let rec = t.priority==="P0"&&t.status==="blocked" ? "Resolver dependência crítica (Atlas) e revalidar evidência (Auditor Zero)."
    : t.status==="blocked" ? "Identificar e limpar o bloqueio; reavaliar prazo (Chronos)."
    : t.status==="pending" ? "Atribuir responsável e iniciar com critério de pronto."
    : "Monitorar e validar com evidência antes de aprovar.";
  showInspector(`
    <div class="insp-hero" style="--accent:var(--teal)"><div class="ih-kicker">Tarefa</div><div class="ih-title">${esc(t.title)}</div><div class="ih-sub">${esc(t.company_name||"")}</div></div>
    <div class="insp-sec"><div class="kv">
      <div class="kv-row"><span class="k">Prioridade</span><span class="v">${esc(t.priority)}</span></div>
      <div class="kv-row"><span class="k">Status</span><span class="v">${esc(t.status)}</span></div>
      <div class="kv-row"><span class="k">Agente</span><span class="v">${esc(t.agent_name||"sem agente")}</span></div>
      <div class="kv-row"><span class="k">Sala</span><span class="v">${esc(room?room.name:"—")}</span></div>
    </div></div>
    <div class="insp-sec"><h4>Origem</h4><div class="chips">${srcTag(t.source)}</div></div>
    ${naBlock(rec,"simulação local · decisão humana obrigatória")}
  `);
}

function renderAlertInspector(id){
  const al=world.alerts.find(x=>x.id===id); if(!al) return;
  const rec=al.blocks_progress?"Mitigar antes de aprovar qualquer progresso (Cassandra + Auditor Zero).":"Documentar sinal fraco e definir gatilho de reavaliação.";
  showInspector(`
    <div class="insp-hero" style="--accent:var(--red)"><div class="ih-kicker">Alerta · S${esc(String(al.severity))}</div><div class="ih-title">${esc(al.title)}</div><div class="ih-sub">${esc(al.company_name||"sistema")}</div></div>
    <div class="insp-sec"><div class="kv">
      <div class="kv-row"><span class="k">Bloqueia progresso</span><span class="v">${al.blocks_progress?"sim":"não"}</span></div>
      <div class="kv-row"><span class="k">Mensagem</span><span class="v">${esc(al.message||"—")}</span></div>
    </div></div>
    <div class="insp-sec"><h4>Origem</h4><div class="chips">${srcTag(al.source)}</div></div>
    ${naBlock(rec,"simulação local · decisão humana obrigatória")}
  `);
}

/* ════════ SELEÇÃO ════════ */
function clearSel(){ $$("#floor .room.selected").forEach(e=>e.classList.remove("selected")); }
function markRoom(){ clearSel(); if(world.selected.type==="room"){ $(`#floor .room[data-key="${world.selected.key}"]`)?.classList.add("selected"); } }
function selectAgent(id){ world.selected={type:"agent",key:null,id}; markRoom(); sims.forEach(paint); renderAgentInspector(id); }
function selectRoom(key,keep){
  if(!keep && world.selected.type==="room" && world.selected.key===key){ world.selected={type:null,key:null,id:null}; markRoom(); renderInspectorWelcome(); return; }
  world.selected={type:"room",key,id:null}; markRoom(); sims.forEach(paint); renderRoomInspector(key);
}
function selectTask(id){ world.selected={type:"task",key:null,id}; renderTaskInspector(id); }
function selectAlert(id){ world.selected={type:"alert",key:null,id}; renderAlertInspector(id); }

/* ════════ CONSOLE (apoio textual) ════════ */
function renderConsole(){
  const T=$("#tasks-list"), D=$("#decisions-list"), A=$("#alerts-list");
  $("#task-count").textContent=world.tasks.length; $("#decision-count").textContent=world.decisions.filter(d=>d.status==="pending").length; $("#alert-count").textContent=world.alerts.length;
  T.innerHTML=world.tasks.length?world.tasks.map(t=>`<div class="console-row" data-task="${t.id}"><div class="cr-h"><span class="cr-t">${esc(t.title)}</span><span class="tag-pri ${esc(t.priority.toLowerCase())}">${esc(t.priority)}</span></div><div class="cr-m">${esc(t.status)} · ${esc(t.agent_name||"sem agente")}</div></div>`).join(""):`<div class="empty-note">sem tarefas</div>`;
  D.innerHTML=world.decisions.length?world.decisions.map(d=>`<div class="console-row"><div class="cr-h"><span class="cr-t">${esc(d.code)}</span><span class="tag-pri ${esc(d.priority.toLowerCase())}">${esc(d.priority)}</span></div><div class="cr-m">${esc(d.title)} · ${esc(d.required_by)}</div></div>`).join(""):`<div class="empty-note">sem decisões</div>`;
  A.innerHTML=world.alerts.length?world.alerts.map(a=>`<div class="console-row" data-alert="${a.id}"><div class="cr-h"><span class="cr-t">${esc(a.title)}</span><span class="tag-pri p0">S${esc(String(a.severity))}</span></div><div class="cr-m">${esc(a.company_name||"sistema")} · ${esc(a.message)}</div></div>`).join(""):`<div class="empty-note">sem alertas</div>`;
  T.querySelectorAll("[data-task]").forEach(r=>r.addEventListener("click",()=>{selectTask(+r.dataset.task);}));
  A.querySelectorAll("[data-alert]").forEach(r=>r.addEventListener("click",()=>{selectAlert(+r.dataset.alert);}));
}

/* ════════ HELPERS ════════ */
function shortName(n){ const p=String(n||"Agente").split(" ").filter(Boolean); if(!p.length)return"Agente"; if(p[0]==="Arconte")return"Arconte"; if(p[0]==="Auditor")return"Auditor"; return p[0]; }
function esc(v){ return String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;"); }
let toastT=null;
function toast(msg){ const t=$("#toast"); t.textContent=msg; t.classList.add("show"); clearTimeout(toastT); toastT=setTimeout(()=>t.classList.remove("show"),5200); }

function bindHud(){
  $("#hud-play").addEventListener("click",togglePlay);
  $$("#speed-group .speed-btn").forEach(b=>b.addEventListener("click",()=>setSpeed(+b.dataset.speed)));
  $("#mode-product").addEventListener("click",()=>setMode("product"));
  $("#mode-redteam").addEventListener("click",()=>setMode("redteam"));
  $("#mode-council").addEventListener("click",()=>setMode("council"));
  $("#mode-risk").addEventListener("click",()=>setMode("risk"));
  $("#focus-arconte").addEventListener("click",focusArconte);
  $("#hud-demo").addEventListener("click",toggleDemo);
  $("#toggle-plan").addEventListener("click",togglePlan);
  $("#toggle-theme").addEventListener("click",toggleTheme);
  $("#toggle-console").addEventListener("click",()=>toggleConsole());
  $("#console-close").addEventListener("click",()=>toggleConsole(false));
  let rz=null;
  window.addEventListener("resize",()=>{ clearTimeout(rz); rz=setTimeout(()=>{ measure(); sims.forEach(s=>{ if(!rects.has(s.cur))return; if(!s.moving){const c=centerOf(s.cur); if(c){s.x=c.x;s.y=c.y;s.tx=c.x;s.ty=c.y;}} paint(s); }); },180); });
  document.addEventListener("visibilitychange",()=>{ if(document.hidden) stop(); else if(world.sim.playing) start(); });
}

window.addEventListener("DOMContentLoaded",()=>{ boot().catch(e=>{ buildWorld({}); renderConn(); renderFloor(); syncSim(); renderConsole(); renderInspectorWelcome(); renderWorldStats(); toast("Modo visual local ativo."); }); });
