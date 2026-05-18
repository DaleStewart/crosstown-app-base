const { getContainer } = require('../_shared/cosmos');
const { requireAuth } = require('../_shared/auth');
const { CRITERIA } = require('../_shared/criteria');

module.exports = async function (context, req) {
  try {
    const { user, res: authRes } = requireAuth(req);
    if (authRes) { context.res = authRes; return; }

    const track = (req.query.track || '').toLowerCase();
    if (!CRITERIA[track]) {
      context.res = { status: 400, body: { error: 'track query param must be one of: azure, copilot' } };
      return;
    }

    const container = getContainer('scores');
    const { resources } = await container.items.query({
      query: 'SELECT * FROM c WHERE c.judgeEmail = @e AND c.track = @t',
      parameters: [
        { name: '@e', value: user.email },
        { name: '@t', value: track }
      ]
    }, { partitionKey: track }).fetchAll();

    context.res = { status: 200, headers: { 'Content-Type': 'application/json' }, body: resources };
  } catch (err) {
    context.log.error('myscores failed', { code: err && err.code, message: err && err.message, stack: err && err.stack });
    context.res = {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
      body: { error: 'Failed to load scores', code: err && err.code, detail: err && err.message }
    };
  }
};
