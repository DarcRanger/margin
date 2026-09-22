import { useEffect, useRef, useState } from 'react'
import { API_BASE } from '../lib/api'
import {
  createPilotActionGate,
  exportButtonAppearance,
  finishPilotSession,
  INELIGIBLE_PILOT_SOURCE_GUIDANCE,
  isEligiblePilotSource,
  pilotControls,
  pilotStatusGuidance,
} from '../lib/pilotControls'
import { useEditorStore, type PilotState } from '../stores/editorStore'

async function action(path: 'start' | 'reset' | 'export' | 'finish', body: object): Promise<PilotState | { path: string; sha256: string }> {
  const response = await fetch(`${API_BASE}/api/workspace/pilot/${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail || `Pilot request failed (${response.status})`)
  return data
}

async function openPilot(state: PilotState) {
  const response = await fetch(`${API_BASE}/api/workspace/files/${encodeURIComponent(state.pilot_path)}`)
  if (!response.ok) throw new Error('Could not open disposable pilot copy')
  const { content } = await response.json()
  const store = useEditorStore.getState()
  store.addFile({
    name: state.pilot_path.split('/').at(-1) || 'pilot.md',
    path: state.pilot_path,
    content,
    originalContent: content,
  })
  store.loadFileContent(state.pilot_path, content)
  store.setContent(content)
  store.setCurrentFilePath(state.pilot_path)
  store.setPilot(state)
  store.setPilotError('')
}

export function PilotPanel({ onSave }: { onSave: () => Promise<void> }) {
  const pilot = useEditorStore(state => state.pilot)
  const pilotError = useEditorStore(state => state.pilotError)
  const currentFilePath = useEditorStore(state => state.currentFilePath)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const actionGate = useRef(createPilotActionGate())
  const sourcePath = pilot?.source_path || currentFilePath
  const sourceEligible = pilot ? true : isEligiblePilotSource(currentFilePath)
  const controls = pilotControls(pilot, sourceEligible, busy)
  const statusGuidance = pilotStatusGuidance(pilot)
  const sourceGuidance = !pilot && currentFilePath && !sourceEligible
    ? INELIGIBLE_PILOT_SOURCE_GUIDANCE
    : null

  useEffect(() => {
    if (pilot || !isEligiblePilotSource(currentFilePath)) return
    let active = true
    fetch(`${API_BASE}/api/workspace/pilot/status?source_path=${encodeURIComponent(currentFilePath!)}`)
      .then(response => response.ok ? response.json() : null)
      .then(state => {
        if (active && state) openPilot(state as PilotState).catch(err => setError(String(err)))
      })
      .catch(() => undefined)
    return () => { active = false }
  }, [pilot, currentFilePath])

  const run = async (operation: 'start' | 'reset' | 'export') => {
    if (operation === 'export' && controls.exportDisabled) return
    if (!sourcePath || !actionGate.current.begin()) return
    setBusy(true)
    setError('')
    try {
      const result = await action(operation, { source_path: sourcePath })
      if (operation === 'export') {
        const current = useEditorStore.getState().pilot
        if (current) useEditorStore.getState().setPilot({ ...current, exported: true })
      } else {
        await openPilot(result as PilotState)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Pilot action failed'
      setError(message)
      if (operation === 'export' && message === 'Approved copy already exported') {
        const current = useEditorStore.getState().pilot
        if (current) useEditorStore.getState().setPilot({ ...current, exported: true })
      }
    } finally {
      actionGate.current.end()
      setBusy(false)
    }
  }

  const save = async () => {
    if (controls.saveDisabled || !actionGate.current.begin()) return
    setBusy(true)
    setError('')
    try {
      await onSave()
    } finally {
      actionGate.current.end()
      setBusy(false)
    }
  }

  const finish = async () => {
    if (controls.finishDisabled || !sourcePath || !actionGate.current.begin()) return
    setBusy(true)
    setError('')
    try {
      await action('finish', { source_path: sourcePath })
      finishPilotSession(useEditorStore.getState(), false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Pilot finish failed')
    } finally {
      actionGate.current.end()
      setBusy(false)
    }
  }

  return <section className="mb-4 rounded-lg border border-[var(--border)] p-3 text-xs bg-[var(--bg)]">
    <div className="font-semibold mb-2">DARC Pilot Mode</div>
    <div>Source chapter: {pilot?.source_path || currentFilePath || 'Select a Markdown chapter'}</div>
    <div>Disposable pilot copy: {pilot?.pilot_path || 'None'}</div>
    <div>Run number: {pilot?.run || '—'}</div>
    <div>Source protection: {pilot ? 'Protected by workspace API' : 'NOT VERIFIED'}</div>
    <div>Last verification: <strong className={pilot?.status === 'PASS' ? 'text-green-600' : pilot?.status === 'FAIL' ? 'text-red-600' : 'text-amber-600'}>{pilot?.status || 'NOT VERIFIED'}</strong></div>
    {pilot?.verification && <div>Verified by: {pilot.verification}</div>}
    {pilot && <div className="break-all">Baseline SHA-256: {pilot.baseline}</div>}
    <div className="flex flex-wrap gap-2 mt-2">
      <button className="rounded-md bg-blue-600 px-3 py-2 font-bold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-45" disabled={controls.startDisabled} onClick={() => run('start')}>Start Protected Pilot</button>
      <button className="rounded-md bg-blue-600 px-3 py-2 font-bold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-45" disabled={controls.saveDisabled} onClick={save}>Save Pilot Edits</button>
      <button className="rounded-md border-2 border-amber-600 px-3 py-2 font-semibold text-amber-700 hover:bg-amber-50 disabled:cursor-not-allowed disabled:opacity-45" disabled={controls.resetDisabled} onClick={() => run('reset')}>Reset Pilot</button>
      <button className={`rounded-md px-3 py-2 font-bold ${exportButtonAppearance(controls.exportDisabled)}`} disabled={controls.exportDisabled} onClick={() => run('export')}>{controls.exportLabel}</button>
      <button className="rounded-md border border-[var(--border)] px-3 py-2 font-semibold text-[var(--text)] hover:bg-[var(--bg-hover)] disabled:cursor-not-allowed disabled:opacity-45" disabled={controls.finishDisabled} onClick={finish}>Finish Pilot</button>
    </div>
    {statusGuidance && <div className="mt-2 text-amber-600">{statusGuidance}</div>}
    {sourceGuidance && <div className="mt-2 text-amber-600">{sourceGuidance}</div>}
    {pilot && <div className="text-amber-600 mt-2">Edit directly in the main text field. Save writes only to the disposable pilot; the source remains protected.</div>}
    {error && <div role="alert" className="text-red-600 mt-2">{error}</div>}
    {pilotError && <div role="alert" className="text-red-600 mt-2">{pilotError}</div>}
  </section>
}
