import { useState, useEffect } from 'react'
import { Link, Route, Routes, useLocation } from 'react-router-dom'
import Library from './pages/Library'
import Upload from './pages/Upload'
import { type Lang, useTranslations } from './i18n'

const INFO_SEEN_KEY = 'reading-coach-info-seen'

function Nav({ language }: { language: Lang }) {
  const { pathname } = useLocation()
  const t = useTranslations(language)
  
  const linkStyle = (path: string) => ({
    padding: '0.5rem 0.9rem',
    textDecoration: 'none',
    borderBottom: pathname === path ? '3px solid #7b83ff' : '3px solid transparent',
    color: pathname === path ? '#1f1e5a' : '#5c607d',
    fontWeight: pathname === path ? 700 : 500,
  })

  const uploadLinkStyle = {
    padding: '0.5rem 1rem',
    textDecoration: 'none',
    background: pathname === '/upload' ? '#1f1e5a' : '#7b83ff',
    color: '#ffffff',
    fontWeight: 600,
    borderRadius: '999px',
    border: 'none',
    borderBottom: 'none',
    fontSize: '0.9rem',
    minHeight: '36px',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    transition: 'all 0.2s ease',
  }

  return (
    <nav style={{ display: 'flex', gap: 12, borderBottom: '1px solid #e3e6ff', marginBottom: 16 }}>
      <Link to="/upload" style={uploadLinkStyle}>{t.navUpload}</Link>
      <Link to="/" style={linkStyle('/')}>{t.navLibrary}</Link>
    </nav>
  )
}

function InfoModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  if (!isOpen) return null

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(31, 30, 90, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        animation: 'fadeIn 0.2s ease',
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%)',
          borderRadius: '20px',
          padding: '2rem 2.5rem',
          maxWidth: '500px',
          width: '90%',
          boxShadow: '0 20px 60px rgba(31, 30, 90, 0.25), 0 0 0 1px rgba(123, 131, 255, 0.1)',
          position: 'relative',
          animation: 'slideUp 0.3s ease',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '12px',
            right: '12px',
            background: 'none',
            border: 'none',
            fontSize: '1.5rem',
            cursor: 'pointer',
            color: '#5c607d',
            padding: '4px 8px',
            minHeight: 'auto',
            borderRadius: '8px',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = '#f0f1ff'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
        >
          ×
        </button>

        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <span style={{ fontSize: '3rem' }}>📚</span>
        </div>

        <h2 style={{
          textAlign: 'center',
          color: '#1f1e5a',
          marginTop: 0,
          marginBottom: '1rem',
          fontSize: '1.4rem',
          fontWeight: 700,
        }}>
          Lasīšanas aplikācijas testa versija
        </h2>

        <p style={{
          color: '#3d4166',
          lineHeight: 1.7,
          marginBottom: '1rem',
          fontSize: '1rem',
        }}>
          Šī aplikācija ļauj jums augšuplādēt jebkuru ne pārāk garu tekstu. 
          Aplikācija to sadala fragmentos, ja nepieciešams to vienkāršo, 
          uzdod jautājumus par tekstu un novērtē atbildes.
        </p>

        <p style={{
          color: '#3d4166',
          lineHeight: 1.7,
          marginBottom: '1rem',
          fontSize: '1rem',
          fontWeight: 500,
        }}>
          Bezmaksas GPT vaicājumi ir limitēti.
        </p>

        <p style={{
          color: '#7b83ff',
          fontWeight: 600,
          textAlign: 'center',
          marginBottom: '0.5rem',
          fontSize: '0.95rem',
        }}>
          Aplikācija paredzēta, lai palīdzētu bērniem ar lasīšanas grūtībām.
        </p>

        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <button
            onClick={onClose}
            style={{
              background: 'linear-gradient(135deg, #7b83ff 0%, #6366f1 100%)',
              color: '#fff',
              border: 'none',
              padding: '0.75rem 2rem',
              borderRadius: '999px',
              fontWeight: 600,
              cursor: 'pointer',
              fontSize: '1rem',
              boxShadow: '0 4px 15px rgba(123, 131, 255, 0.4)',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(123, 131, 255, 0.5)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 4px 15px rgba(123, 131, 255, 0.4)'
            }}
          >
            Sapratu!
          </button>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from { 
            opacity: 0; 
            transform: translateY(20px) scale(0.95); 
          }
          to { 
            opacity: 1; 
            transform: translateY(0) scale(1); 
          }
        }
      `}</style>
    </div>
  )
}

export default function App() {
  const [language, setLanguage] = useState<Lang>('Latvian')
  const [showInfo, setShowInfo] = useState(false)
  const t = useTranslations(language)

  // Show popup automatically on first visit
  useEffect(() => {
    const hasSeenInfo = localStorage.getItem(INFO_SEEN_KEY)
    if (!hasSeenInfo) {
      setShowInfo(true)
    }
  }, [])

  const handleCloseInfo = () => {
    setShowInfo(false)
    localStorage.setItem(INFO_SEEN_KEY, 'true')
  }

  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '1.5rem 1rem' }}>
      <div style={{ position: 'relative', textAlign: 'center', marginBottom: '0.5rem' }}>
        <h1 style={{ margin: 0 }}>{t.appTitle}</h1>
        <button
          onClick={() => setShowInfo(true)}
          style={{
            position: 'absolute',
            right: 0,
            top: '50%',
            transform: 'translateY(-50%)',
            background: 'linear-gradient(135deg, #7b83ff 0%, #6366f1 100%)',
            color: '#fff',
            border: 'none',
            width: '36px',
            height: '36px',
            minHeight: '36px',
            borderRadius: '50%',
            fontSize: '1.1rem',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 0,
            boxShadow: '0 3px 10px rgba(123, 131, 255, 0.35)',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-50%) scale(1.1)'
            e.currentTarget.style.boxShadow = '0 5px 15px rgba(123, 131, 255, 0.5)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(-50%) scale(1)'
            e.currentTarget.style.boxShadow = '0 3px 10px rgba(123, 131, 255, 0.35)'
          }}
          title="?"
        >
          ?
        </button>
      </div>
      <p style={{ textAlign: 'center', color: '#5c607d', marginTop: 0 }}>
        {t.appSubtitle}
      </p>
      <Nav language={language} />
      <Routes>
        <Route path="/" element={<Library language={language} onLanguageChange={setLanguage} />} />
        <Route path="/upload" element={<Upload language={language} onLanguageChange={setLanguage} />} />
      </Routes>

      <InfoModal isOpen={showInfo} onClose={handleCloseInfo} />
    </div>
  )
}
