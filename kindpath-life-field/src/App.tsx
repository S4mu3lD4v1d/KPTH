import { ChangeEvent, useEffect, useState } from 'react'
import './App.css'

type ModuleKey =
  | 'snapshot'
  | 'idealLife'
  | 'creativity'
  | 'community'
  | 'gapMap'
  | 'experiments'
  | 'weeklyCheckins'

type SectionType = 'textarea' | 'list'

type SectionConfig = {
  id: string
  title: string
  type: SectionType
  placeholder?: string
  helper?: string
}

type ModuleConfig = {
  key: ModuleKey
  title: string
  description: string
  accent: string
  sections: SectionConfig[]
}

type ModuleData = Record<ModuleKey, Record<string, string | string[]>>
type DraftState = Record<ModuleKey, Record<string, string>>

const STORAGE_KEY = 'kindpath-life-field'

const modules: ModuleConfig[] = [
  {
    key: 'snapshot',
    title: 'Snapshot',
    description: 'How life feels right now and the signals you are noticing.',
    accent: '#b472ff',
    sections: [
      {
        id: 'currentState',
        title: 'Current State',
        type: 'textarea',
        placeholder: 'What is true right now? Energy, routines, constraints.',
      },
      {
        id: 'evidence',
        title: 'Evidence & Signals',
        type: 'list',
        placeholder: 'Wins, tensions, feedback you are collecting.',
      },
      {
        id: 'feelings',
        title: 'How It Feels',
        type: 'list',
        placeholder: 'Words that describe the vibe of this season.',
      },
    ],
  },
  {
    key: 'idealLife',
    title: 'Ideal Life',
    description: 'Describe the life you are designing toward.',
    accent: '#68d4ff',
    sections: [
      {
        id: 'narrative',
        title: 'Narrative',
        type: 'textarea',
        placeholder: 'Paint the scene for the life you want.',
      },
      {
        id: 'outcomes',
        title: 'Defining Outcomes',
        type: 'list',
        placeholder: 'Health, work, relationships, money, environment.',
      },
      {
        id: 'habits',
        title: 'Daily Practices',
        type: 'list',
        placeholder: 'Micro-behaviors that make the ideal life inevitable.',
      },
    ],
  },
  {
    key: 'creativity',
    title: 'Creativity',
    description: 'Projects, sparks, and constraints that help you ship.',
    accent: '#ffd166',
    sections: [
      {
        id: 'projects',
        title: 'Active Projects',
        type: 'list',
        placeholder: 'Name the creative tracks you are moving.',
      },
      {
        id: 'sparks',
        title: 'Sparks',
        type: 'list',
        placeholder: 'Ideas, references, people, or quotes to explore.',
      },
      {
        id: 'constraints',
        title: 'Creative Constraints',
        type: 'textarea',
        placeholder: 'Rules that keep you prolific (formats, schedules, limits).',
      },
    ],
  },
  {
    key: 'community',
    title: 'Community',
    description: 'Who you are traveling with and how you show up for them.',
    accent: '#7bd88f',
    sections: [
      {
        id: 'people',
        title: 'People & Circles',
        type: 'list',
        placeholder: 'Communities, mentors, collaborators.',
      },
      {
        id: 'collaborations',
        title: 'Collaboration Ideas',
        type: 'list',
        placeholder: 'Things to build, host, or ship together.',
      },
      {
        id: 'support',
        title: 'Support Needs',
        type: 'textarea',
        placeholder: 'What you need from the room right now.',
      },
    ],
  },
  {
    key: 'gapMap',
    title: 'Gap Map',
    description: 'Where reality and the vision diverge, and how to close it.',
    accent: '#ff8ba7',
    sections: [
      {
        id: 'frictions',
        title: 'Frictions',
        type: 'list',
        placeholder: 'Blocks, resource gaps, patterns that keep showing up.',
      },
      {
        id: 'opportunities',
        title: 'Opportunities',
        type: 'list',
        placeholder: 'Moments to leverage, shortcuts, relationships.',
      },
      {
        id: 'bridges',
        title: 'Possible Bridges',
        type: 'textarea',
        placeholder: 'What would collapse the gap? Systems, rhythms, asks.',
      },
    ],
  },
  {
    key: 'experiments',
    title: 'Experiments',
    description: 'Run small bets that test what matters.',
    accent: '#74b9ff',
    sections: [
      {
        id: 'active',
        title: 'Active',
        type: 'list',
        placeholder: 'Hypotheses you are currently running.',
      },
      {
        id: 'next',
        title: 'Next Up',
        type: 'list',
        placeholder: 'Experiments queued for this month.',
      },
      {
        id: 'learning',
        title: 'Learning Notes',
        type: 'textarea',
        placeholder: 'What you are noticing, what to double down on.',
      },
    ],
  },
  {
    key: 'weeklyCheckins',
    title: 'Weekly Check-ins',
    description: 'Lightweight rituals to keep momentum.',
    accent: '#c792ea',
    sections: [
      {
        id: 'wins',
        title: 'Wins',
        type: 'list',
        placeholder: 'Moments to celebrate from this week.',
      },
      {
        id: 'mood',
        title: 'Mood & Energy',
        type: 'textarea',
        placeholder: 'How did the week feel? What spiked or dipped?',
      },
      {
        id: 'focus',
        title: 'Focus for Next Week',
        type: 'list',
        placeholder: 'Three commitments that would make next week a win.',
      },
    ],
  },
]

