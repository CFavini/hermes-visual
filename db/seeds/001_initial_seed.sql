PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

DELETE FROM hermes_cycles;
DELETE FROM risk_alerts;
DELETE FROM decisions;
DELETE FROM task_events;
DELETE FROM tasks;
DELETE FROM agents;
DELETE FROM rooms;
DELETE FROM virtual_companies;

INSERT INTO virtual_companies
(id, name, slug, entity_type, phase, status, legal_status, labels, risk_level, visual_color, data_classification, is_simulated, external_interaction_allowed, requires_human_responsible, requires_legal_review, is_blocked, public_summary)
VALUES
(1, 'Founder’s Office Favini', 'founders-office-favini', 'centro_comando', 1, 'active', 'sem_personalidade_juridica', 'PRIVADA FAVINI;SIMULADA;NÃO INTERAGE COM TERCEIROS', 2, '#d6ad60', 'S1', 1, 0, 0, 0, 0, 'Centro privado de decisão e coordenação de Favini.'),
(2, 'Conselho do Arconte', 'conselho-do-arconte', 'conselho_visual', 1, 'active', 'sem_personalidade_juridica', 'SIMULADA;EM TREINAMENTO;NÃO INTERAGE COM TERCEIROS', 2, '#7aa2ff', 'S1', 1, 0, 0, 0, 0, 'Conselho visual de agentes subordinados ao Arconte.'),
(3, 'COS Virtual', 'cos-virtual', 'empresa_virtual_favini', 1, 'blocked', 'sem_personalidade_juridica', 'REGULADA;BLOQUEADA;NÃO INTERAGE COM TERCEIROS;EXIGE HUMANO RESPONSÁVEL', 5, '#ff3b3b', 'S2', 1, 0, 1, 1, 1, 'Empresa virtual candidata regulada. Sem terceiros, sem dados reais, sem execução externa.'),
(4, 'Contabilidades Virtuais', 'contabilidades-virtuais', 'linha_exploratoria', 0, 'incubation', 'sem_personalidade_juridica', 'LINHA EXPLORATÓRIA;INCUBAÇÃO REGULADA;EXIGE HUMANO RESPONSÁVEL;NÃO INTERAGE COM TERCEIROS', 4, '#ffb020', 'S1', 1, 0, 1, 1, 0, 'Linha exploratória assistiva para organização contábil simulada.'),
(5, 'Aitherion Labs em estruturação', 'aitherion-labs-estruturacao', 'frente_fisica_estruturacao', 1, 'planning', 'nao_constituida', 'PROJETO EM ESTRUTURAÇÃO;SIMULADA NA INTERFACE;NÃO INTERAGE COM TERCEIROS', 3, '#2f6fed', 'S2', 1, 0, 0, 1, 0, 'Frente Aitherion em estruturação, ainda sem personalidade jurídica.'),
(6, 'Vantion/LUNA', 'vantion-luna', 'frente_tecnica_protegida', 0, 'quarantine_partial', 'sem_personalidade_juridica', 'QUARENTENA PARCIAL;TÉCNICA;NÃO INTERAGE COM TERCEIROS', 4, '#8f5cff', 'S2', 1, 0, 0, 1, 0, 'Frente técnica protegida, visualizada apenas por metadados sanitizados.'),
(7, 'Cofre Genoma Digital', 'cofre-genoma-digital', 'ativo_pessoal_protegido', 0, 'quarantine', 'ativo_pessoal', 'S4;QUARENTENA;BLOQUEADO;SEM CONTEÚDO;NÃO INTERAGE COM TERCEIROS', 5, '#3b1d5f', 'S4', 1, 0, 1, 1, 1, 'Cofre visual sem conteúdo bruto; acesso apenas como cofre S4.'),
(8, 'Biblioteca dos Originais', 'biblioteca-dos-originais', 'acervo_autoral', 1, 'private', 'ativo_pessoal_autoral', 'AUTORAL;PRIVADA FAVINI;NÃO INTERAGE COM TERCEIROS', 2, '#9a6a3a', 'S1', 1, 0, 0, 0, 0, 'Acervo visual de obras e originais autorizados/sanitizados.'),
(9, 'Radar Argentina', 'radar-argentina', 'hipotese_jurisdicional', 0, 'observation', 'hipotese_sem_execucao', 'HIPÓTESE JURISDICIONAL;OBSERVAÇÃO;NÃO EXECUÇÃO;SEM INSTRUÇÃO DE ABERTURA', 3, '#18b7ff', 'S0', 1, 0, 0, 1, 0, 'Radar público e conceitual sobre hipótese jurisdicional futura.'),
(10, 'Sandbox de Novas Empresas', 'sandbox-novas-empresas', 'sandbox', 0, 'incubation', 'sem_personalidade_juridica', 'SIMULADA;INCUBAÇÃO;NÃO INTERAGE COM TERCEIROS', 2, '#5fd19a', 'S0', 1, 0, 0, 0, 0, 'Área de criação e teste de novas empresas virtuais simuladas.');

