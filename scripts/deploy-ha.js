/**
 * Deploy custom_components/voice_satellite_llm_tools_plus to the Home
 * Assistant box.  Cross-platform replacement for the old Windows-only
 * xcopy step in the npm dev script.
 */
const fs = require('fs');
const path = require('path');

const src = path.resolve(__dirname, '../custom_components/voice_satellite_llm_tools_plus');
const ATTEMPTS_PER_TARGET = 3;
const RETRY_DELAY_MS = 2000;

function candidateBases() {
  const bases = [];
  if (process.env.HA_DEPLOY_TARGET) bases.push(process.env.HA_DEPLOY_TARGET);
  if (process.platform === 'win32') bases.push('\\\\hassio\\config');
  else if (process.platform === 'darwin') bases.push('/Volumes/hassio/config');
  else bases.push('/mnt/hassio', '/mnt/hassio-smb', '/mnt/hassio/config', '/config');
  return bases;
}

function findConfigDir(base) {
  for (const dir of [base, path.join(base, 'config')]) {
    try {
      if (fs.existsSync(path.join(dir, 'configuration.yaml'))) return dir;
    } catch {
      // unreachable mount - treat as not found
    }
  }
  return null;
}

function revalidateStaleDir(dir) {
  let st;
  try {
    st = fs.statSync(dir);
  } catch {
    return true;
  }
  if (st.nlink !== 0) return true;

  console.warn(`deploy-ha: ${dir} looks like a stale NFS handle, revalidating...`);
  try { fs.rmdirSync(dir); } catch {}
  try { fs.mkdirSync(dir, { recursive: true }); } catch {}
  const probe = path.join(dir, '.deploy-ha-probe');
  try {
    fs.writeFileSync(probe, '');
    fs.unlinkSync(probe);
  } catch {}

  try {
    return fs.statSync(dir).nlink !== 0;
  } catch {
    return true;
  }
}

function copyTree(dst) {
  let count = 0;
  fs.cpSync(src, dst, {
    recursive: true,
    force: true,
    filter: (p) => {
      if (path.basename(p) === '__pycache__') return false;
      if (fs.statSync(p).isFile()) count += 1;
      return true;
    },
  });
  return count;
}

function verifyDeploy(dst) {
  const marker = 'manifest.json';
  const expected = fs.readFileSync(path.join(src, marker));
  const actual = fs.readFileSync(path.join(dst, marker));
  if (!expected.equals(actual)) {
    throw new Error(`${marker} read back from ${dst} does not match the source`);
  }
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function deployTo(dst) {
  let lastErr;
  for (let attempt = 1; attempt <= ATTEMPTS_PER_TARGET; attempt += 1) {
    try {
      if (!revalidateStaleDir(dst)) {
        throw new Error(`${dst} is a stale NFS handle the client cannot clear`);
      }
      const count = copyTree(dst);
      verifyDeploy(dst);
      return count;
    } catch (err) {
      lastErr = err;
      if (attempt < ATTEMPTS_PER_TARGET) {
        console.warn(`deploy-ha: attempt ${attempt} failed (${err.message}), retrying...`);
        await sleep(RETRY_DELAY_MS * attempt);
      }
    }
  }
  throw lastErr;
}

(async () => {
  const tried = [];
  for (const base of candidateBases()) {
    const configDir = findConfigDir(base);
    if (!configDir) {
      tried.push(`${base} (no configuration.yaml found)`);
      continue;
    }
    const dst = path.join(configDir, 'custom_components', 'voice_satellite_llm_tools_plus');
    try {
      const count = await deployTo(dst);
      console.log(`LLM Tools+ deployed: ${count} files -> ${dst}`);
      return;
    } catch (err) {
      tried.push(`${dst} (${err.message})`);
      console.warn(`deploy-ha: giving up on ${dst}, trying next target...`);
    }
  }

  console.error(
    'deploy-ha: could not deploy to any Home Assistant target.\n'
    + (tried.length ? `Tried:\n  - ${tried.join('\n  - ')}\n` : '')
    + 'Mount the HA config share (\\\\hassio\\config on Windows, '
    + '/Volumes/hassio on macOS, /mnt/hassio-smb or /mnt/hassio/config on '
    + 'Linux) or set HA_DEPLOY_TARGET to the HA config directory.',
  );
  process.exit(1);
})();
