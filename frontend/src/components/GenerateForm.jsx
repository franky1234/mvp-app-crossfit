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
        <div style={{marginTop:20, padding:20, backgroundColor:'#f5f5f5', borderRadius:8}}>
          {result.error ? (
            <div style={{color:'red'}}>
              <h3>Error</h3>
              <pre style={{whiteSpace:'pre-wrap'}}>{result.error}</pre>
            </div>
          ) : (
            <div>
              <h2 style={{marginTop:0, color:'#2c3e50'}}>{result.title || 'Rutina CrossFit'}</h2>
              <p><strong>Nivel:</strong> {result.level} | <strong>Duración:</strong> {result.duration_minutes} min</p>
              
              {result.warmup && result.warmup.length > 0 && (
                <div style={{marginTop:20}}>
                  <h3 style={{color:'#e67e22'}}>🔥 Calentamiento</h3>
                  <ul>
                    {result.warmup.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.exercises && result.exercises.length > 0 && (
                <div style={{marginTop:20}}>
                  <h3 style={{color:'#27ae60'}}>💪 Ejercicios</h3>
                  {result.exercises.map((ex, i) => (
                    <div key={i} style={{marginBottom:15, padding:15, backgroundColor:'white', borderRadius:6, border:'1px solid #ddd'}}>
                      <h4 style={{margin:'0 0 8px 0', color:'#2c3e50'}}>{i+1}. {ex.name}</h4>
                      <p style={{margin:0}}>
                        <strong>Sets:</strong> {ex.sets} | 
                        <strong> Reps/Tiempo:</strong> {ex.reps_or_time}
                        {ex.rest_seconds && ` | Descanso: ${ex.rest_seconds}s`}
                      </p>
                      {ex.notes && <p style={{margin:'8px 0 0 0', fontSize:'0.9em', color:'#7f8c8d'}}><em>{ex.notes}</em></p>}
                    </div>
                  ))}
                </div>
              )}

              {result.cooldown && result.cooldown.length > 0 && (
                <div style={{marginTop:20}}>
                  <h3 style={{color:'#3498db'}}>🧘 Enfriamiento</h3>
                  <ul>
                    {result.cooldown.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.modifications && Object.keys(result.modifications).length > 0 && (
                <div style={{marginTop:20}}>
                  <h3 style={{color:'#9b59b6'}}>⚙️ Modificaciones</h3>
                  {result.modifications.principiante && (
                    <div style={{marginBottom:10}}>
                      <strong>Principiante:</strong> {result.modifications.principiante}
                    </div>
                  )}
                  {result.modifications.avanzado && (
                    <div>
                      <strong>Avanzado:</strong> {result.modifications.avanzado}
                    </div>
                  )}
                </div>
              )}

              <details style={{marginTop:20}}>
                <summary style={{cursor:'pointer', color:'#7f8c8d'}}>Ver JSON completo</summary>
                <pre style={{marginTop:10, padding:10, backgroundColor:'#2c3e50', color:'#ecf0f1', borderRadius:4, overflow:'auto'}}>
                  {JSON.stringify(result, null, 2)}
                </pre>
              </details>
            </div>
          )}
        </div>
      )}
    </form>
  )
}
