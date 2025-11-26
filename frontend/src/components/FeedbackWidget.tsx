import React, { useState } from 'react'

type Props = {
  endpoint?: string
}

export const FeedbackWidget: React.FC<Props> = ({ endpoint }) => {
  const [open, setOpen] = useState(false)
  const [rating, setRating] = useState<number | undefined>(undefined)
  const [comment, setComment] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [sent, setSent] = useState(false)

  const submit = async () => {
    if (!rating && !comment) return
    setSubmitting(true)
    try {
      await fetch(`${endpoint || ''}/api/v1/rum/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          rating,
          comment,
          context: { path: window.location.pathname }
        }),
      })
      setSent(true)
      setTimeout(() => setOpen(false), 1200)
      setRating(undefined)
      setComment('')
    } catch (e) {
      // ignore
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {!open ? (
        <button
          className="bg-blue-600 text-white px-3 py-2 rounded shadow hover:bg-blue-700 text-sm"
          onClick={() => setOpen(true)}
          aria-label="Open feedback form"
        >
          Feedback
        </button>
      ) : (
        <div className="bg-white dark:bg-gray-800 text-sm rounded-lg shadow-lg p-4 w-80 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="font-semibold">Your feedback</div>
            <button onClick={() => setOpen(false)} aria-label="Close" className="text-gray-500">✕</button>
          </div>
          {!sent ? (
            <div className="space-y-3">
              <div>
                <label className="block text-xs mb-1">Rating (1-5)</label>
                <select
                  className="w-full border rounded p-1 dark:bg-gray-900"
                  value={rating ?? ''}
                  onChange={(e) => setRating(e.target.value ? Number(e.target.value) : undefined)}
                >
                  <option value="">No rating</option>
                  {[1,2,3,4,5].map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs mb-1">Comment</label>
                <textarea
                  className="w-full border rounded p-2 resize-none h-20 dark:bg-gray-900"
                  maxLength={2000}
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="How can we improve? (no personal/PHI data)"
                />
              </div>
              <button
                onClick={submit}
                disabled={submitting || (!rating && !comment)}
                className="w-full bg-green-600 text-white py-2 rounded disabled:opacity-50"
              >
                {submitting ? 'Sending…' : 'Send'}
              </button>
            </div>
          ) : (
            <div className="text-green-600">Thanks for your feedback!</div>
          )}
        </div>
      )}
    </div>
  )
}


