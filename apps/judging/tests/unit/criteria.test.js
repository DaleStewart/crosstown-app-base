#!/usr/bin/env node
/**
 * Pure-Node smoke test for shared/criteria.js — no Playwright, no browser.
 * Run with: node unit/criteria.test.js  (or `npm run test:unit`)
 */
'use strict';

const assert = require('node:assert');
const path = require('node:path');

const { computeTotal, tier } = require(path.join('..', '..', 'shared', 'criteria.js'));

let passed = 0;
let failed = 0;

function check(name, fn) {
  try {
    fn();
    passed++;
    console.log('  PASS  ' + name);
  } catch (err) {
    failed++;
    console.error('  FAIL  ' + name);
    console.error('        ' + (err && err.message ? err.message : err));
  }
}

console.log('criteria.js — unit smoke');

check('azure: all 5s = 100', function () {
  assert.strictEqual(
    computeTotal('azure', { alignment: 5, architecture: 5, reliability: 5, ux: 5, demo: 5 }),
    100
  );
});

check('azure: all 1s = 20', function () {
  assert.strictEqual(
    computeTotal('azure', { alignment: 1, architecture: 1, reliability: 1, ux: 1, demo: 1 }),
    20
  );
});

check('copilot: all 5s = 100', function () {
  assert.strictEqual(
    computeTotal('copilot', { alignment: 5, design: 5, actions: 5, branding: 5, demo: 5 }),
    100
  );
});

check('azure: mixed scores match hand-computed weighted total (66)', function () {
  // 3*0.20*20 + 4*0.30*20 + 3*0.20*20 + 3*0.15*20 + 3*0.15*20
  // = 12 + 24 + 12 + 9 + 9 = 66
  assert.strictEqual(
    computeTotal('azure', { alignment: 3, architecture: 4, reliability: 3, ux: 3, demo: 3 }),
    66
  );
});

check('missing criterion returns null', function () {
  assert.strictEqual(
    computeTotal('azure', { alignment: 5, architecture: 5, reliability: 5, ux: 5 }),
    null
  );
});

check('tier(95) === "Exceptional"', function () {
  assert.strictEqual(tier(95), 'Exceptional');
});

check('tier(75) === "Strong"', function () {
  assert.strictEqual(tier(75), 'Strong');
});

check('tier(55) === "Developing"', function () {
  assert.strictEqual(tier(55), 'Developing');
});

check('tier(30) === "Needs work"', function () {
  assert.strictEqual(tier(30), 'Needs work');
});

console.log('');
console.log(passed + ' passed, ' + failed + ' failed');

if (failed > 0) process.exit(1);
