export const API_BASE = import.meta.env?.VITE_API_BASE || 'http://localhost:8000'

async function request(path, options) {
  const res = await fetch(`${API_BASE}${path}`, options)
  let body = null
  try {
    body = await res.json()
  } catch {
    /* non-JSON response */
  }
  if (res.ok === false) {
    throw new Error((body && (body.detail || body.error)) || `Request failed (${res.status})`)
  }
  return body
}

export function uploadFile(file) {
  const fd = new FormData()
  fd.append('file', file)
  return request('/upload', { method: 'POST', body: fd })
}

export function analyze(filename, displayName) {
  return request('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, display_name: displayName }),
  })
}

export const listRuns = () => request('/runs')
export const getRun = (id) => request(`/runs/${id}`)
