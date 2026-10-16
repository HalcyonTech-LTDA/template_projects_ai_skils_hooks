#!/usr/bin/env node
'use strict';
/**
 * Importa skills, regras e agentes de repositorios publicos "modern-*" do GitHub
 * para .claude/ do template. Fonte sempre o GitHub (clone raso em tmpdir).
 *
 * Uso: node .claude/scripts/importar-padroes.js [--only <curto>] [--dry-run]
 */
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const ORG = 'HalcyonTech-LTDA';
const REF = 'main';
const ROOT = path.resolve(__dirname, '..', '..');
const SKILLS_DIR = path.join(ROOT, '.claude', 'skills');
const SHARED_DIR = path.join(SKILLS_DIR, '_shared');
const AGENTS_DIR = path.join(ROOT, '.claude', 'agents');
const LOCK_PATH = path.join(ROOT, 'padroes-lock.json');
const PROTEGIDOS = ['explorer', 'implementer', 'researcher', 'reviewer', 'worker'];
const TOOLS_BASE = 'Read, Write, Edit, Grep, Glob, WebSearch, WebFetch';

const REPOS = {
  java: 'modern-java-best-practices',
  'spring-boot': 'modern-spring-boot-best-practices',
  'spring-boot-microservices': 'modern-spring-boot-microservices-best-practices',
  mongodb: 'modern-mongodb-best-practices',
  docker: 'modern-docker-best-practices',
  git: 'modern-git-best-practices',
  k6: 'modern-k6-best-practices',
  'postman-newman': 'modern-postman-newman-best-practices',
  wiremock: 'modern-wiremock-best-practices',
  'azure-bicep': 'modern-azure-bicep-best-practices',
  'business-blueprint': 'modern-business-blueprint-plugin',
};

function falha(msg) {
  throw new Error(msg);
}

function parseArgs(argv) {
  const opts = { only: null, dryRun: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--dry-run') opts.dryRun = true;
    else if (argv[i] === '--only') opts.only = argv[++i];
    else falha(`Opcao desconhecida: ${argv[i]}`);
  }
  if (opts.only && !REPOS[opts.only]) {
    falha(`--only invalido "${opts.only}". Validos: ${Object.keys(REPOS).join(', ')}`);
  }
  return opts;
}

function git(args, cwd) {
  return execFileSync('git', args, { cwd, encoding: 'utf8' }).trim();
}

function clonar(repo, destRoot) {
  const dest = path.join(destRoot, repo);
  const url = `https://github.com/${ORG}/${repo}.git`;
  git(['-c', 'core.autocrlf=false', 'clone', '-q', '--depth', '1', '--branch', REF, url, dest]);
  return { dir: dest, commit: git(['rev-parse', 'HEAD'], dest) };
}

function lerJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function lerLock() {
  if (!fs.existsSync(LOCK_PATH)) return { version: 1, plugins: {} };
  return lerJson(LOCK_PATH);
}

function ordenar(obj) {
  if (Array.isArray(obj)) return obj.map(ordenar);
  if (obj && typeof obj === 'object') {
    return Object.fromEntries(Object.keys(obj).sort().map((k) => [k, ordenar(obj[k])]));
  }
  return obj;
}

function gravarLock(lock) {
  fs.writeFileSync(LOCK_PATH, JSON.stringify(ordenar(lock), null, 2) + '\n');
}

function subdirs(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name).sort();
}

// ---------- frontmatter ----------

/** Separa o bloco "---" inicial do corpo. Retorna { linhas, corpo }. */
function separarFrontmatter(texto) {
  const t = texto.replace(/\r\n/g, '\n');
  const m = t.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!m) falha('Frontmatter nao encontrado');
  return { linhas: m[1].split('\n'), corpo: t.slice(m[0].length) };
}

/** Agrupa linhas em entradas { chave, valor, linhas } por chave de nivel zero. */
function agruparEntradas(linhas) {
  const entradas = [];
  for (const l of linhas) {
    const m = l.match(/^([A-Za-z_][\w-]*):(.*)$/);
    if (m) entradas.push({ chave: m[1], valor: m[2].trim(), linhas: [l] });
    else if (entradas.length) entradas[entradas.length - 1].linhas.push(l);
  }
  return entradas;
}

