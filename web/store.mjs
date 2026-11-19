// Where accounts and sessions are kept. PgStore is used when DATABASE_URL is set (Replit's Postgres);
// MemoryStore is for tests and local runs, and forgets everything on restart.

export class MemoryStore {
  constructor() { this.users = new Map(); this.sessions = new Map(); this.setups = new Map(); this.next = 1; }
  async init() {}
  async countUsers() { return this.users.size; }
  async getUserByEmail(email) { return [...this.users.values()].find((u) => u.email === email) || null; }
  async getUser(id) { return this.users.get(id) || null; }
  async createUser(u) {
    if (await this.getUserByEmail(u.email)) throw new Error('exists');
    const row = { id: this.next++, failedCount: 0, lockedUntil: 0, lastStep: -1, recovery: [], ...u };
    this.users.set(row.id, row); return row;
  }
  async updateUser(id, fields) { const u = this.users.get(id); if (u) Object.assign(u, fields); return u; }
  async claimStep(id, step) { const u = this.users.get(id); if (!u || u.lastStep >= step) return false; u.lastStep = step; return true; }
  async useRecovery(id, hash) {
    const u = this.users.get(id); if (!u || !u.recovery.includes(hash)) return false;
    u.recovery = u.recovery.filter((h) => h !== hash); return true;
  }
  async putSession(s) { this.sessions.set(s.tokenHash, { ...s }); }
  async getSession(h) { const s = this.sessions.get(h); return s && s.expiresAt > Date.now() ? s : null; }
  async deleteSession(h) { this.sessions.delete(h); }
  async putSetup(s) { this.setups.set(s.tokenHash, { ...s }); }
  async getSetup(h) { const s = this.setups.get(h); return s && s.expiresAt > Date.now() ? s : null; }
  async deleteSetup(h) { this.setups.delete(h); }
}

const SCHEMA = `
create table if not exists lob_users (
  id serial primary key,
  email text unique not null,
  pw_hash text not null,
  totp_secret text not null,
  recovery text[] not null default '{}',
  last_step bigint not null default -1,
  failed_count int not null default 0,
  locked_until bigint not null default 0,
  created_at timestamptz not null default now()
);
create table if not exists lob_sessions (
  token_hash text primary key,
  user_id int not null references lob_users(id) on delete cascade,
  stage text not null,
  expires_at bigint not null,
  created_at timestamptz not null default now()
);
create table if not exists lob_setups (
  token_hash text primary key,
  email text not null,
  pw_hash text not null,
  totp_secret text not null,
  expires_at bigint not null
);`;

const user = (r) => r && ({ id: r.id, email: r.email, pwHash: r.pw_hash, totpSecret: r.totp_secret, recovery: r.recovery,
  lastStep: Number(r.last_step), failedCount: r.failed_count, lockedUntil: Number(r.locked_until) });
const COLS = { failedCount: 'failed_count', lockedUntil: 'locked_until', lastStep: 'last_step', pwHash: 'pw_hash', totpSecret: 'totp_secret', recovery: 'recovery' };

export class PgStore {
  constructor(url) { this.url = url; }
  async init() {
    const { default: pg } = await import('pg');
    const local = /localhost|127\.0\.0\.1|helium/.test(this.url) || /sslmode=disable/.test(this.url);
    this.pool = new pg.Pool({ connectionString: this.url, max: 5, ssl: local ? undefined : { rejectUnauthorized: false } });
    await this.pool.query(SCHEMA);
    await this.pool.query('delete from lob_sessions where expires_at < $1', [Date.now()]);
    await this.pool.query('delete from lob_setups where expires_at < $1', [Date.now()]);
  }
  q(sql, args) { return this.pool.query(sql, args); }
  async countUsers() { return Number((await this.q('select count(*)::int as n from lob_users')).rows[0].n); }
  async getUserByEmail(e) { return user((await this.q('select * from lob_users where email = $1', [e])).rows[0]); }
  async getUser(id) { return user((await this.q('select * from lob_users where id = $1', [id])).rows[0]); }
  async createUser(u) {
    const r = await this.q('insert into lob_users (email, pw_hash, totp_secret, recovery, last_step) values ($1,$2,$3,$4,$5) returning *',
      [u.email, u.pwHash, u.totpSecret, u.recovery || [], u.lastStep ?? -1]);
    return user(r.rows[0]);
  }
  async updateUser(id, fields) {
    const keys = Object.keys(fields).filter((k) => COLS[k]);
    if (!keys.length) return this.getUser(id);
    const sets = keys.map((k, i) => `${COLS[k]} = $${i + 2}`).join(', ');
    return user((await this.q(`update lob_users set ${sets} where id = $1 returning *`, [id, ...keys.map((k) => fields[k])])).rows[0]);
  }
  async claimStep(id, step) { return (await this.q('update lob_users set last_step = $2 where id = $1 and last_step < $2', [id, step])).rowCount === 1; }
  async useRecovery(id, hash) {
    return (await this.q('update lob_users set recovery = array_remove(recovery, $2) where id = $1 and $2 = any(recovery)', [id, hash])).rowCount === 1;
  }
  async putSession(s) {
    await this.q('insert into lob_sessions (token_hash, user_id, stage, expires_at) values ($1,$2,$3,$4)', [s.tokenHash, s.userId, s.stage, s.expiresAt]);
  }
  async getSession(h) {
    const r = (await this.q('select * from lob_sessions where token_hash = $1 and expires_at > $2', [h, Date.now()])).rows[0];
    return r && { tokenHash: r.token_hash, userId: r.user_id, stage: r.stage, expiresAt: Number(r.expires_at) };
  }
  async deleteSession(h) { await this.q('delete from lob_sessions where token_hash = $1', [h]); }
  async putSetup(s) {
    await this.q('insert into lob_setups (token_hash, email, pw_hash, totp_secret, expires_at) values ($1,$2,$3,$4,$5)', [s.tokenHash, s.email, s.pwHash, s.totpSecret, s.expiresAt]);
  }
  async getSetup(h) {
    const r = (await this.q('select * from lob_setups where token_hash = $1 and expires_at > $2', [h, Date.now()])).rows[0];
    return r && { tokenHash: r.token_hash, email: r.email, pwHash: r.pw_hash, totpSecret: r.totp_secret, expiresAt: Number(r.expires_at) };
  }
  async deleteSetup(h) { await this.q('delete from lob_setups where token_hash = $1', [h]); }
}
