import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createPilotActionGate, finishPilotSession, pilotBlocksNavigation, pilotControls, pilotStatusGuidance, UNVERIFIED_PILOT_GUIDANCE } from '../src/lib/pilotControls.ts'

test('active pilot enables direct save but gates export and finish', () => {
  const active = { status: 'NOT VERIFIED', decision: null, exported: false }
  const controls = pilotControls(active, true, false)
  assert.equal(controls.startDisabled, true)
  assert.equal(controls.saveDisabled, false)
  assert.equal(controls.exportDisabled, true)
  assert.equal(controls.finishDisabled, true)
  assert.equal(pilotStatusGuidance(active), UNVERIFIED_PILOT_GUIDANCE)
  assert.match(UNVERIFIED_PILOT_GUIDANCE, /main text field/)
})

test('accepted exported pass can finish and release navigation', () => {
  const pilot = { pilot_path: 'PILOT/run/chapter.md', status: 'PASS', decision: 'ACCEPT', exported: true }
  const session = {
    pilot,
    setCurrentFilePath(value) { this.path = value },
    setContent(value) { this.content = value },
    setAiPendingEdit(value) { this.pending = value },
    setPilotError(value) { this.error = value },
    setPilot(value) { this.pilot = value },
  }
  assert.equal(pilotBlocksNavigation(pilot, 'chapters/next.md'), true)
  assert.equal(finishPilotSession(session, false), true)
  assert.equal(session.pilot, null)
  assert.equal(pilotBlocksNavigation(session.pilot, 'chapters/next.md'), false)
})

test('action gate rejects duplicate requests', () => {
  const gate = createPilotActionGate()
  assert.equal(gate.begin(), true)
  assert.equal(gate.begin(), false)
  gate.end()
  assert.equal(gate.begin(), true)
})