function itensLista(entrada) {
  return entrada.linhas
    .slice(1)
    .map((l) => l.match(/^\s+-\s+(.+)$/))
    .filter(Boolean)
    .map((m) => m[1].trim());
}

// ---------- regras ----------

function converterRegra(texto, { curto, repo, sha, arquivo, versao }) {
  const { corpo } = separarFrontmatter(texto);
  const cab = [
    `# Padroes ${curto} (importado)`,
    '',
    `Origem: https://github.com/${ORG}/${repo}/blob/${sha}/rules/${arquivo} (versao ${versao})`,
    'Gerado por `.claude/scripts/importar-padroes.js`. Nao edite aqui: corrija no repo de origem e rode o script de novo.',
    '',
  ].join('\n');
  return cab + '\n' + corpo.replace(/^\n+/, '');
}

// ---------- agentes ----------

function converterAgente(texto) {
  const { linhas, corpo } = separarFrontmatter(texto);
  const entradas = agruparEntradas(linhas);
  const get = (k) => entradas.find((e) => e.chave === k);
  const nome = get('name') && get('name').valor;
  if (!nome) falha('Agente sem campo name');
  const ehSub = get('subagent') && get('subagent').valor === 'true';
  const permitidos = get('allowed_subagents') ? itensLista(get('allowed_subagents')) : [];
  const mantidos = entradas.filter((e) => !['subagent', 'allowed_subagents'].includes(e.chave));
  const saida = mantidos.flatMap((e) => e.linhas);
  let aviso = '';
  if (ehSub) {
    saida.push(`tools: ${TOOLS_BASE}`, 'model: sonnet');
  } else {
    if (!permitidos.length) falha(`Orquestrador ${nome} sem allowed_subagents`);
    saida.push(`tools: Agent(${permitidos.join(', ')}), ${TOOLS_BASE}`);
    aviso =
      `> Rode como agente da sessao principal: \`claude --agent ${nome}\`. ` +
      'No Claude Code um subagente nao chama outro subagente; so a sessao principal despacha os quatro especialistas.\n\n';
  }
  return { nome, conteudo: `---\n${saida.join('\n')}\n---\n\n${aviso}${corpo.replace(/^\n+/, '')}` };
}

// ---------- planejamento e seguranca ----------

function planejar(plugin) {
  const { dir } = plugin;
  const skills = subdirs(path.join(dir, 'skills'));
  const regras = fs.existsSync(path.join(dir, 'rules'))
    ? fs.readdirSync(path.join(dir, 'rules')).filter((f) => f.endsWith('.md')).sort()
    : [];
  if (regras.length !== 1) falha(`${plugin.repo}: esperava 1 regra em rules/, achei ${regras.length}`);
  const agentes = [];
  if (plugin.curto === 'business-blueprint') {
    const adir = path.join(dir, 'agents');
    for (const f of fs.readdirSync(adir).filter((x) => x.endsWith('.md')).sort()) {
      agentes.push(converterAgente(fs.readFileSync(path.join(adir, f), 'utf8')));
    }
  }
  return { skills, regra: regras[0], agentes };
}

function conjuntosGerenciados(lock) {
  const skills = new Set();
  const agentes = new Set();
  const dono = new Map();
  for (const [repo, p] of Object.entries(lock.plugins || {})) {
    for (const s of p.skills || []) {
      skills.add(s);
      dono.set(s, repo);
    }
    for (const a of p.agents || []) agentes.add(a);
  }
  return { skills, agentes, dono };
}

function validar(planos, lock) {
  const ger = conjuntosGerenciados(lock);
  const vistos = new Map();
  for (const { plugin, plano } of planos) {
    for (const s of plano.skills) {
      if (vistos.has(s)) falha(`Skill duplicada "${s}" em ${plugin.repo} e ${vistos.get(s)}`);
      vistos.set(s, plugin.repo);
      const outro = ger.dono.get(s);
      if (outro && outro !== plugin.repo) falha(`Skill "${s}" de ${plugin.repo} colide com a de ${outro} (lock)`);
      if (fs.existsSync(path.join(SKILLS_DIR, s)) && !ger.skills.has(s)) {
        falha(`.claude/skills/${s} ja existe e nao e gerenciada pelo lock. Nao sobrescrevo.`);
      }
    }
    for (const a of plano.agentes) {
      if (PROTEGIDOS.includes(a.nome)) falha(`Agente ${a.nome} e protegido`);
      if (fs.existsSync(path.join(AGENTS_DIR, `${a.nome}.md`)) && !ger.agentes.has(a.nome)) {
        falha(`.claude/agents/${a.nome}.md ja existe e nao e gerenciado pelo lock. Nao sobrescrevo.`);
      }
    }
  }
}

