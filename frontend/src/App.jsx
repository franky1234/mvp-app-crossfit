import GenerateForm from './components/GenerateForm'

export default function App(){
  const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
  return (
    <div style={{padding:20, fontFamily:'Arial, sans-serif', maxWidth:800, margin:'0 auto'}}>
      <h1>CrossFit GPT‑4 — MVP</h1>
      <GenerateForm apiBase={apiBase} />
    </div>
  )
}
