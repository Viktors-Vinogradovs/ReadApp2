import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export const api = axios.create({ baseURL: API_BASE })

export type TextItem = { name: string; language: string; parts: Record<string, string> }

export async function listTexts(lang: string) {
  const res = await api.get<TextItem[]>(`/texts`, { params: { lang } })
  return res.data
}

export async function getParts(name: string, lang: string) {
  const res = await api.get<Record<string, string>>(`/texts/${encodeURIComponent(name)}/parts`, { params: { lang } })
  return res.data
}

export async function simplify(text: string, language: string, level: string = 'default') {
  const res = await api.post<{ text: string }>(`/qa/simplify`, { text, language, level })
  return res.data.text
}

export async function formatText(text: string, language: string) {
  const res = await api.post<{ text: string }>(`/qa/format`, { text, language })
  return res.data.text
}

export async function generateQuestions(fragment: string, previous: string[], language: string, difficulty: string = 'standard') {
  const res = await api.post<string[]>(`/qa/questions`, { fragment, previous_questions: previous, language, difficulty })
  return res.data
}

export async function evaluate(
  fragment: string,
  question: string,
  answer: string,
  language: string,
  userId?: string,
  strictness: number = 2,
) {
  const res = await api.post(`/qa/evaluate`, { fragment, question, answer, language, userId, strictness })
  return res.data as { feedback: string; correct_snippet: string; correct: boolean; rate_limited?: boolean }
}

export async function uploadText(
  name: string,
  language: string,
  text: string,
  autoSplit = true,
  fragmentTargetTokens = 400,
) {
  const res = await api.post(`/texts`, { name, language, text, autoSplit, fragmentTargetTokens })
  return res.data
}

export async function previewFragments(text: string, targetTokens: number) {
  const res = await api.post<{ fragments: string[] }>(`/texts/preview`, { text, targetTokens })
  return res.data.fragments
}

export type WordTiming = {
  word: string
  start: number
  end: number
}

export async function synthesizeAudio(text: string, language: string) {
  const res = await api.post<{ audio: string; mime: string; words: WordTiming[] }>(`/qa/audio`, { text, language })
  return res.data
}


