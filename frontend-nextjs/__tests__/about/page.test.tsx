import { expect, test } from 'vitest'
import { render, screen } from '@testing-library/react'
import Page from '../../app/about/page'

test('Page', () => {
  render(<Page />)
  expect(screen.getByRole('heading', { level: 1, name: 'About' })).toBeDefined()
})