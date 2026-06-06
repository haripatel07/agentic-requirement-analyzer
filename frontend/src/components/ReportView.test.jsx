import React from 'react'
import { render, screen } from '@testing-library/react'
import ReportView from './ReportView'

describe('ReportView', () => {
  test('renders all major report sections', () => {
    render(
      <ReportView
        report={{
          executive_summary: 'Summary text',
          functional_requirements: ['Login'],
          non_functional_requirements: ['Fast response'],
          user_stories: [{ feature: 'Login', story: 'As a user, I want to log in', priority: 'High' }],
          acceptance_criteria: [{ story_ref: 'As a user, I want to log in', given: 'Given valid creds', when: 'When submitted', then: 'Then user is logged in' }],
          ambiguities: [{ requirement: 'Fast response', reason: 'vague', suggestion: 'Specify a response time' }],
          suggestions: ['Specify a response time'],
          errors: [],
        }}
      />
    )

    expect(screen.getByText('Executive Summary')).toBeInTheDocument()
    expect(screen.getByText('Summary text')).toBeInTheDocument()
    expect(screen.getByText('Functional Requirements')).toBeInTheDocument()
    expect(screen.getByText('Non-Functional Requirements')).toBeInTheDocument()
    expect(screen.getByText('User Stories')).toBeInTheDocument()
    expect(screen.getByText('Acceptance Criteria')).toBeInTheDocument()
    expect(screen.getByText('Ambiguities')).toBeInTheDocument()
    expect(screen.getByText('Suggestions')).toBeInTheDocument()
  })
})
