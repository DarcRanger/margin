export interface PilotControlState {
  status: 'NOT VERIFIED' | 'PASS' | 'FAIL'
  decision?: 'ACCEPT' | 'REJECT' | null
  exported?: boolean
}

export const UNVERIFIED_PILOT_GUIDANCE = 'Edit the main text field and save, or review a Margin AI change, to verify this pilot.'
export const INELIGIBLE_PILOT_SOURCE_GUIDANCE = 'Select a Markdown chapter outside PILOT to start a protected pilot.'

export function isEligiblePilotSource(path: string | null): boolean {
  if (!path) return false
  const normalized = path.replaceAll('\\', '/').replace(/^\.\//, '')
  const lower = normalized.toLowerCase()
  return lower.endsWith('.md') && lower !== 'pilot' && !lower.startsWith('pilot/')
}

export function pilotStatusGuidance(pilot: PilotControlState | null): string | null {
  return pilot?.status === 'NOT VERIFIED' ? UNVERIFIED_PILOT_GUIDANCE : null
}

export function exportButtonAppearance(disabled: boolean): string {
  return disabled
    ? 'cursor-not-allowed border border-[var(--border)] bg-[var(--bg-elevated)] text-[var(--text-muted)]'
    : 'bg-green-600 text-white hover:bg-green-700'
}

export function pilotControls(pilot: PilotControlState | null, sourceEligible: boolean, busy: boolean) {
  return {
    startDisabled: busy || !!pilot || !sourceEligible,
    saveDisabled: busy || !pilot,
    resetDisabled: busy || !pilot,
    exportDisabled: busy || !pilot || pilot.status !== 'PASS' || pilot.decision !== 'ACCEPT' || !!pilot.exported,
    exportLabel: pilot?.exported ? 'Exported' : 'Export Approved Copy',
    finishDisabled: busy || !pilot || pilot.status !== 'PASS' || pilot.decision !== 'ACCEPT' || !pilot.exported,
  }
}

export function pilotBlocksNavigation(pilot: { pilot_path: string } | null, path: string): boolean {
  return !!pilot && path !== pilot.pilot_path
}

interface PilotUiSession {
  pilot: PilotControlState | null
  setCurrentFilePath: (path: null) => void
  setContent: (content: string) => void
  setAiPendingEdit: (edit: null) => void
  setPilotError: (error: string) => void
  setPilot: (pilot: null) => void
}

export function finishPilotSession(session: PilotUiSession, busy: boolean): boolean {
  if (pilotControls(session.pilot, true, busy).finishDisabled) return false
  session.setCurrentFilePath(null)
  session.setContent('')
  session.setAiPendingEdit(null)
  session.setPilotError('')
  session.setPilot(null)
  return true
}

export function createPilotActionGate() {
  let inFlight = false
  return {
    begin() {
      if (inFlight) return false
      inFlight = true
      return true
    },
    end() { inFlight = false },
  }
}
