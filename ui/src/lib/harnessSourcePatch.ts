type Line = { text: string; end: string }

function lines(source: string): Line[] {
  const result: Line[] = []
  const pattern = /([^\r\n]*)(\r\n|\n|\r|$)/g
  for (const match of source.matchAll(pattern)) {
    if (!match[0]) break
    result.push({ text: match[1], end: match[2] })
  }
  return result
}

export function applyHarnessSourceChanges(original: string, changed: string): string {
  const before = lines(original)
  const after = lines(changed)
  const n = before.length
  const m = after.length
  const dp: number[][] = Array.from({ length: n + 1 }, () => Array<number>(m + 1).fill(0))
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i][j] = before[i].text === after[j].text
        ? dp[i + 1][j + 1] + 1
        : Math.max(dp[i + 1][j], dp[i][j + 1])
    }
  }
  const preferredEnd = before.find(line => line.end)?.end || '\n'
  const output: Line[] = []
  let i = 0
  let j = 0
  while (i < n || j < m) {
    if (i < n && j < m && before[i].text === after[j].text) {
      output.push(before[i])
      i += 1
      j += 1
      continue
    }
    const oldStart = i
    const newStart = j
    while ((i < n || j < m) && !(i < n && j < m && before[i].text === after[j].text)) {
      if (j < m && (i === n || dp[i][j + 1] >= dp[i + 1][j])) j += 1
      else i += 1
    }
    const old = before.slice(oldStart, i)
    after.slice(newStart, j).forEach((line, index) => {
      output.push({ text: line.text, end: old[index]?.end || preferredEnd })
    })
  }
  if (output.length) {
    output[output.length - 1].end = before.at(-1)?.end || ''
    for (let index = 0; index < output.length - 1; index++) {
      if (!output[index].end) output[index].end = preferredEnd
    }
  }
  return output.map(line => line.text + line.end).join('')
}

export function sourceForHarnessReview(original: string, changed: string, accept: boolean): string {
  return accept ? applyHarnessSourceChanges(original, changed) : original
}
