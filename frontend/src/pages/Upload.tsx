import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { formatText, previewFragments, simplify, uploadText } from '../api/client'
import { LANGS, type Lang, useTranslations } from '../i18n'

type UploadProps = {
  language: Lang
  onLanguageChange: (lang: Lang) => void
}

const FRAGMENT_TARGETS = {
  small: 250,
  medium: 400,
  large: 650,
} as const

function generateAutoTitle(text: string): string {
  const cleaned = text.replace(/\s+/g, ' ').trim()
  const words = cleaned.split(' ').slice(0, 3)
  return words.join(' ')
}

export default function Upload({ language, onLanguageChange }: UploadProps) {
  const t = useTranslations(language)
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [text, setText] = useState('')
  const [fragmentSize, setFragmentSize] = useState<keyof typeof FRAGMENT_TARGETS>('medium')
  const [preview, setPreview] = useState<string[]>([])
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')

  async function handleSimplify(level: 'gentle' | 'deep') {
    if (!text.trim()) return
    setBusy(true)
    setMessage('')
    try {
      const simplified = await simplify(text, language, level === 'gentle' ? 'gentle' : 'deep')
      setText(simplified)
    } catch (err) {
      console.error('simplify failed', err)
      setMessage(t.uploadError)
    } finally {
      setBusy(false)
    }
  }

  async function handleFormat() {
    if (!text.trim()) return
    setBusy(true)
    setMessage('')
    try {
      const formatted = await formatText(text, language)
      setText(formatted)
    } catch (err) {
      console.error('format failed', err)
      setMessage(t.uploadError)
    } finally {
      setBusy(false)
    }
  }

  async function handlePreview() {
    if (!text.trim()) return
    setBusy(true)
    setMessage('')
    try {
      const fragments = await previewFragments(text, FRAGMENT_TARGETS[fragmentSize])
      setPreview(fragments)
    } catch (err) {
      console.error('preview failed', err)
      setPreview([])
    } finally {
      setBusy(false)
    }
  }

  async function handleSave() {
    if (!text.trim()) return
    setBusy(true)
    setMessage('')
    try {
      const finalTitle = title.trim() || generateAutoTitle(text)
      await uploadText(finalTitle, language, text, true, FRAGMENT_TARGETS[fragmentSize])
      setMessage(t.uploadSuccess)
      localStorage.setItem('reading:lastUploaded', finalTitle)
      setTimeout(() => {
        setTitle('')
        setText('')
        setPreview([])
        navigate('/')
      }, 1000)
    } catch (err) {
      console.error('upload failed', err)
      setMessage(t.uploadError)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="upload-container">
      <h2>{t.uploadTitle}</h2>
      
      <div className="upload-form">
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 20 }}>
          <label style={{ flex: '1 1 200px' }}>
            {t.languageLabel}
            <select 
              value={language} 
              onChange={e => onLanguageChange(e.target.value as Lang)} 
              style={{ width: '100%', marginTop: 4 }}
            >
              {LANGS.map(l => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </label>
          <label style={{ flex: '2 1 300px' }}>
            {t.titleLabel}
            <input
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder={t.titlePlaceholder}
              style={{ width: '100%', marginTop: 4, padding: '0.5rem 0.7rem' }}
            />
          </label>
        </div>

        <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
          {t.pastePlaceholder}
        </label>
        <textarea
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder={t.pastePlaceholder}
          rows={16}
          style={{ 
            width: '100%', 
            padding: '1rem', 
            borderRadius: 12, 
            border: '1px solid #dfe2ff',
            fontFamily: 'inherit',
            fontSize: '1rem',
            lineHeight: 1.6
          }}
        />

        <div className="text-tools" style={{ marginTop: 20 }}>
          <h3 style={{ fontSize: '1rem', marginBottom: 12 }}>{t.simplifyTitle}</h3>
          <div className="control-grid" style={{ marginBottom: 20 }}>
            <div className="tool-with-hint">
              <button 
                onClick={() => handleSimplify('gentle')} 
                disabled={busy || !text.trim()}
                title={t.simplifyGentleHint}
              >
                ✨ {t.simplifyGentle}
              </button>
              <small className="hint-text">{t.simplifyGentleHint}</small>
            </div>
            <div className="tool-with-hint">
              <button 
                onClick={() => handleSimplify('deep')} 
                disabled={busy || !text.trim()}
                title={t.simplifyDeepHint}
              >
                ✨✨ {t.simplifyDeep}
              </button>
              <small className="hint-text">{t.simplifyDeepHint}</small>
            </div>
            <div className="tool-with-hint">
              <button 
                onClick={handleFormat} 
                disabled={busy || !text.trim()}
                title={t.formatButtonHint}
              >
                📝 {t.formatButton}
              </button>
              <small className="hint-text">{t.formatButtonHint}</small>
            </div>
          </div>
        </div>

        <div style={{ marginTop: 24 }}>
          <h3 style={{ fontSize: '1rem', marginBottom: 12 }}>{t.fragmentToolsTitle}</h3>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center', marginBottom: 12 }}>
            {(['small', 'medium', 'large'] as Array<keyof typeof FRAGMENT_TARGETS>).map(size => (
              <label key={size} style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input
                  type="radio"
                  checked={fragmentSize === size}
                  onChange={() => setFragmentSize(size)}
                  disabled={busy}
                />
                <span>{t.fragmentSize[{ small: 0, medium: 1, large: 2 }[size]]}</span>
              </label>
            ))}
            <button 
              onClick={handlePreview} 
              disabled={busy || !text.trim()}
              style={{ marginLeft: 'auto' }}
            >
              👁 {t.fragmentPreview}
            </button>
          </div>
          <p className="hint-text" style={{ margin: '8px 0 16px 0' }}>{t.previewHint}</p>
          
          {preview.length > 0 && (
            <div className="preview-panel-scrollable">
              <strong style={{ display: 'block', marginBottom: 8 }}>{t.previewHeading}</strong>
              {preview.map((frag, idx) => (
                <div key={idx} className="preview-fragment">
                  <strong style={{ color: '#7b83ff' }}>Fragment {idx + 1}:</strong>
                  <p style={{ margin: '4px 0 0 0', lineHeight: 1.6 }}>
                    {frag.slice(0, 200)}
                    {frag.length > 200 ? '…' : ''}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {message && (
          <div className={`upload-message ${message.includes('added') || message.includes('saglabāts') || message.includes('guardado') || message.includes('сохранён') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        <button 
          onClick={handleSave} 
          disabled={busy || !text.trim()} 
          className="save-button"
          style={{ marginTop: 24, width: '100%', padding: '0.8rem', fontSize: '1.1rem', fontWeight: 600 }}
        >
          {busy ? '⏳ ' + t.saveButton + '…' : '💾 ' + t.saveButton}
        </button>
      </div>
    </div>
  )
}
