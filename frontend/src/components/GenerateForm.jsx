import { useState } from 'react'

export default function GenerateForm({ apiBase }){
  const [level, setLevel] = useState('intermedio')
  const [duration, setDuration] = useState(45)
  const [goals, setGoals] = useState('Mejorar resistencia y fuerza')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  async function handleSubmit(e){
    e.preventDefault()
    setLoading(true)
    setResult(null)

    const res = await fetch(`${apiBase}/generate`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({level, duration_minutes: Number(duration), goals})
    })

    if(!res.ok){
      const text = await res.text()
      setResult({error: text})
      setLoading(false)
      return
    }

    const data = await res.json()
    setResult(data)
    setLoading(false)
  }

  return (
    <form onSubmit={handleSubmit} style={{display:'grid', gap:12}}>
      <label>
        Nivel
        <select value={level} onChange={e=>setLevel(e.target.value)}>
          <option value="principiante">Principiante</option>
          <option value="intermedio">Intermedio</option>
          <option value="avanzado">Avanzado</option>
        </select>
      </label>

      <label>
        Duración (min)
        <input type="number" value={duration} onChange={e=>setDuration(e.target.value)} min={10} max={120} />
      </label>

      <label>
        Objetivos
        <input value={goals} onChange={e=>setGoals(e.target.value)} />
      </label>

      <button type="submit" disabled={loading}>{loading? 'Generando...':'Generar rutina'}</button>

      {result && (
        <div style={{marginTop:12}}>
          {result.error ? <pre>{result.error}</pre> : (
            <div>
              <h3>{result.title || 'Rutina'}</h3>
              <p><strong>Notas:</strong></p>
              <pre>{result.raw_text || JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </form>
  )
}
