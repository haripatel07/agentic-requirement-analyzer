import React from 'react'
import { render, screen } from '@testing-library/react'
import PipelineProgress from './PipelineProgress'

describe('PipelineProgress', () => {
  test('marks done, active and pending steps', () => {
    render(<PipelineProgress step={2} />)

    expect(screen.getByText('Uploading').closest('li')).toHaveAttribute('data-state', 'done')
    expect(screen.getByText('Running agent pipeline').closest('li')).toHaveAttribute('data-state', 'active')
    expect(screen.getByText('Assembling report').closest('li')).toHaveAttribute('data-state', 'todo')
  })
})