INSERT INTO rooms
(id, company_id, name, slug, room_type, status, grid_col, grid_row, grid_w, grid_h, security_level, is_quarantine)
VALUES
(1, 1, 'Sala Executiva Favini', 'sala-executiva-favini', 'executive', 'active', 5, 1, 4, 2, 'S1', 0),
(2, 2, 'Conselho / Reunião', 'conselho-reuniao', 'meeting', 'active', 1, 1, 4, 2, 'S1', 0),
(3, 3, 'Compliance COS', 'compliance-cos', 'compliance', 'blocked', 1, 3, 3, 3, 'S2', 0),
(4, 4, 'Incubação Regulada', 'incubacao-regulada', 'incubation', 'active', 4, 3, 3, 2, 'S1', 0),
(5, 5, 'Sala de Trabalho Aitherion', 'sala-trabalho-aitherion', 'work', 'active', 7, 3, 4, 2, 'S2', 0),
(6, 6, 'Laboratório Técnico Vantion/LUNA', 'laboratorio-tecnico-vantion-luna', 'lab', 'active', 7, 5, 4, 2, 'S2', 0),
(7, 7, 'Server Room / Cofre S4', 'server-room-cofre-s4', 'server_vault', 'blocked', 1, 6, 3, 2, 'S4', 1),
(8, 8, 'Biblioteca Autoral', 'biblioteca-autoral', 'library', 'active', 4, 5, 3, 2, 'S1', 0),
(9, 9, 'Radar Jurisdicional', 'radar-jurisdicional', 'radar', 'observation', 9, 1, 3, 2, 'S0', 0),
(10, 10, 'Sandbox Visual', 'sandbox-visual', 'sandbox', 'active', 4, 7, 4, 2, 'S0', 0),
(11, NULL, 'Área de Descanso / Status', 'area-descanso-status', 'lounge', 'active', 8, 7, 4, 2, 'S0', 0);

INSERT INTO agents
(id, name, slug, role, avatar_symbol, home_room_id, current_room_id, state, status, alert_type, can_block, is_blocked, data_access_level, external_interaction_allowed, visual_color, xp)
VALUES
(1, 'Arconte Supremo', 'arconte-supremo', 'Governador operacional privado', '♛', 1, 1, 'aguardando_favini', 'active', 'decisao_pendente', 1, 0, 'S2', 0, '#d6ad60', 40),
(2, 'Auditor Zero', 'auditor-zero', 'Auditoria e veto de falsa execução', '◉', 2, 2, 'auditando', 'active', 'falsa_execucao', 1, 0, 'S2', 0, '#b88cff', 35),
(3, 'Cerberus', 'cerberus', 'Segurança, cofre e quarentena', '◆', 7, 7, 'quarentena', 'active', 's3_s4', 1, 0, 'S4_METADATA_ONLY', 0, '#7b3ff2', 45),
(4, 'Cassandra', 'cassandra', 'Red Team e anti-ingenuidade', '⚠', 2, 2, 'red_team', 'active', 'premissa_fraca', 1, 0, 'S2', 0, '#ff3b3b', 32),
(5, 'Chronos', 'chronos', 'Tempo, ciclos e atrasos', '◷', 1, 1, 'trabalhando', 'active', 'prazo', 0, 0, 'S1', 0, '#64d2ff', 25),
(6, 'Sophia', 'sophia', 'Curadoria documental', '📘', 8, 8, 'lendo_documento', 'active', 'documento_sem_classificacao', 0, 0, 'S2_METADATA_ONLY', 0, '#4dd4ac', 28),
(7, 'Nomos', 'nomos', 'Jurídico virtual e jurisdição', '⚖', 9, 9, 'exige_juridico', 'active', 'juridico', 1, 0, 'S2', 0, '#ffb020', 30),
(8, 'Themis', 'themis', 'Compliance e responsabilidade', '🛡', 3, 3, 'auditando', 'active', 'compliance', 1, 0, 'S2', 0, '#ff8a3d', 29),
(9, 'Atlas', 'atlas', 'Operações e processos', '▣', 5, 5, 'trabalhando', 'active', 'gargalo_operacional', 0, 0, 'S1', 0, '#2f6fed', 24),
(10, 'Midas', 'midas', 'Financeiro simulado', '◎', 5, 5, 'idle', 'active', 'financeiro', 0, 0, 'S1', 0, '#ffd166', 20),
(11, 'Daedalus', 'daedalus', 'Produto, arquitetura e protótipo', '△', 6, 6, 'trabalhando', 'active', 'produto_mvp', 0, 0, 'S2', 0, '#7aa2ff', 38),
(12, 'Argos', 'argos', 'Risco transversal', '◌', 2, 2, 'auditando', 'active', 'risco_sistemico', 1, 0, 'S2', 0, '#aab7c4', 31);

