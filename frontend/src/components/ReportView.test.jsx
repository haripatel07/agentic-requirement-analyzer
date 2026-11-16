import React from 'react'
import { render, screen } from '@testing-library/react'
import ReportView, { reportToMarkdown } from './ReportView'

const report = {
  executive_summary: 'Summary text',
  functional_requirements: ['Login'],
  non_functional_requirements: ['Fast response'],
  user_stories: [{ feature: 'Login', story: 'As a user, I want to log in', priority: 'High' }],
  acceptance_criteria: [{ story_ref: 'As a user, I want to log in', given: 'valid creds', when: 'submitted', then: 'user is logged in' }],
  ambiguities: [{ requirement: 'Fast response', reason: 'vague', suggestion: 'Specify a response time' }],
  risks: [{ requirement: 'Login', reason: 'Security risk (High)', suggestion: 'Add MFA' }],
  suggestions: ['Specify a response time'],
  errors: [],
}

describe('ReportView', () => {
  test('renders all major report sections', () => {
    render(<ReportView report={report} />)

    for (const title of ['Executive Summary', 'Functional Requirements', 'Non-Functional Requirements',
      'User Stories', 'Acceptance Criteria', 'Ambiguities', 'Risks', 'Suggestions']) {
      expect(screen.getByRole('heading', { name: new RegExp("^" + title) })).toBeInTheDocument()
    }
    expect(screen.getByText('Summary text')).toBeInTheDocument()
  })

  test('renders Given/When/Then labels exactly once', () => {
    render(<ReportView report={report} />)

    expect(screen.getAllByText('Given')).toHaveLength(1)
    expect(screen.getAllByText('When')).toHaveLength(1)
    expect(screen.getAllByText('Then')).toHaveLength(1)
    expect(screen.queryByText(/Given Given/)).not.toBeInTheDocument()
  })

  test('markdown export includes risks and criteria', () => {
    const md = reportToMarkdown(report)
    expect(md).toContain('## Risks')
    expect(md).toContain('Given valid creds')
  })
})