const createEmptyData = (): ModuleData =>
  modules.reduce((acc, module) => {
    const sections = module.sections.reduce((sectionAcc, section) => {
      sectionAcc[section.id] = section.type === 'list' ? [] : ''
      return sectionAcc
    }, {} as Record<string, string | string[]>)
    acc[module.key] = sections
    return acc
  }, {} as ModuleData)

const createDrafts = (): DraftState =>
  modules.reduce((acc, module) => {
    const drafts = module.sections.reduce((sectionAcc, section) => {
      if (section.type === 'list') {
        sectionAcc[section.id] = ''
      }
      return sectionAcc
    }, {} as Record<string, string>)
    acc[module.key] = drafts
    return acc
  }, {} as DraftState)

const mergeWithDefaults = (saved: unknown): ModuleData => {
  const base = createEmptyData()
  if (!saved || typeof saved !== 'object') return base

  modules.forEach((module) => {
    const moduleState = (saved as Record<string, unknown>)[module.key]
    if (!moduleState || typeof moduleState !== 'object') return

    module.sections.forEach((section) => {
      const sectionValue = (moduleState as Record<string, unknown>)[section.id]
      if (section.type === 'list') {
        if (Array.isArray(sectionValue) && sectionValue.every((item) => typeof item === 'string')) {
          base[module.key][section.id] = sectionValue
        }
      } else if (typeof sectionValue === 'string') {
        base[module.key][section.id] = sectionValue
      }
    })
  })

  return base
}

