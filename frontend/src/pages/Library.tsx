import { useEffect, useMemo, useRef, useState } from 'react'
import type { TextItem, WordTiming } from '../api/client'
import { evaluate, generateQuestions, generateQuestionsBatch, getParts, listTexts, synthesizeAudio, simplify } from '../api/client'
import { LANGS, type Lang, useTranslations } from '../i18n'

type LibraryProps = {
  language: Lang
  onLanguageChange: (lang: Lang) => void
}

type HighlightMeta = { text: string; correct: boolean } | null

const STRICTNESS_LEVELS = [1, 2, 3] as const
const DIFFICULTIES: Array<{ key: 'standard' | 'easy'; labelKey: 'regenerateDefault' | 'regenerateEasy' }> = [
  { key: 'standard', labelKey: 'regenerateDefault' },
  { key: 'easy', labelKey: 'regenerateEasy' },
]

const SEQUENCE_WORDS: Record<Lang, string[]> = {
  English: ['then', 'after that', 'later', 'finally'],
  Latvian: ['pēc tam', 'un tad', 'vēlāk'],
  Spanish: ['luego', 'después', 'más tarde'],
  Russian: ['потом', 'затем', 'после этого'],
}

const escapeHtml = (value: string) =>
  value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

const escapeRegExp = (value: string) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

function buildFragmentHtml(
  text: string, 
  lang: Lang, 
  highlight: HighlightMeta, 
  uppercase: boolean,
  wordTimings: WordTiming[] = [],
  currentWordIndex: number = -1
) {
  if (!text) return ''
  let working = uppercase ? text.toUpperCase() : text

  // If we have word timings for audio highlighting, use word-by-word rendering
  if (wordTimings.length > 0 && currentWordIndex >= 0) {
    const words = working.split(/(\s+)/)  // Split but keep whitespace
    let html = ''
    let wordIndex = 0
    
    for (const segment of words) {
      if (segment.match(/^\s+$/)) {
        // Whitespace - just add it
        html += escapeHtml(segment)
      } else if (segment.trim()) {
        // It's a word
        const isCurrentWord = wordIndex === currentWordIndex
        const escaped = escapeHtml(segment)
        
        if (isCurrentWord) {
          html += `<span class="audio-highlight">${escaped}</span>`
        } else {
          html += escaped
        }
        
        wordIndex++
      }
    }
    
    return html.replace(/\n/g, '<br />')
  }

  // Otherwise, use the standard highlighting for answers
  // Single-match, case-insensitive highlighting
  if (highlight?.text) {
    const snippet = (uppercase ? highlight.text.toUpperCase() : highlight.text).trim()
    if (snippet.length > 0) {
      const workingLower = working.toLowerCase()
      const snippetLower = snippet.toLowerCase()
      
      let index = workingLower.indexOf(snippetLower)
      
      // If not found, try stripping trailing punctuation from snippet
      if (index === -1) {
        const stripped = snippetLower.replace(/[.,!?…]+$/, '')
        if (stripped.length >= 3) {
          index = workingLower.indexOf(stripped)
        }
      }
      
      // Only highlight if we found a match
      if (index !== -1) {
        const before = escapeHtml(working.slice(0, index))
        const match = escapeHtml(working.slice(index, index + snippet.length))
        const after = escapeHtml(working.slice(index + snippet.length))
        // Build HTML directly with proper tags (escape BEFORE adding tags)
        working = `${before}<span class="${highlight.correct ? 'hl-correct' : 'hl-wrong'}">${match}</span>${after}`
      } else {
        // No match found, just escape the whole text
        working = escapeHtml(working)
      }
    } else {
      working = escapeHtml(working)
    }
  } else {
    working = escapeHtml(working)
  }

  // Now working is already HTML-escaped, just add line breaks
  let html = working.replace(/\n/g, '<br />')

  // Add sequence word highlighting
  SEQUENCE_WORDS[lang]?.forEach(seq => {
    const regex = new RegExp(escapeRegExp(escapeHtml(seq)), 'gi')
    html = html.replace(regex, '<span class="seq-word">$&</span>')
  })

  return html
}

