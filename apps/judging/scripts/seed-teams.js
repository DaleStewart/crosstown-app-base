#!/usr/bin/env node
/*
 * seed-teams.js — bulk-create teams in the MTA Hackathon judging app.
 *
 * Reads a CSV (header: name,track,members,room,slot ; members is ';'-separated)
 * and POSTs each row to <url>/api/teams.
 *
 * Usage:
 *   node seed-teams.js --url https://<swa-hostname>.azurestaticapps.net \
 *                      --csv ./teams.csv \
 *                      [--token <auth-cookie-or-function-key>]
 *
 * Auth notes (the /api/teams admin route is AAD role-gated):
 *   1. Easiest: copy the `StaticWebAppsAuthCookie` from a signed-in admin's
 *      browser session (DevTools → Application → Cookies) and pass via --token.
 *   2. Local dev: run `swa start ./src --api-location ./api` and use the auth
 *      simulator at http://localhost:4280/.auth/me to set role=admin, then
 *      point --url at http://localhost:4280 (no --token needed).
 *   3. Fallback: insert team documents directly via the Cosmos DB Data Explorer
 *      matching the schema in apps/judging/shared/criteria.js.
 *
 * Requires Node 20+ (uses built-in fetch). No npm install needed.
 */

'use strict';

const fs = require('node:fs');
const path = require('node:path');

const REQUIRED_COLUMNS = ['name', 'track', 'members', 'room', 'slot'];

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--url') out.url = argv[++i];
    else if (a === '--csv') out.csv = argv[++i];
    else if (a === '--token') out.token = argv[++i];
    else if (a === '-h' || a === '--help') out.help = true;
  }
  return out;
}

function usage() {
  console.log(
    'Usage: node seed-teams.js --url <swa-url> --csv <path> [--token <auth-cookie-or-key>]'
  );
}

// Minimal CSV parser supporting quoted fields and embedded commas/quotes.
function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = '';
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; }
        else { inQuotes = false; }
      } else {
        field += c;
      }
    } else {
      if (c === '"') inQuotes = true;
      else if (c === ',') { row.push(field); field = ''; }
      else if (c === '\n') { row.push(field); rows.push(row); row = []; field = ''; }
      else if (c === '\r') { /* skip */ }
      else field += c;
    }
  }
  // Flush last field/row if file doesn't end in newline.
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

function isBlankRow(row) {
  return row.every((v) => v === undefined || String(v).trim() === '');
}

async function postTeam(baseUrl, team, token) {
  const url = baseUrl.replace(/\/+$/, '') + '/api/teams';
  const headers = { 'content-type': 'application/json' };
  if (token) {
    // Heuristic: if it looks like a cookie value, send as Cookie header; else
    // treat as a function key / bearer token.
    if (/=/.test(token) || /StaticWebAppsAuthCookie/i.test(token)) {
      headers['cookie'] = /StaticWebAppsAuthCookie=/i.test(token)
        ? token
        : `StaticWebAppsAuthCookie=${token}`;
    } else {
      headers['x-functions-key'] = token;
      headers['authorization'] = `Bearer ${token}`;
    }
  }
  const res = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(team),
  });
  let body = '';
  try { body = await res.text(); } catch { /* ignore */ }
  return { status: res.status, ok: res.ok, body };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || !args.url || !args.csv) {
    usage();
    process.exit(args.help ? 0 : 2);
  }

  const csvPath = path.resolve(args.csv);
  if (!fs.existsSync(csvPath)) {
    console.error(`CSV not found: ${csvPath}`);
    process.exit(2);
  }
  const text = fs.readFileSync(csvPath, 'utf8');
  const rows = parseCsv(text);
  if (rows.length === 0) {
    console.error('CSV is empty.');
    process.exit(2);
  }

  const header = rows[0].map((h) => String(h).trim().toLowerCase());
  for (const col of REQUIRED_COLUMNS) {
    if (!header.includes(col)) {
      console.error(`Missing required column: ${col}. Expected: ${REQUIRED_COLUMNS.join(',')}`);
      process.exit(2);
    }
  }
  const idx = Object.fromEntries(REQUIRED_COLUMNS.map((c) => [c, header.indexOf(c)]));

  let ok = 0;
  let fail = 0;
  let skipped = 0;

  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row || isBlankRow(row)) { skipped++; continue; }
    const name = String(row[idx.name] ?? '').trim();
    const track = String(row[idx.track] ?? '').trim();
    const membersRaw = String(row[idx.members] ?? '').trim();
    const room = String(row[idx.room] ?? '').trim();
    const slot = String(row[idx.slot] ?? '').trim();

    if (!name || !track) {
      console.error(`row ${i}: SKIP (missing name or track)`);
      skipped++;
      continue;
    }

    const team = {
      name,
      track,
      members: membersRaw ? membersRaw.split(';').map((m) => m.trim()).filter(Boolean) : [],
      room,
      slot,
    };

    try {
      const { status, ok: success, body } = await postTeam(args.url, team, args.token);
      if (success) {
        console.log(`row ${i}: OK  ${status}  ${name} (${track})`);
        ok++;
      } else {
        const snippet = (body || '').replace(/\s+/g, ' ').slice(0, 200);
        console.error(`row ${i}: FAIL ${status} ${name} (${track}) :: ${snippet}`);
        fail++;
      }
    } catch (err) {
      console.error(`row ${i}: ERROR ${name} (${track}) :: ${err.message || err}`);
      fail++;
    }
  }

  console.log(`\nDone. ok=${ok} fail=${fail} skipped=${skipped}`);
  process.exit(fail > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error('Fatal:', err);
  process.exit(1);
});
