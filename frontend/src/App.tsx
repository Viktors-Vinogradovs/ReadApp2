import { useState } from 'react'
import { Link, Route, Routes, useLocation } from 'react-router-dom'
import Library from './pages/Library'
import Upload from './pages/Upload'
import { type Lang } from './i18n'

function Nav() {
  const { pathname } = useLocation()
  const linkStyle = (path: string) => ({
    padding: '0.5rem 0.9rem',
    textDecoration: 'none',
    borderBottom: pathname === path ? '3px solid #7b83ff' : '3px solid transparent',
    color: pathname === path ? '#1f1e5a' : '#5c607d',
    fontWeight: pathname === path ? 700 : 500,
  })

  return (
    <nav style={{ display: 'flex', gap: 12, borderBottom: '1px solid #e3e6ff', marginBottom: 16 }}>
      <Link to="/upload" style={linkStyle('/upload')}>Upload</Link>
      <Link to="/" style={linkStyle('/')}>Library</Link>
    </nav>
  )
}

export default function App() {
  const [language, setLanguage] = useState<Lang>('Latvian')

  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '1.5rem 1rem' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '0.5rem' }}>Reading Coach</h1>
      <p style={{ textAlign: 'center', color: '#5c607d', marginTop: 0 }}>
        Upload your text, simplify it, and practise comprehension with instant feedback.
      </p>
      <Nav />
      <Routes>
        <Route path="/" element={<Library language={language} onLanguageChange={setLanguage} />} />
        <Route path="/upload" element={<Upload language={language} onLanguageChange={setLanguage} />} />
      </Routes>
    </div>
  )
}