/**
 * Hermes v0.4.2 — Operational Memory Panel Manager
 * Carrega dados do SQLite via /api/knowledge/* e exibe no painel lateral
 */

class MemoryPanelManager {
  constructor() {
    this.panel = document.getElementById('memory-panel');
    this.closeBtn = document.getElementById('memory-close');
    this.summaryElements = {
      trained: document.getElementById('trained-count'),
      sources: document.getElementById('sources-count'),
      claims: document.getElementById('claims-count'),
      rules: document.getElementById('rules-count'),
      gaps: document.getElementById('gaps-count'),
      cost: document.getElementById('cost-value'),
    };

    this.attachEvents();
  }

  attachEvents() {
    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.hide());
    }

    // Expõe toggles globais
    window.toggleMemoryPanel = () => this.toggle();
    window.showMemoryPanel = () => this.show();
    window.loadAgentMemory = (agentId) => this.loadAgentMemory(agentId);
  }

  toggle() {
    if (this.panel.classList.contains('hidden')) {
      this.show();
    } else {
      this.hide();
    }
  }

  show() {
    this.panel.classList.remove('hidden');
    this.loadMemoryData();
  }

  hide() {
    this.panel.classList.add('hidden');
  }

  async loadMemoryData() {
    try {
      // Tenta carregar via API (v0.4.2 endpoints)
      let sourcesData = { sources: [] };
      let claimsData = { claims: [] };
      let uncertData = { uncertainties: [] };
      let costData = {};

      try {
        const sourcesResp = await fetch('/api/knowledge/sources');
        if (sourcesResp.ok) sourcesData = await sourcesResp.json();
      } catch (e) {
        console.log('API /api/knowledge/sources indisponível, usando dados locais');
      }

      try {
        const claimsResp = await fetch('/api/knowledge/claims');
        if (claimsResp.ok) claimsData = await claimsResp.json();
      } catch (e) {
        console.log('API /api/knowledge/claims indisponível');
      }

      try {
        const uncertResp = await fetch('/api/knowledge/uncertainties');
        if (uncertResp.ok) uncertData = await uncertResp.json();
      } catch (e) {
        console.log('API /api/knowledge/uncertainties indisponível');
      }

      try {
        const costResp = await fetch('/api/model-usage/summary');
        if (costResp.ok) costData = await costResp.json();
      } catch (e) {
        console.log('API /api/model-usage/summary indisponível');
      }

      // Se APIs não retornaram dados, carrega JSON embarcado
      if (!sourcesData.sources || sourcesData.sources.length === 0) {
        try {
          const localData = await fetch('hermes-knowledge-data.json');
          if (localData.ok) {
            const embedded = await localData.json();
            sourcesData = { sources: embedded.sources || [] };
            claimsData = { claims: embedded.claims || [] };
            uncertData = { uncertainties: embedded.uncertainties || [] };
            costData = embedded.stats || {};
            console.log('✓ Usando dados embarcados (hermes-knowledge-data.json)');
          }
        } catch (e) {
          console.error('Dados embarcados também indisponíveis:', e);
        }
      }

      this.renderSources(sourcesData.sources || []);

      const claimsCount = claimsData.claims ? claimsData.claims.length : 0;

      this.renderUncertainties(uncertData.uncertainties || []);

      if (costData.total) {
        this.renderCostBreakdown(costData);
      }

      // Atualiza summary
      const agents = (sourcesData.sources || []).reduce((acc, s) => {
        if (!acc.includes(s.agent_id)) acc.push(s.agent_id);
        return acc;
      }, []);

      if (this.summaryElements.trained) {
        this.summaryElements.trained.textContent = agents.length;
      }
      if (this.summaryElements.sources) {
        this.summaryElements.sources.textContent = sourcesData.sources ? sourcesData.sources.length : 0;
      }
      if (this.summaryElements.claims) {
        this.summaryElements.claims.textContent = claimsCount;
      }
      if (this.summaryElements.gaps) {
        this.summaryElements.gaps.textContent = (uncertData.uncertainties || []).length;
      }
      if (costData.total && this.summaryElements.cost) {
        const totalCost = costData.total.total_cost || 0;
        this.summaryElements.cost.textContent = `$${totalCost.toFixed(2)}`;
      }
    } catch (err) {
      console.error('Erro ao carregar memória operacional:', err);
    }
  }

  renderSources(sources) {
    const container = document.getElementById('sources-list');
    if (!container) return;

    if (sources.length === 0) {
      container.innerHTML = '<p class="placeholder">Nenhuma fonte carregada</p>';
      return;
    }

    const html = sources.map(source => `
      <div class="source-item">
        <div class="source-title">${this.escapeHtml(source.title || 'Sem título')}</div>
        <div class="source-meta">
          <span>${source.agent_name || 'Agente?'}</span>
          <span>${source.year || '?'}</span>
          <span class="source-badge source-status-${source.status === 'lida_completa' ? 'ok' : 'partial'}">
            ${source.status || 'desconhecido'}
          </span>
          <span class="source-badge">${source.level}</span>
        </div>
      </div>
    `).join('');

    container.innerHTML = html;
  }

  renderUncertainties(uncertainties) {
    const container = document.getElementById('uncertainties-list');
    if (!container) return;

    if (uncertainties.length === 0) {
      container.innerHTML = '<p class="placeholder">Sem incertezas abertas</p>';
      return;
    }

    const html = uncertainties.map(unc => `
      <div class="uncertainty-item">
        <span class="uncertainty-impact impact-${unc.impact_level || 'medio'}">
          ${unc.impact_level || 'médio'}
        </span>
        <span>${this.escapeHtml(unc.uncertainty_text || '')}</span>
        <br/>
        <small style="color: #999;">Agente: ${unc.agent_name || 'n/d'}</small>
      </div>
    `).join('');

    container.innerHTML = html;
  }

  renderCostBreakdown(costData) {
    const container = document.getElementById('cost-breakdown');
    if (!container) return;

    const byProvider = costData.by_provider || [];
    if (byProvider.length === 0) {
      container.innerHTML = '<p class="placeholder">Sem uso de modelos registrado</p>';
      return;
    }

    const html = byProvider.map(provider => `
      <div class="cost-item">
        <span class="cost-provider">${provider.provider}</span>
        <span class="cost-amount">$${(provider.total_cost || 0).toFixed(2)}</span>
      </div>
    `).join('');

    container.innerHTML = html;
  }

  async loadAgentMemory(agentId) {
    try {
      const resp = await fetch(`/api/knowledge/agents/${agentId}/learning`);
      const data = await resp.json();

      if (!data.ok) {
        console.error('Erro ao carregar aprendizagem do agente');
        return;
      }

      this.renderAgentLearning(data);
    } catch (err) {
      console.error('Erro ao carregar memória do agente:', err);
    }
  }

  renderAgentLearning(agentData) {
    const container = document.getElementById('agent-learning');
    if (!container) return;

    let html = '';

    // Learning text
    if (agentData.latest_learning && agentData.latest_learning.learning_text) {
      html += `
        <div class="learning-item">
          <span class="learning-label">Última Aprendizagem</span>
          ${this.escapeHtml(agentData.latest_learning.learning_text)}
          ${agentData.latest_learning.maturity_after ? 
            `<br/><small style="color: #999;">Maturidade: ${agentData.latest_learning.maturity_after.toFixed(1)}/5</small>` 
            : ''}
        </div>
      `;
    }

    // Sources
    if (agentData.sources && agentData.sources.length > 0) {
      html += `
        <div class="learning-item" style="border-left-color: #66bb6a;">
          <span class="learning-label" style="color: #66bb6a;">Fontes Estudadas</span>
          ${agentData.sources.length} fontes (${agentData.sources
            .filter(s => s.status === 'lida_completa').length} completas)
        </div>
      `;
    }

    // Rules
    if (agentData.rules && agentData.rules.length > 0) {
      html += `
        <div class="learning-item" style="border-left-color: #ffa726;">
          <span class="learning-label" style="color: #ffa726;">Regras Operacionais</span>
          ${agentData.rules.length} regras novas incorporadas
        </div>
      `;
    }

    // Gaps
    if (agentData.open_gaps && agentData.open_gaps.length > 0) {
      html += `
        <div class="learning-item" style="border-left-color: #ef5350;">
          <span class="learning-label" style="color: #ef5350;">Lacunas Abertas</span>
          ${agentData.open_gaps.length} incertezas aguardando resolução
        </div>
      `;
    }

    if (!html) {
      html = '<p class="placeholder">Sem aprendizagem registrada</p>';
    }

    container.innerHTML = html;
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Inicializa ao carregar o documento
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.memoryPanel = new MemoryPanelManager();
  });
} else {
  window.memoryPanel = new MemoryPanelManager();
}
