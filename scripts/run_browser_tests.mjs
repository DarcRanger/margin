#!/usr/bin/env node

import { spawn } from 'node:child_process'
import { createServer } from 'node:net'
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const ui = join(root, 'ui')
const temporaryRoot = mkdtempSync(join(tmpdir(), 'margin-browser-'))
const workspace = join(temporaryRoot, 'workspace')
const config = join(temporaryRoot, 'config')
mkdirSync(join(workspace, 'chapters'), { recursive: true })
mkdirSync(config, { recursive: true })
writeFileSync(
  join(workspace, 'chapters', 'Fixture_Chapter.md'),
  '# Fixture Chapter\n\nA generic sentence for browser acceptance.\n',
  'utf8',
)
writeFileSync(
  join(workspace, 'chapters', 'Lifecycle_First.md'),
  '# Lifecycle First\n\nA first lifecycle sentence.\n',
  'utf8',
)
writeFileSync(
  join(workspace, 'chapters', 'Lifecycle_Second.md'),
  '# Lifecycle Second\n\nA second lifecycle sentence.\n',
  'utf8',
)

function availablePort() {
  return new Promise((resolvePort, reject) => {
    const server = createServer()
    server.unref()
    server.on('error', reject)
    server.listen(0, '127.0.0.1', () => {
      const address = server.address()
      if (!address || typeof address === 'string') return reject(new Error('Could not allocate port'))
      const port = address.port
      server.close(() => resolvePort(port))
    })
  })
}

async function waitFor(url, process, name) {
  const deadline = Date.now() + 30_000
  while (Date.now() < deadline) {
    if (process.exitCode !== null) throw new Error(`${name} exited before becoming ready`)
    try {
      const response = await fetch(url)
      if (response.ok) return
    } catch { /* server is still starting */ }
    await new Promise(resolveWait => setTimeout(resolveWait, 200))
  }
  throw new Error(`${name} did not become ready at ${url}`)
}

function stop(process) {
  if (process.exitCode === null) process.kill('SIGTERM')
}

const apiPort = await availablePort()
const uiPort = await availablePort()
const apiUrl = `http://127.0.0.1:${apiPort}`
const uiUrl = `http://127.0.0.1:${uiPort}`
const isolatedEnv = {
  ...process.env,
  MARGIN_CONFIG_DIR: config,
  MARGIN_WORKSPACE_DIR: workspace,
}

const api = spawn(
  process.env.PYTHON || process.env.PYTHON3 || (process.platform === 'win32' ? 'python' : 'python3'),
  ['-m', 'uvicorn', 'api.main:app', '--host', '127.0.0.1', '--port', String(apiPort)],
  { cwd: root, env: isolatedEnv, stdio: 'inherit' },
)
const vite = spawn(
  process.execPath,
  [join(ui, 'node_modules', 'vite', 'bin', 'vite.js'), '--host', '127.0.0.1', '--port', String(uiPort), '--strictPort'],
  { cwd: ui, env: { ...isolatedEnv, VITE_API_BASE: apiUrl }, stdio: 'inherit' },
)

let exitCode = 1
try {
  await Promise.all([waitFor(`${apiUrl}/`, api, 'Margin API'), waitFor(uiUrl, vite, 'Margin UI')])
  const playwright = spawn(
    process.execPath,
    [join(ui, 'node_modules', '@playwright', 'test', 'cli.js'), 'test', '--config', join(ui, 'playwright.config.ts')],
    {
      cwd: ui,
      env: {
        ...isolatedEnv,
        MARGIN_BROWSER_BASE_URL: uiUrl,
        MARGIN_BROWSER_WORKSPACE: workspace,
      },
      stdio: 'inherit',
    },
  )
  exitCode = await new Promise((resolveExit, reject) => {
    playwright.on('error', reject)
    playwright.on('exit', code => resolveExit(code ?? 1))
  })
} finally {
  stop(vite)
  stop(api)
  rmSync(temporaryRoot, { recursive: true, force: true })
}

process.exitCode = exitCode
