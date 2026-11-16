import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import UploadForm from './UploadForm'

beforeEach(() => {
  global.fetch = vi.fn()
})

afterEach(() => {
  vi.restoreAllMocks()
})

const ok = (body) => ({ ok: true, json: async () => body })

describe('UploadForm', () => {
  test('shows a message when no file is selected', async () => {
    render(<UploadForm />)

    fireEvent.click(screen.getByRole('button', { name: /upload & analyze/i }))

    expect(await screen.findByText('No file selected')).toBeInTheDocument()
  })

  test('uploads, analyzes and reports the result to the parent', async () => {
    const onComplete = vi.fn()
    fetch
      .mockResolvedValueOnce(ok({ filename: 'uploads/sample.txt', status: 'uploaded' }))
      .mockResolvedValueOnce(ok({ run_id: 1, report: { executive_summary: 'Summary text' } }))

    const { container } = render(<UploadForm onComplete={onComplete} />)
    const input = container.querySelector('input[type="file"]')
    fireEvent.change(input, { target: { files: [new File(['hello'], 'sample.txt', { type: 'text/plain' })] } })
    fireEvent.click(screen.getByRole('button', { name: /upload & analyze/i }))

    await waitFor(() => expect(screen.getByText('Analysis complete')).toBeInTheDocument())
    expect(onComplete).toHaveBeenCalledWith({ run_id: 1, report: { executive_summary: 'Summary text' } })
    expect(fetch).toHaveBeenCalledTimes(2)
  })

  test('shows the server error when analysis fails', async () => {
    fetch
      .mockResolvedValueOnce(ok({ filename: 'uploads/a.txt' }))
      .mockResolvedValueOnce({ ok: false, status: 500, json: async () => ({ detail: 'boom' }) })

    const { container } = render(<UploadForm />)
    fireEvent.change(container.querySelector('input[type="file"]'), {
      target: { files: [new File(['x'], 'a.txt')] },
    })
    fireEvent.click(screen.getByRole('button', { name: /upload & analyze/i }))

    expect(await screen.findByText('Error: boom')).toBeInTheDocument()
  })

  test('rejects unsupported file types', () => {
    const { container } = render(<UploadForm />)
    fireEvent.change(container.querySelector('input[type="file"]'), {
      target: { files: [new File(['x'], 'a.exe')] },
    })
    expect(screen.getByText(/Unsupported file type/)).toBeInTheDocument()
  })
})
