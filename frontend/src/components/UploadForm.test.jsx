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

describe('UploadForm', () => {
  test('shows a message when no file is selected', async () => {
    render(<UploadForm />)

    fireEvent.click(screen.getByRole('button', { name: /upload & analyze/i }))

    expect(await screen.findByText('No file selected')).toBeInTheDocument()
  })

  test('uploads a file, analyzes it, and shows the report', async () => {
    fetch
      .mockResolvedValueOnce({
        json: async () => ({ filename: 'uploads/sample.txt', status: 'uploaded' }),
      })
      .mockResolvedValueOnce({
        json: async () => ({
          run_id: 1,
          report: {
            executive_summary: 'Summary text',
            functional_requirements: ['Login'],
            non_functional_requirements: ['Fast response'],
            user_stories: [{ feature: 'Login', story: 'As a user, I want to log in', priority: 'High' }],
            acceptance_criteria: [{ story_ref: 'As a user, I want to log in', given: 'Given valid creds', when: 'When submitted', then: 'Then user is logged in' }],
            ambiguities: [{ requirement: 'Fast response', reason: 'vague', suggestion: 'Specify a response time' }],
            suggestions: ['Specify a response time'],
            errors: [],
          },
        }),
      })

    const { container } = render(<UploadForm />)
    const fileInput = container.querySelector('input[type="file"]')
    const file = new File(['hello world'], 'sample.txt', { type: 'text/plain' })

    fireEvent.change(fileInput, { target: { files: [file] } })
    fireEvent.click(screen.getByRole('button', { name: /upload & analyze/i }))

    await waitFor(() => expect(screen.getByText('Analysis complete')).toBeInTheDocument())
    expect(screen.getByText('Summary text')).toBeInTheDocument()
    expect(screen.getByText('Login')).toBeInTheDocument()
    expect(screen.getByText('Fast response')).toBeInTheDocument()
    expect(fetch).toHaveBeenCalledTimes(2)
  })
})
