// src/App.test.tsx
import { render } from '@testing-library/react'
import App from './App'

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(document.body).toBeTruthy()
  })

  it('should have basic structure', () => {
    const { container } = render(<App />)
    expect(container).toBeInTheDocument()
  })
})
