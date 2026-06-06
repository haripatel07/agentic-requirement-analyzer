import React from 'react'
import { render, screen } from '@testing-library/react'
import PipelineProgress from './PipelineProgress'

describe('PipelineProgress', () => {
  test('highlights the current step', () => {
    render(<PipelineProgress step={2} />)

    expect(screen.getByText('Uploading')).toBeInTheDocument()
    expect(screen.getByText('Parsing+Analysis').closest('li')).toHaveClass('font-semibold')
    expect(screen.getByText('Generating report')).toBeInTheDocument()
  })
})
