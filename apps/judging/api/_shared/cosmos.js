const { CosmosClient } = require('@azure/cosmos');

const DB_NAME = 'mtahack';
let _client = null;
let _db = null;
const _containers = {};

function getClient() {
  if (_client) return _client;
  const conn = process.env.COSMOS_CONNECTION_STRING;
  if (!conn) throw new Error('COSMOS_CONNECTION_STRING is not set');
  _client = new CosmosClient(conn);
  return _client;
}

function getDatabase() {
  if (_db) return _db;
  _db = getClient().database(DB_NAME);
  return _db;
}

function getContainer(name) {
  if (_containers[name]) return _containers[name];
  _containers[name] = getDatabase().container(name);
  return _containers[name];
}

module.exports = { getClient, getDatabase, getContainer, DB_NAME };
