import { expect, test } from '@playwright/test'
import { readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const sourceText = '# Fixture Chapter\n\nA generic sentence for browser acceptance.\n'
const editedText = ' Browser edit'
const exportText = ' Browser export'

test('protected Pilot lifecycle preserves source and recovers from a visible conflict', async ({ page }) => {
  const workspace = process.env.MARGIN_BROWSER_WORKSPACE
  if (!workspace) throw new Error('MARGIN_BROWSER_WORKSPACE is required')

  const source = join(workspace, 'chapters', 'Fixture_Chapter.md')
  const pilot = join(workspace, 'PILOT', 'Fixture_Chapter_Margin_Pilot', 'Fixture_Chapter.md')
  const sourceBytes = readFileSync(source)

  await page.goto('/')
  await expect(page.getByText('DARC Pilot Mode')).toBeVisible()

  const sourceRow = page.locator('[title="chapters/Fixture_Chapter.md"]')
  await expect(sourceRow).toBeVisible()
  await sourceRow.click()
  await expect(page.getByText('Source chapter: chapters/Fixture_Chapter.md')).toBeVisible()
  await expect(page.locator('.ProseMirror')).toContainText('A generic sentence')

  await page.getByRole('button', { name: 'Start Protected Pilot' }).click()
  await expect(page.getByText('Run number: 1')).toBeVisible()
  await expect(page.getByText('Source protection: Protected by workspace API')).toBeVisible()

  const editor = page.locator('.ProseMirror')
  await editor.click()
  await page.keyboard.press(process.platform === 'darwin' ? 'Meta+End' : 'Control+End')
  await page.keyboard.type(editedText)

  const cleanPilotBytes = readFileSync(pilot)
  writeFileSync(pilot, Buffer.concat([cleanPilotBytes, Buffer.from('external conflict\n')]))
  await page.getByRole('button', { name: 'Save Pilot Edits' }).click()
  await expect(page.getByRole('alert')).toContainText('Pilot changed externally; pilot save refused')

  writeFileSync(pilot, cleanPilotBytes)
  await page.getByRole('button', { name: 'Save Pilot Edits' }).click()
  await expect(page.getByText('Last verification:').locator('strong')).toHaveText('PASS')
  await expect(page.getByText('Verified by: MANUAL EDIT')).toBeVisible()
  await expect(page.getByRole('alert')).toHaveCount(0)

  await page.getByRole('button', { name: 'Reset Pilot' }).click()
  await expect(page.getByText('Run number: 2')).toBeVisible()
  await expect(editor).not.toContainText(editedText.trim())

  await editor.click()
  await page.keyboard.press(process.platform === 'darwin' ? 'Meta+End' : 'Control+End')
  await page.keyboard.type(exportText)
  await page.getByRole('button', { name: 'Save Pilot Edits' }).click()
  await expect(page.getByText('Last verification:').locator('strong')).toHaveText('PASS')
  await page.getByRole('button', { name: 'Export Approved Copy' }).click()
  await expect(page.getByRole('button', { name: 'Exported' })).toBeDisabled()

  const approved = join(
    workspace,
    'PILOT',
    'Fixture_Chapter_Margin_Pilot',
    'OUTPUT',
    'RUN_002_APPROVED.md',
  )
  const expectedApprovedBytes = Buffer.from(
    sourceText.replace('acceptance.', `acceptance.${exportText}`),
  )
  expect(readFileSync(approved).equals(expectedApprovedBytes)).toBe(true)
  expect(readFileSync(source).equals(sourceBytes)).toBe(true)

  await page.getByRole('button', { name: 'Finish Pilot' }).click()
  await expect(page.getByText('Run number: —')).toBeVisible()

  await sourceRow.click()
  await expect(page.getByText('Source chapter: chapters/Fixture_Chapter.md')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Start Protected Pilot' })).toBeEnabled()
  await expect(editor).not.toContainText(exportText.trim())

  await page.getByText('PILOT/', { exact: true }).click()
  await page.getByText('Fixture_Chapter_Margin_Pilot/', { exact: true }).click()
  await page.locator('[title="PILOT/Fixture_Chapter_Margin_Pilot/Fixture_Chapter.md"]').click()
  await expect(page.getByRole('button', { name: 'Start Protected Pilot' })).toBeDisabled()
  await expect(page.getByText('Select a Markdown chapter outside PILOT to start a protected pilot.')).toBeVisible()

  expect(readFileSync(source).equals(sourceBytes)).toBe(true)
  expect(readFileSync(source, 'utf8')).toBe(sourceText)
})