function App() {
  const [data, setData] = useState<ModuleData>(() => {
    if (typeof window === 'undefined') return createEmptyData()
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) return createEmptyData()

    try {
      return mergeWithDefaults(JSON.parse(saved))
    } catch (error) {
      console.warn('Could not parse saved data', error)
      return createEmptyData()
    }
  })
  const [drafts, setDrafts] = useState<DraftState>(() => createDrafts())
  const [importError, setImportError] = useState('')

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  }, [data])

  const handleTextChange = (moduleKey: ModuleKey, sectionId: string, value: string) => {
    setData((prev) => ({
      ...prev,
      [moduleKey]: {
        ...prev[moduleKey],
        [sectionId]: value,
      },
    }))
  }

  const handleDraftChange = (moduleKey: ModuleKey, sectionId: string, value: string) => {
    setDrafts((prev) => ({
      ...prev,
      [moduleKey]: {
        ...prev[moduleKey],
        [sectionId]: value,
      },
    }))
  }

  const addListItem = (moduleKey: ModuleKey, sectionId: string) => {
    const draftValue = drafts[moduleKey]?.[sectionId]?.trim()
    if (!draftValue) return

    setData((prev) => {
      const existing = prev[moduleKey][sectionId]
      const nextList = Array.isArray(existing) ? [...existing, draftValue] : [draftValue]

      return {
        ...prev,
        [moduleKey]: {
          ...prev[moduleKey],
          [sectionId]: nextList,
        },
      }
    })

    setDrafts((prev) => ({
      ...prev,
      [moduleKey]: {
        ...prev[moduleKey],
        [sectionId]: '',
      },
    }))
  }

  const removeListItem = (moduleKey: ModuleKey, sectionId: string, index: number) => {
    setData((prev) => {
      const existing = prev[moduleKey][sectionId]
      if (!Array.isArray(existing)) return prev

      const nextList = existing.filter((_, idx) => idx !== index)
      return {
        ...prev,
        [moduleKey]: {
          ...prev[moduleKey],
          [sectionId]: nextList,
        },
      }
    })
  }

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'kindpath-life-field.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  const handleImport = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const result = e.target?.result
        const parsed = result ? JSON.parse(String(result)) : {}
        setData(mergeWithDefaults(parsed))
        setImportError('')
      } catch (error) {
        console.error('Import failed', error)
        setImportError('Could not import file. Ensure it is valid JSON.')
      }
    }
    reader.readAsText(file)
    event.target.value = ''
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">KindPath</p>
          <h1>Life Field</h1>
          <p className="lede">
            A personal field kit to keep your life story coherent. Track where you are, where you&apos;re going, and
            the experiments that will get you there.
          </p>
        </div>
        <div className="actions">
          <button className="ghost" onClick={handleExport}>
            Export JSON
          </button>
          <label className="import">
            <input type="file" accept="application/json" onChange={handleImport} />
            Import JSON
          </label>
          {importError ? <p className="import-error">{importError}</p> : null}
        </div>
      </header>

      <div className="module-grid">
        {modules.map((module) => (
          <section key={module.key} className="module-card" style={{ borderColor: module.accent }}>
            <div className="module-heading">
              <div>
                <p className="eyebrow" style={{ color: module.accent }}>
                  {module.title}
                </p>
                <p className="muted">{module.description}</p>
              </div>
              <div className="accent-dot" style={{ background: module.accent }} />
            </div>

            {module.sections.map((section) => {
              const value = data[module.key][section.id]
              const draftValue = drafts[module.key]?.[section.id] ?? ''
              const isList = section.type === 'list'

              return (
                <div key={section.id} className="section">
                  <div className="section-title">
                    <h3>{section.title}</h3>
                    {section.helper ? <span className="helper">{section.helper}</span> : null}
                  </div>

                  {isList ? (
                    <div>
                      <div className="pill-row">
                        {Array.isArray(value) && value.length ? (
                          value.map((item, index) => (
                            <span key={`${section.id}-${index}`} className="pill">
                              {item}
                              <button
                                className="pill-remove"
                                aria-label={`Remove ${item}`}
                                onClick={() => removeListItem(module.key, section.id, index)}
                              >
                                ×
                              </button>
                            </span>
                          ))
                        ) : (
                          <p className="muted empty-state">No entries yet. Add your first one below.</p>
                        )}
                      </div>
                      <div className="add-row">
                        <input
                          type="text"
                          value={draftValue}
                          onChange={(e) => handleDraftChange(module.key, section.id, e.target.value)}
                          placeholder={section.placeholder}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              e.preventDefault()
                              addListItem(module.key, section.id)
                            }
                          }}
                        />
                        <button onClick={() => addListItem(module.key, section.id)}>Add</button>
                      </div>
                    </div>
                  ) : (
                    <textarea
                      value={typeof value === 'string' ? value : ''}
                      placeholder={section.placeholder}
                      onChange={(e) => handleTextChange(module.key, section.id, e.target.value)}
                      rows={4}
                    />
                  )}
                </div>
              )
            })}
          </section>
        ))}
      </div>
    </div>
  )
}

export default App