// ---------- escrita ----------

function copiarSkill(origem, nome) {
  const destino = path.join(SKILLS_DIR, nome);
  fs.rmSync(destino, { recursive: true, force: true });
  fs.cpSync(path.join(origem, 'skills', nome), destino, { recursive: true });
}

function aplicar(plugin, plano, versao) {
  fs.mkdirSync(SHARED_DIR, { recursive: true });
  fs.mkdirSync(AGENTS_DIR, { recursive: true });
  for (const s of plano.skills) copiarSkill(plugin.dir, s);
  const regraTxt = fs.readFileSync(path.join(plugin.dir, 'rules', plano.regra), 'utf8');
  const alvo = path.join(SHARED_DIR, `padroes-${plugin.curto}.md`);
  const dados = { curto: plugin.curto, repo: plugin.repo, sha: plugin.commit, arquivo: plano.regra, versao };
  fs.writeFileSync(alvo, converterRegra(regraTxt, dados));
  for (const a of plano.agentes) fs.writeFileSync(path.join(AGENTS_DIR, `${a.nome}.md`), a.conteudo);
}

function entradaLock(plugin, plano, versao) {
  return {
    repo: `${ORG}/${plugin.repo}`,
    url: `https://github.com/${ORG}/${plugin.repo}`,
    ref: REF,
    commit: plugin.commit,
    version: versao,
    skills: [...plano.skills].sort(),
    rule: `.claude/skills/_shared/padroes-${plugin.curto}.md`,
    agents: plano.agentes.map((a) => a.nome).sort(),
  };
}

/** Remove skills/agentes que o lock anterior tinha e a origem nao tem mais. */
function limparRemovidos(lock, repo, plano) {
  const anterior = lock.plugins[repo] || {};
  for (const s of anterior.skills || []) {
    if (!plano.skills.includes(s)) fs.rmSync(path.join(SKILLS_DIR, s), { recursive: true, force: true });
  }
  const nomes = plano.agentes.map((a) => a.nome);
  for (const a of anterior.agents || []) {
    if (!nomes.includes(a)) fs.rmSync(path.join(AGENTS_DIR, `${a}.md`), { force: true });
  }
}

// ---------- principal ----------

function relatar(plugin, plano, versao, dryRun) {
  const prefixo = dryRun ? '[dry-run]' : 'ok';
  console.log(
    `${prefixo} ${plugin.curto}: ${plano.skills.length} skills, regra ${plano.regra}, ` +
      `${plano.agentes.length} agentes (${plugin.commit.slice(0, 7)} v${versao})`
  );
  if (dryRun) {
    plano.skills.forEach((s) => console.log(`  skill ${s}`));
    plano.agentes.forEach((a) => console.log(`  agente ${a.nome}`));
  }
}

function preparar(curto, tmp, lock) {
  const repo = REPOS[curto];
  console.log(`clone ${repo}`);
  const plugin = { curto, repo, ...clonar(repo, tmp) };
  const versao = lerJson(path.join(plugin.dir, 'installed_version.json')).version;
  return { plugin, versao, plano: planejar(plugin, lock) };
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const curtos = opts.only ? [opts.only] : Object.keys(REPOS);
  const lock = lerLock();
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'importar-padroes-'));
  try {
    const planos = curtos.map((c) => preparar(c, tmp, lock));
    validar(planos, lock);
    for (const { plugin, versao, plano } of planos) {
      if (!opts.dryRun) {
        limparRemovidos(lock, plugin.repo, plano);
        aplicar(plugin, plano, versao);
        lock.plugins[plugin.repo] = entradaLock(plugin, plano, versao);
      }
      relatar(plugin, plano, versao, opts.dryRun);
    }
    if (!opts.dryRun) gravarLock(lock);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

try {
  main();
} catch (e) {
  console.error(`ERRO: ${e.message}`);
  process.exit(1);
}