INSERT INTO tasks
(id, company_id, room_id, assigned_agent_id, title, description, priority, status, risk_level, requires_favini, requires_legal, external_action_allowed, is_simulated, data_classification)
VALUES
(1, 1, 1, 1, 'Validar implementação v0.4-alpha', 'Confirmar criação da pasta hermes-visual, schema mínimo, seed e servidor local.', 'P0', 'pending', 3, 1, 0, 0, 1, 'S1'),
(2, 3, 3, 7, 'Delimitar COS como simulação regulada bloqueada', 'Manter COS sem terceiros, sem dados reais e sem operação externa.', 'P0', 'blocked', 5, 1, 1, 0, 1, 'S2'),
(3, 7, 7, 3, 'Manter Cofre Genoma Digital S4 sem conteúdo', 'Exibir apenas cofre S4 e metadados mínimos; conteúdo bruto não entra.', 'P0', 'blocked', 5, 1, 1, 0, 1, 'S4'),
(4, 5, 5, 2, 'Revisar Aitherion como frente em estruturação', 'Garantir que Aitherion apareça como projeto em estruturação, não pessoa jurídica.', 'P0', 'pending', 4, 1, 1, 0, 1, 'S2'),
(5, 10, 10, 11, 'Criar template de Empresa Virtual Favini', 'Modelo visual mínimo para novas empresas virtuais simuladas.', 'P1', 'pending', 2, 0, 0, 0, 1, 'S0'),
(6, 2, 2, 2, 'Auditar falsa execução', 'Impedir que o app declare execução externa quando só houve simulação local.', 'P1', 'in_progress', 3, 0, 0, 0, 1, 'S1'),
(7, 9, 9, 7, 'Monitorar Radar Argentina como hipótese', 'Registrar observação sem instrução de abertura de empresa.', 'P1', 'pending', 3, 0, 1, 0, 1, 'S0'),
(8, 2, 2, 1, 'Organizar Conselho Visual do Arconte', 'Distribuir agentes no Pixel Office e dar leitura rápida de estado.', 'P1', 'pending', 2, 0, 0, 0, 1, 'S1');

INSERT INTO task_events
(task_id, agent_id, event_type, message, is_external_action, data_classification)
VALUES
(1, 1, 'created', 'Tarefa criada para validar v0.4-alpha local.', 0, 'S1'),
(2, 7, 'blocked', 'COS bloqueado por regulação, terceiros e humano responsável obrigatório.', 0, 'S2'),
(3, 3, 'quarantine', 'Cofre Genoma Digital marcado como S4; conteúdo não renderizado.', 0, 'S4'),
(4, 2, 'audit', 'Aitherion marcada como frente em estruturação, sem personalidade jurídica.', 0, 'S2'),
(6, 2, 'audit', 'Auditor Zero ativo para impedir falsa execução.', 0, 'S1');

INSERT INTO decisions
(id, company_id, title, decision_code, status, priority, summary, required_by, requires_favini, external_effect_allowed, data_classification)
VALUES
(1, 1, 'Autorizar criação física do protótipo Hermes v0.4-alpha', 'DEC-004-V04-ALPHA', 'pending', 'P0', 'Decidir se os arquivos executáveis devem ser criados na nova pasta hermes-visual.', 'Favini', 1, 0, 'S1'),
(2, 1, 'Aprovar estilo Pixel Office / The Sims corporativo 2D', 'DEC-005-PIXEL-OFFICE', 'pending', 'P0', 'Confirmar o estilo visual top-down/pixel office como direção principal do cockpit.', 'Favini', 1, 0, 'S0'),
(3, 1, 'Confirmar SQLite local como base inicial', 'DEC-006-SQLITE-LOCAL', 'pending', 'P0', 'Confirmar SQLite em db/private como estado local inicial, sem cloud e sem banco externo.', 'Favini', 1, 0, 'S1');

INSERT INTO risk_alerts
(id, company_id, task_id, agent_id, title, risk_type, severity, status, blocks_progress, requires_favini, data_classification, message)
VALUES
(1, 3, 2, 7, 'COS regulado e bloqueado', 'regulatorio', 5, 'open', 1, 1, 'S2', 'COS envolve seguros, sinistros, IA, dados e terceiros; não pode operar externamente.'),
(2, 7, 3, 3, 'Cofre GD S4', 'quarentena', 5, 'open', 1, 1, 'S4', 'Genoma Digital aparece apenas como cofre visual S4, sem conteúdo bruto.'),
(3, 4, NULL, 8, 'Contabilidade exige humano responsável', 'responsabilidade_tecnica', 4, 'open', 1, 0, 'S1', 'Agentes podem preparar simulação, mas não assumir atos privativos.'),
(4, 9, 7, 7, 'Argentina é hipótese, não lei operacional', 'hipotese_juridica', 3, 'open', 0, 0, 'S0', 'Radar Argentina observa tendência, sem instrução de abertura de empresa.'),
(5, 5, 4, 2, 'Aitherion ainda não é pessoa jurídica', 'governanca', 3, 'open', 0, 1, 'S2', 'Interface deve mostrar estruturação, não operação societária real.'),
(6, 6, NULL, 3, 'Vantion/LUNA requer proteção técnica', 'pi_tecnica', 4, 'open', 1, 1, 'S2', 'Exibir apenas frente técnica sanitizada, sem PI sensível.');

COMMIT;
