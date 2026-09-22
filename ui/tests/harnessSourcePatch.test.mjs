import assert from 'node:assert/strict'
import { test } from 'node:test'
import { sourceForHarnessReview } from '../src/lib/harnessSourcePatch.ts'

test('accept changes only requested text and preserves bytes', () => {
  const original = '# Old\r\n\r\n  \\[literal\\]  \r\nA  ·  B'
  const changed = '# New\n\n  \\[literal\\]  \nA  ·  B\n'
  assert.equal(sourceForHarnessReview(original, changed, true), original.replace('# Old', '# New'))
})

test('reject restores exact original source', () => {
  const original = '# Old\r\n\r\nA  ·  B'
  assert.deepEqual(
    Buffer.from(sourceForHarnessReview(original, '# New\n\nA · B\n', false)),
    Buffer.from(original),
  )
})
