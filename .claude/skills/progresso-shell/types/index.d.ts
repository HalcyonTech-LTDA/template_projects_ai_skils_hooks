export type Job = { kind: 'test' | 'shell'; label: string }

export type Progress = Job & {
  id: string
  passed: number
  failed: number
  skipped: number
  suites: number
  total: number | null
  percent: number | null
  lines: number
}
