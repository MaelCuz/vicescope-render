const entries = $input.all();
const text = value => typeof value === 'string' ? value.replace(/\s+/g, ' ').trim() : '';
return entries.map((item, index) => {
  const data = item.json || {};
  const reasons = [];
  const narration = text(data.narration);
  const title = text(data.title);
  const subtitle = text(data.subtitle);
  const safety = data.safety || {};
  if (!narration || narration.length > 1200) reasons.push('INVALID_NARRATION');
  if (!title || title.length > 50) reasons.push('INVALID_TITLE');
  if (!subtitle || subtitle.length > 70) reasons.push('INVALID_SUBTITLE');
  if (data.language !== 'en-US') reasons.push('INVALID_LANGUAGE');
  if (data.status !== 'READY_FOR_HUMAN_REVIEW') reasons.push('EDITORIAL_REVIEW_PENDING');
  if (data.factCheck?.independentVerification !== true) reasons.push('FACTUAL_REVIEW_PENDING');
  if (!Array.isArray(data.factCheck?.pendingClaims) || data.factCheck.pendingClaims.length) reasons.push('UNRESOLVED_FACTUAL_CLAIMS');
  if (safety.approvedForProduction !== true || data.renderAllowed !== true) reasons.push('PRODUCTION_APPROVAL_PENDING');
  if (safety.noAutomaticPublishing !== true) reasons.push('PUBLICATION_POLICY_INVALID');
  const ready = reasons.length === 0;
  return {
    json: {
      ...data,
      productionJob: {
        schema: 'vicescope.production-job.v1',
        candidateId: text(data.candidateId),
        state: ready ? 'READY_TO_DISPATCH' : 'BLOCKED',
        blockers: reasons,
        repository: 'MaelCuz/vicescope-render',
        method: 'POST',
        dispatchUrl: 'https://api.github.com/repos/MaelCuz/vicescope-render/actions/workflows/render.yml/dispatches',
        requiredCredentialType: 'githubApi',
        dispatchPerformed: false,
        requestBody: ready ? {
          ref: 'main',
          inputs: {narration, title, subtitle, voice: 'am_adam', speed: '1.08'}
        } : null,
        artifactsExpected: ['ViceScope-Video', 'ViceScope-Audio', 'ViceScope-OpenCut-Media'],
        publicationAllowed: false
      }
    },
    pairedItem: {item: index}
  };
});