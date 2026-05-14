const { getContainer } = require('../_shared/cosmos');
const { requireAuth } = require('../_shared/auth');
const { CRITERIA } = require('../_shared/criteria');

module.exports = async function (context, req) {
  const { res: authRes } = requireAuth(req);
  if (authRes) { context.res = authRes; return; }

  const track = (req.query.track || '').toLowerCase();
  if (!CRITERIA[track]) {
    context.res = { status: 400, body: { error: 'track query param must be one of: azure, copilot' } };
    return;
  }

  try {
    const container = getContainer('teams');
    const { resources } = await container.items.query({
      query: 'SELECT * FROM c WHERE c.track = @t',
      parameters: [{ name: '@t', value: track }]
    }, { partitionKey: track }).fetchAll();

    context.res = { status: 200, headers: { 'Content-Type': 'application/json' }, body: resources };
  } catch (err) {
    context.log.error('teams-list failed', err);
    context.res = { status: 500, body: { error: 'Failed to list teams' } };
  }
};