export default function Library({ language, onLanguageChange }: LibraryProps) {
  const t = useTranslations(language)
  const [texts, setTexts] = useState<TextItem[]>([])
  const [selectedText, setSelectedText] = useState('')
  const [parts, setParts] = useState<Record<string, string>>({})
  const [selectedPart, setSelectedPart] = useState('')
  const [fragment, setFragment] = useState('')
  const [questions, setQuestions] = useState<string[]>([])
  const [qIndex, setQIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [feedback, setFeedback] = useState('')
  const [highlight, setHighlight] = useState<HighlightMeta>(null)
  const [strictness, setStrictness] = useState<number>(2)
  const [uppercase, setUppercase] = useState(false)
  const [renderedFragment, setRenderedFragment] = useState('')
  const [isFragmentReading, setFragmentReading] = useState(false)
  const [textMode, setTextMode] = useState<'original' | 'simple'>('original')
  const [simpleCache, setSimpleCache] = useState<Record<string, string>>({})
  const [loadingSimple, setLoadingSimple] = useState(false)
  const [showRuler, setShowRuler] = useState(false)
  const [textSize, setTextSize] = useState<'normal' | 'large'>('normal')
  const [lastResult, setLastResult] = useState<'idle' | 'correct' | 'incorrect' | 'rateLimited'>('idle')
  const [difficulty, setDifficulty] = useState<'standard' | 'easy'>('standard')
  const [loadingQuestions, setLoadingQuestions] = useState(false)
  const [audioLoading, setAudioLoading] = useState(false)
  const [audioError, setAudioError] = useState('')
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [wordTimings, setWordTimings] = useState<WordTiming[]>([])
  const [currentWordIndex, setCurrentWordIndex] = useState<number>(-1)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const fragmentRef = useRef<HTMLDivElement | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  
  // Score tracking state
  const [scoreTracker, setScoreTracker] = useState<{
    correct: number
    incorrect: number
    fragmentScores: Record<string, { correct: number; incorrect: number }>
  }>({
    correct: 0,
    incorrect: 0,
    fragmentScores: {}
  })
  const [showFinalResults, setShowFinalResults] = useState(false)
  const [justUploaded, setJustUploaded] = useState(false)
  const [questionCache, setQuestionCache] = useState<Record<number, string[]>>({})
  const [allQuestionsLoaded, setAllQuestionsLoaded] = useState(false)
  const [batchGenerating, setBatchGenerating] = useState(false)

  const currentQuestion = useMemo(() => questions[qIndex] || '', [questions, qIndex])

  const cacheKey = selectedText && selectedPart ? `${language}::${selectedText}::${selectedPart}` : ''

  const displayText = useMemo(() => {
    if (textMode === 'simple' && cacheKey) {
      return simpleCache[cacheKey] ?? fragment
    }
    return fragment
  }, [textMode, cacheKey, simpleCache, fragment])

  useEffect(() => {
    listTexts(language)
      .then(data => setTexts(data))
      .catch(() => setTexts([]))
  }, [language])

  useEffect(() => {
    if (!texts.length) return
    const stored = localStorage.getItem('reading:lastUploaded')
    const preferred =
      stored && texts.find(t => t.name === stored) ? stored : texts[0]?.name
    if (preferred) {
      setSelectedText(preferred)
      // Mark as just uploaded for visual feedback
      if (stored) {
        setJustUploaded(true)
        setTimeout(() => setJustUploaded(false), 4000) // Clear after 4 seconds
      }
    }
    localStorage.removeItem('reading:lastUploaded')
  }, [texts])

  useEffect(() => {
    if (!selectedText) {
      setParts({})
      setFragment('')
      setQuestions([])
      setSelectedPart('')
      return
    }
    getParts(selectedText, language)
      .then(p => {
        setParts(p)
        const first = Object.keys(p)[0]
        if (first) {
          setSelectedPart(first)
          setFragment(p[first])
          setTextMode('original')
          // Don't auto-generate questions - user should click batch button
          setQuestions([])
          setQIndex(0)
          setAnswer('')
          setFeedback('')
          
          // Auto-scroll to fragment after upload
          if (justUploaded) {
            setTimeout(() => {
              fragmentRef.current?.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
              })
            }, 300)
          }
        }
      })
      .catch(() => setParts({}))
  }, [selectedText, language, justUploaded])

  useEffect(() => {
    setRenderedFragment(
      buildFragmentHtml(displayText, language, highlight, uppercase, wordTimings, currentWordIndex)
    )
  }, [displayText, language, highlight, uppercase, wordTimings, currentWordIndex])

  async function loadQuestions(mode: 'standard' | 'easy' = difficulty, overrideText?: string) {
    // 1. Check cache first if we're not forcing a specific text and mode hasn't changed
    const fragmentIndex = Object.keys(parts).indexOf(selectedPart)
    if (allQuestionsLoaded && questionCache[fragmentIndex] && !overrideText && mode === difficulty) {
      console.log(`✅ Using cached questions for fragment ${fragmentIndex}`)
      setQuestions(questionCache[fragmentIndex])
      setQIndex(0)
      setAnswer('')
      setFeedback('')
      setHighlight(null)
      setLastResult('idle')
      return
    }

    const source =
      overrideText ??
      (textMode === 'simple' && cacheKey ? simpleCache[cacheKey] ?? fragment : fragment)
    
    if (!source) return
    
    setLoadingQuestions(true)
    try {
      const qs = await generateQuestions(source, [], language, mode)
      setQuestions(qs)
      setDifficulty(mode)
      setQIndex(0)
      setAnswer('')
      setFeedback('')
      setHighlight(null)
      setLastResult('idle')
      
      // Update cache if this was for the current fragment
      if (!overrideText) {
        setQuestionCache(prev => ({ ...prev, [fragmentIndex]: qs }))
      }
    } catch (err) {
      console.error('failed to load questions', err)
    } finally {
      setLoadingQuestions(false)
    }
  }

  async function handleBatchGenerateQuestions() {
    if (!selectedText || !parts || Object.keys(parts).length === 0) return
    
    setBatchGenerating(true)
    setQuestionCache({})
    setAllQuestionsLoaded(false)
    
    try {
      const fragmentsArray = Object.values(parts)
      const result = await generateQuestionsBatch(
        selectedText,
        fragmentsArray,
        language,
        difficulty
      )
      
      // Store all questions in cache
      setQuestionCache(result.questions_by_fragment)
      setAllQuestionsLoaded(true)
      
      // Load questions for current fragment
      const currentFragmentIndex = Object.keys(parts).indexOf(selectedPart)
      if (currentFragmentIndex >= 0 && result.questions_by_fragment[currentFragmentIndex]) {
        setQuestions(result.questions_by_fragment[currentFragmentIndex])
        setQIndex(0)
        setAnswer('')
        setFeedback('')
        setHighlight(null)
        setLastResult('idle')
      }
      
      console.log(`✅ Generated questions for ${result.total_fragments} fragments in ${result.total_api_calls} API call(s)`)
    } catch (err: any) {
      console.error('Batch question generation failed', err)
      alert(err.response?.data?.detail || 'Failed to generate questions. Please try again.')
    } finally {
      setBatchGenerating(false)
    }
  }

  async function handleEvaluate() {
    if (!answer.trim() || !currentQuestion) return
    try {
      const res = await evaluate(displayText, currentQuestion, answer.trim(), language, undefined, strictness)
      setFeedback(res.feedback || '')
      setHighlight(res.correct_snippet ? { text: res.correct_snippet, correct: !!res.correct } : null)
      if (res.rate_limited) {
        setLastResult('rateLimited')
        return
      }
      
      // Update score tracker
      setScoreTracker(prev => ({
        ...prev,
        correct: prev.correct + (res.correct ? 1 : 0),
        incorrect: prev.incorrect + (res.correct ? 0 : 1),
        fragmentScores: {
          ...prev.fragmentScores,
          [selectedPart]: {
            correct: (prev.fragmentScores[selectedPart]?.correct || 0) + (res.correct ? 1 : 0),
            incorrect: (prev.fragmentScores[selectedPart]?.incorrect || 0) + (res.correct ? 0 : 1)
          }
        }
      }))
      
      setLastResult(res.correct ? 'correct' : 'incorrect')
    } catch (err) {
      console.error('evaluation failed', err)
    }
  }

  function handleNextQuestion() {
    setQIndex(i => i + 1)
    setAnswer('')
    setFeedback('')
    setHighlight(null)
    setLastResult('idle')
  }

  function handleAutoAdvance() {
    const isLastQuestion = qIndex >= questions.length - 1
    const partKeys = Object.keys(parts)
    const currentPartIndex = partKeys.indexOf(selectedPart)
    const isLastFragment = currentPartIndex >= partKeys.length - 1

    if (!isLastQuestion) {
      // Move to next question
      handleNextQuestion()
    } else if (!isLastFragment) {
      // Move to next fragment
      const nextPart = partKeys[currentPartIndex + 1]
      handlePartChange(nextPart)
    } else {
      // Show final results
      setShowFinalResults(true)
    }
  }

  function handlePartChange(part: string) {
    setSelectedPart(part)
    const frag = parts[part]
    setFragment(frag)
    setTextMode('original')
    setHighlight(null)
    setLastResult('idle')
    setAnswer('')
    setFeedback('')
    setShowFinalResults(false)
    
    // Check if we have cached questions for this fragment
    const fragmentIndex = Object.keys(parts).indexOf(part)
    if (allQuestionsLoaded && questionCache[fragmentIndex]) {
      // Use cached questions
      setQuestions(questionCache[fragmentIndex])
      setQIndex(0)
      console.log(`✅ Using cached questions for fragment ${fragmentIndex}`)
    } else {
      // No cached questions - user should use batch generation button
      setQuestions([])
      setQIndex(0)
    }
  }

  async function handleModeChange(mode: 'original' | 'simple') {
    if (mode === textMode) return
    if (!selectedPart || !selectedText) {
      setTextMode('original')
      return
    }
    
    if (mode === 'simple') {
      const key = cacheKey
      if (key && !simpleCache[key]) {
        try {
          setLoadingSimple(true)
          const source = parts[selectedPart]
          if (!source) return
          const simplified = await simplify(source, language, 'default')
          setSimpleCache(prev => ({ ...prev, [key]: simplified }))
          setFragment(simplified)
          
          // Only load new questions if we don't have any yet
          if (questions.length === 0) {
            loadQuestions(difficulty, simplified)
          }
        } catch (err) {
          console.error('Failed to simplify', err)
          setTextMode('original')
          return
        } finally {
          setLoadingSimple(false)
        }
      } else if (key && simpleCache[key]) {
        setFragment(simpleCache[key])
        // Only load new questions if we don't have any yet
        if (questions.length === 0) {
          loadQuestions(difficulty, simpleCache[key])
        }
      }
    }
    
    if (mode === 'original') {
      const base = parts[selectedPart]
      if (base) {
        setFragment(base)
        // Only load new questions if we don't have any yet
        if (questions.length === 0) {
          loadQuestions(difficulty, base)
        }
      }
    }
    setTextMode(mode)
  }

  async function handleReadAgain() {
    fragmentRef.current?.scrollIntoView({ behavior: 'smooth' })
    await loadQuestions(difficulty)
  }

  async function handleAudio(kind: 'fragment' | 'question') {
    const target = kind === 'fragment' ? displayText : currentQuestion
    if (!target) return
    
    setAudioLoading(true)
    setAudioError('')

    try {
      const { audio, mime, words } = await synthesizeAudio(target, language)
      
      // Create data URL for audio player
      const dataUrl = `data:${mime};base64,${audio}`
      
      if (kind === 'fragment') {
        // For fragment audio, show persistent player with word highlighting
        setAudioUrl(dataUrl)
        setWordTimings(words || [])
        setCurrentWordIndex(-1)
        setFragmentReading(false)
      } else {
        // For question audio, play immediately without showing player
        const tempAudio = new Audio(dataUrl)
        tempAudio.play()
      }
      
      setAudioLoading(false)
    } catch (err) {
      console.error('audio synthesis failed', err)
      setAudioLoading(false)
      setAudioError(t.storyAudioError)
    }
  }

  function stopAudio() {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }
    setAudioUrl(null)
    setWordTimings([])
    setCurrentWordIndex(-1)
    setFragmentReading(false)
  }
  
  // Track audio playback and update current word
  function trackAudioProgress() {
    if (!audioRef.current || wordTimings.length === 0) return
    
    const currentTime = audioRef.current.currentTime
    
    // Find which word should be highlighted based on current time
    const wordIndex = wordTimings.findIndex(
      (timing, idx) => {
        const nextTiming = wordTimings[idx + 1]
        return currentTime >= timing.start && (!nextTiming || currentTime < nextTiming.start)
      }
    )
    
    if (wordIndex !== currentWordIndex) {
      setCurrentWordIndex(wordIndex)
    }
    
    // Continue tracking if audio is playing
    if (!audioRef.current.paused) {
      animationFrameRef.current = requestAnimationFrame(trackAudioProgress)
    }
  }

  return (
    <div>
      <header className="app-header">
        <div>
          <h1>Reading Coach</h1>
          <p style={{ margin: 0, color: '#6a6f91' }}>{t.libraryTitle}</p>
        </div>
      </header>

      {/* Upload Success Banner */}
      {justUploaded && (
        <div className="upload-success-banner">
          {t.textLoadedSuccessfully} <strong>{selectedText}</strong>
        </div>
      )}

      <div className="top-settings panel">
        <div className="setting-grid">
          <label>
            {t.languageLabel}
            <select value={language} onChange={e => onLanguageChange(e.target.value as Lang)}>
              {LANGS.map(l => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t.chooseText}
            <select value={selectedText} onChange={e => setSelectedText(e.target.value)}>
              {texts.length === 0 && <option value="">{t.chooseText}</option>}
              {texts.map(text => (
                <option key={text.name} value={text.name}>
                  {text.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t.choosePart}
            <select value={selectedPart} onChange={e => handlePartChange(e.target.value)} disabled={!Object.keys(parts).length}>
              {Object.keys(parts).map(part => (
                <option key={part} value={part}>
                  {part}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t.strictnessLabel}
            <select value={strictness} onChange={e => setStrictness(Number(e.target.value))}>
              {STRICTNESS_LEVELS.map((level, idx) => (
                <option key={level} value={level}>
                  {t.strictness[idx]}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="workspace">
        <div className="reading-split">
          <aside className="left-toolbar panel">
            <div className="toolbar-group">
              <span>{t.toolsLabel}</span>
              <button 
                className={`tool-button ${uppercase ? 'active' : ''}`} 
                onClick={() => setUppercase(v => !v)}
                title={t.uppercase}
              >
                {uppercase ? 'Aa' : 'AA'}
              </button>
              <button 
                className={`tool-button ${showRuler ? 'active' : ''}`} 
                onClick={() => setShowRuler(v => !v)}
                title={t.toolRuler}
              >
                ≡ {t.toolRuler}
              </button>
              <button
                className={`tool-button ${textSize === 'large' ? 'active' : ''}`}
                onClick={() => setTextSize(p => (p === 'large' ? 'normal' : 'large'))}
                title={t.toolSize}
              >
                {textSize === 'large' ? 'A-' : 'A+'}
              </button>
            </div>
          </aside>

          <section className="text-zone">
            <div className="text-content panel">
              <div className="panel-title">{selectedText || t.libraryTitle}</div>
              <div className="text-header-actions">
                <div className="mode-inline">
                  <button
                    className={`mode-button ${textMode === 'original' ? 'active' : ''}`}
                    onClick={() => handleModeChange('original')}
                    disabled={!fragment}
                  >
                    {t.modeOriginal}
                  </button>
                  <button
                    className={`mode-button ${textMode === 'simple' ? 'active' : ''}`}
                    onClick={() => handleModeChange('simple')}
                    disabled={!fragment || loadingSimple}
                  >
                    {loadingSimple ? '…' : t.modeSimple}
                  </button>
                </div>
                <div className="audio-controls">
                  {audioUrl ? (
                    <button className="story-audio-btn playing" onClick={stopAudio}>
                      ✕ Close Audio
                    </button>
                  ) : (
                    <button 
                      className="story-audio-btn" 
                      onClick={() => handleAudio('fragment')} 
                      disabled={!displayText || audioLoading}
                    >
                      {audioLoading ? '⏳ ' + t.storyAudioLoading : '🔊 ' + t.storyAudio}
                    </button>
                  )}
                </div>
              </div>
              {audioError && (
                <div className="audio-error">{audioError}</div>
              )}
              {audioUrl && (
                <audio 
                  ref={audioRef}
                  src={audioUrl} 
                  controls 
                  autoPlay
                  style={{ width: '100%', marginTop: '12px' }}
                  onPlay={() => {
                    setFragmentReading(true)
                    trackAudioProgress()
                  }}
                  onPause={() => {
                    setFragmentReading(false)
                    if (animationFrameRef.current) {
                      cancelAnimationFrame(animationFrameRef.current)
                      animationFrameRef.current = null
                    }
                  }}
                  onEnded={() => {
                    setFragmentReading(false)
                    setCurrentWordIndex(-1)
                    if (animationFrameRef.current) {
                      cancelAnimationFrame(animationFrameRef.current)
                      animationFrameRef.current = null
                    }
                  }}
                  onSeeked={() => {
                    // Restart tracking when user seeks
                    if (!audioRef.current?.paused) {
                      trackAudioProgress()
                    }
                  }}
                />
              )}
              <div
                ref={fragmentRef}
                className={`fragment-view ${textSize === 'large' ? 'large' : ''} ${showRuler ? 'with-ruler' : ''} ${
                  isFragmentReading ? 'fragment-reading' : ''
                }`}
                dangerouslySetInnerHTML={{
                  __html: renderedFragment || `<em>${selectedText ? '(no text loaded)' : t.chooseText}</em>`,
                }}
              />
            </div>
          </section>

          <section className="qa-panel panel">
            <div className="qa-panel-head">
              <div>
                <div className="panel-title">{t.questionTitle}</div>
                <small className="qa-progress-count">
                  {questions.length ? `${qIndex + 1}/${questions.length}` : '--'}
                </small>
              </div>
              <button
                className={`batch-generate-btn ${allQuestionsLoaded ? 'loaded' : ''}`}
                onClick={handleBatchGenerateQuestions}
                disabled={!selectedText || Object.keys(parts).length === 0 || batchGenerating}
                style={{ marginBottom: '12px' }}
              >
                {batchGenerating ? '⏳ ' + t.generatingAllQuestions : 
                 allQuestionsLoaded ? '✅ ' + t.questionsGenerated : 
                 '🎯 ' + t.generateAllQuestions}
              </button>
              <div className="difficulty-row">
                {DIFFICULTIES.map(diff => (
                  <button
                    key={diff.key}
                    onClick={() => loadQuestions(diff.key)}
                    className={`tool-button ${difficulty === diff.key ? 'active' : ''}`}
                    disabled={!displayText || loadingQuestions}
                  >
                    {t[diff.labelKey]}
                  </button>
                ))}
              </div>
            </div>

            {loadingQuestions && (
              <div className="loading-message">{t.regenerateQuestionsLoading}</div>
            )}

            <div className={`result-banner ${lastResult}`}>
              <strong>{t.resultLabel}:</strong>
              <span>{feedback || t.resultEmpty}</span>
            </div>

            <div className="qa-body">
              <div className="qa-question-block">
                <p>{currentQuestion || t.noQuestions}</p>
                <button 
                  className="question-audio-btn" 
                  onClick={() => handleAudio('question')} 
                  disabled={!currentQuestion}
                  title={t.audioQuestion}
                >
                  🎧 {t.audioQuestion}
                </button>
              </div>

              <label>{t.answerLabel}</label>
              <textarea
                value={answer}
                onChange={e => setAnswer(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && e.ctrlKey) {
                    handleEvaluate()
                  }
                }}
                placeholder={t.answerPlaceholder}
                className="answer-input"
                disabled={!currentQuestion}
                rows={3}
              />
              <button 
                onClick={handleEvaluate} 
                disabled={!answer.trim() || !currentQuestion}
                className="submit-btn"
              >
                {t.submitButton}
              </button>
              
              {(lastResult === 'correct' || lastResult === 'incorrect') && (
                <button 
                  onClick={handleAutoAdvance}
                  className="next-btn"
                >
                  {t.nextQuestion} →
                </button>
              )}
            </div>

            <button 
              className="read-again-btn" 
              onClick={handleReadAgain}
              disabled={!displayText || loadingQuestions}
              title={t.readAgain}
            >
              🔁 {t.readAgain}
            </button>
          </section>
        </div>
      </div>

      {/* Final Results Modal */}
      {showFinalResults && (
        <div className="final-results-overlay" onClick={() => {}}>
          <div className="final-results-modal" onClick={(e) => e.stopPropagation()}>
            <h2>{t.storyCompleted}</h2>
            <div className="score-summary">
              <div className="score-big">
                {scoreTracker.correct} / {scoreTracker.correct + scoreTracker.incorrect}
              </div>
              <p>{t.correctAnswers}</p>
            </div>
            <div className="fragment-breakdown">
              <h3>{t.fragmentScore}:</h3>
              {Object.entries(scoreTracker.fragmentScores).map(([part, score]) => (
                <div key={part} className="fragment-score-row">
                  <strong>{part}:</strong>
                  <span className="score-value">
                    {score.correct}/{score.correct + score.incorrect}
                  </span>
                </div>
              ))}
            </div>
            <button 
              className="start-over-btn"
              onClick={() => {
                setShowFinalResults(false)
                setScoreTracker({ correct: 0, incorrect: 0, fragmentScores: {} })
                // Reset to first fragment
                const firstPart = Object.keys(parts)[0]
                if (firstPart) handlePartChange(firstPart)
              }}
            >
              🔁 {t.startOver}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
