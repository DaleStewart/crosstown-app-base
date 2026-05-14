// @ts-check
/**
 * Shared helpers for stubbing /.auth/me and core API endpoints so E2E tests
 * never touch real AAD or real Cosmos DB.
 */
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const ANON = { clientPrincipal: null };

function principal(roles, email) {
  return {
    clientPrincipal: {
      identityProvider: 'aad',
      userId: 'test-user-id',
      userDetails: email || 'judge@microsoft.com',
      userRoles: ['anonymous', 'authenticated'].concat(roles || [])
    }
  };
}

/**
 * Stub /.auth/me on the given page.
 *   kind: 'anon' | 'judge' | 'admin'
 */
async function stubAuth(page, kind) {
  let body = ANON;
  if (kind === 'judge') body = principal([], 'judge@microsoft.com');
  if (kind === 'admin') body = principal(['admin'], 'admin@microsoft.com');
  await page.route('**/.auth/me', function (route) {
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(body)
    });
  });
}

function sampleTeams() {
  return [
    { id: 't1', name: 'Team Aurora', track: 'azure', members: ['Ada Lovelace', 'Alan Turing'], room: 'Room 1', slot: '10:00 AM' },
    { id: 't2', name: 'Team Borealis', track: 'azure', members: ['Grace Hopper'], room: 'Room 2', slot: '10:30 AM' },
    { id: 't3', name: 'Team Cosmos', track: 'azure', members: ['Linus Torvalds'], room: 'Room 3', slot: '11:00 AM' }
  ];
}

function sampleLeaderboard() {
  return [
    { rank: 1, teamId: 't1', teamName: 'Team Aurora', avgTotal: 92.5, judgeCount: 3, tieBreakerAvg: 4.8, avgPerCriterion: { alignment: 4.7, architecture: 4.9, reliability: 4.6, ux: 4.5, demo: 4.6 } },
    { rank: 2, teamId: 't2', teamName: 'Team Borealis', avgTotal: 78.0, judgeCount: 3, tieBreakerAvg: 4.0, avgPerCriterion: {} },
    { rank: 3, teamId: 't3', teamName: 'Team Cosmos', avgTotal: 61.3, judgeCount: 2, tieBreakerAvg: 3.2, avgPerCriterion: {} }
  ];
}

function jsonRoute(payload, status) {
  return function (route) {
    return route.fulfill({
      status: status || 200,
      contentType: 'application/json',
      body: typeof payload === 'string' ? payload : JSON.stringify(payload)
    });
  };
}

/**
 * Intercept /shared/criteria.js so the scorecard page gets the real module
 * even when the static server is rooted at apps/judging/src/ (which has no
 * shared/ subdirectory).
 */
async function stubCriteria(page) {
  const criteriaPath = path.join(__dirname, '..', '..', 'shared', 'criteria.js');
  const criteriaSource = fs.readFileSync(criteriaPath, 'utf8');
  await page.route('**/shared/criteria.js', function (route) {
    return route.fulfill({
      status: 200,
      contentType: 'application/javascript',
      body: criteriaSource
    });
  });
}

module.exports = {
  stubAuth,
  stubCriteria,
  sampleTeams,
  sampleLeaderboard,
  jsonRoute
};
