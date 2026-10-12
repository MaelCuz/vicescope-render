import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '../..');
const read = p => fs.readFileSync(path.join(root, p), 'utf8');
const json = p => JSON.parse(read(p));
const assert = (ok, message) => { if (!ok) throw new Error(message); };

const radar = json('n8n/vicescope-01-radar-gta6.json');
const flow2 = json('n8n/vicescope-02-editorial-master.json');
const policy = json('n8n/vicescope-master-policy.json');
const prompt = read('n8n/prompts/vicescope-editorial-master.md');
const renderYml = read('.github/workflows/render.yml');
const renderPy = read('vicescope-render/render.py');
const audioPy = read('vicescope-render/generate_audio.py');

const nodeMap = workflow => new Map(workflow.nodes.map(node => [node.name, node]));
const validateConnections = workflow => {
  const names = new Set(workflow.nodes.map(node => node.name));
  for (const [source, groups] of Object.entries(workflow.connections || {})) {
    assert(names.has(source), `Connection source missing: ${source}`);
    for (const branch of groups.main || []) {
      for (const edge of branch) assert(names.has(edge.node), `Connection target missing: ${edge.node}`);
    }
  }
};

validateConnections(radar);
validateConnections(flow2);
assert(radar.name.includes('Master 1.2.0'), 'Radar version mismatch');
assert(flow2.name.includes('Editorial Master'), 'Flow 02 name mismatch');

const radarNodes = nodeMap(radar);
const filterCode = radarNodes.get('Filtrar pontuar e remover duplicados').parameters.jsCode;
const prepareCode = radarNodes.get('Preparar lote para IA').parameters.jsCode;
const flowNodes = nodeMap(flow2);
const masterCode = flowNodes.get('Aplicar raciocinio Master').parameters.jsCode;
const consolidateCode = flowNodes.get('Montar pacote editorial').parameters.jsCode;

const runFilter = new Function('$input', '$getWorkflowStaticData', filterCode);
const runPrepare = new Function('$input', prepareCode);
const runMaster = new Function('$input', masterCode);
const runConsolidate = new Function('$input', consolidateCode);

const now = new Date().toISOString();
const fakeInput = { all: () => [
  { json: {
    title: 'Lucia leaked clip allegedly shows naked scene - IGN',
    link: 'https://news.google.com/rss/articles/master-test?oc=5',
    contentSnippet: 'A leaked GTA 6 clip allegedly shows Lucia during a mission.',
    creator: 'IGN',
    isoDate: now
  }},
  { json: {
    title: 'Grand Theft Auto VI official trailer - Rockstar Games',
    link: 'https://www.rockstargames.com/VI',
    contentSnippet: 'Official GTA VI trailer featuring Lucia and Jason.',
    creator: 'Rockstar Games',
    isoDate: now
  }},
  { json: {
    title: 'Best earbuds deal compared with GTA 6 - Store',
    link: 'https://example.com/deal',
    contentSnippet: 'Buy now.',
    creator: 'Store',
    isoDate: now
  }}
]};

const staticMemory = {};
const filtered = runFilter(fakeInput, () => staticMemory).map(x => x.json);
assert(filtered.length === 2, 'Radar filter or junk removal failed');
const adult = filtered.find(x => x.topic === 'adult-content');
const official = filtered.find(x => x.official);
assert(adult, 'Adult-topic candidate missing');
assert(adult.creativeLead === 'lucia', 'Lucia routing failed');
assert(adult.manualApprovalRequired, 'Adult manual approval missing');
assert(adult.leakedMediaForbidden, 'Leak media prohibition missing');
assert(adult.visualRestrictions.includes('no_nudity'), 'Adult visual safety missing');
assert(official?.creativeLead === 'lucia_and_jason', 'Official duo routing failed');

const preparedItems = runPrepare({ all: () => filtered.map(item => ({ json: item })) });
const batch = preparedItems[0].json;
assert(batch.schemaVersion === '1.2', 'Radar schema version mismatch');
assert(batch.policyVersion === 'vicescope-master-1.0', 'Policy version mismatch');
assert(batch.editorialRules.noAutomaticPublishing, 'Auto-publish must remain off');
assert(batch.masterCreativeRules.imageGeneration.realismQualityGate.required, 'Realism gate missing');
assert(batch.masterCreativeRules.assetPolicy.directOriginRequiredForOfficialLabel, 'Official-source gate missing');

const packages = runMaster({ all: () => preparedItems });
assert(packages.length === 2, 'Flow 02 package count mismatch');
for (const item of packages) {
  const brief = item.json.creativeBrief;
  assert(brief.thumbnailVariants.length === 3, 'Must create three thumbnail variants');
  assert(brief.sourceTruth.official === false, 'Generated concept must not claim official status');
  assert(brief.realismQualityChecklist.length >= 6, 'Realism checklist incomplete');
  assert(brief.rejectGeneratedImageIfAnyChecklistItemFails, 'Failed image rejection gate missing');
}
const consolidated = runConsolidate({ all: () => packages });
assert(consolidated[0].json.manualApprovalRequired, 'Flow 02 approval gate missing');
assert(consolidated[0].json.noAutomaticPublishing, 'Flow 02 auto-publish must remain off');

assert(policy.generatedImages.realismQualityGate.required, 'Policy realism gate missing');
assert(policy.generatedImages.sourceTruth.includes('nunca'), 'Policy source-truth statement missing');
assert(policy.officialAssets.luciaRedBikiniBeach.status.includes('pending'), 'Unverified official image must remain pending');
assert(prompt.includes('Controle de realismo'), 'Editorial prompt realism section missing');

for (const voice of ['am_adam', 'am_michael', 'af_heart', 'af_bella']) {
  assert(renderYml.includes(voice) || audioPy.includes(voice), `Missing voice: ${voice}`);
}
for (const speed of ['0.95', '1.00', '1.08', '1.15']) {
  assert(renderYml.includes(`"${speed}"`), `Missing speed: ${speed}`);
}
assert(renderPy.includes('1200'), 'Narration limit mismatch');
assert(renderPy.includes('50).upper()'), 'Title limit mismatch');
assert(/70,\s*\)\.upper\(\)/m.test(renderPy), 'Subtitle limit mismatch');

const secretPatterns = [/AIza[0-9A-Za-z_-]{20,}/, /ghp_[0-9A-Za-z]{20,}/, /github_pat_[0-9A-Za-z_]{20,}/];
for (const [name, value] of Object.entries({filterCode, prepareCode, masterCode, consolidateCode, prompt})) {
  for (const pattern of secretPatterns) assert(!pattern.test(value), `Possible secret in ${name}`);
}

console.log(JSON.stringify({
  status: 'PASS',
  checks: 31,
  radarCandidates: filtered.length,
  flow2Packages: packages.length,
  thumbnailVariantsPerCandidate: 3,
  sourceTruth: 'generated concepts remain non-official',
  publishing: 'manual approval required'
}, null, 2));
