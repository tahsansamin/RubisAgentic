import { useState } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSend = async () => {
    if (!message.trim()) return

    setLoading(true)
    setError('')
    setResponse('')

    try {
      const res = await fetch('http://127.0.0.1:8000/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: message }),
      })

      if (!res.ok) {
        throw new Error(`${res.status} ${res.statusText}`)
      }

      const data = await res.json()
      setResponse(data.message ?? JSON.stringify(data))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <h1>Send a message to the bot</h1>
      <p>Type a paragraph below and click <strong>Send to bot</strong>.</p>

      <textarea
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        placeholder="Write your message here..."
        rows={8}
      />

      <button type="button" onClick={handleSend} disabled={loading || !message.trim()}>
        {loading ? 'Sending…' : 'Send to bot'}
      </button>

      {response && (
        <div className="response-box">
          <h2>Bot response</h2>
          <pre>{response}</pre>
        </div>
      )}

      {error && <div className="error-box">{error}</div>}
    </main>
  )
}

export default App
