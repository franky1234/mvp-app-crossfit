import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './styles.css'

function mount() {
	const root = document.getElementById('root')
	if (!root) return
	try {
		createRoot(root).render(<App />)
	} catch (e) {
		// fallback: attach on next tick
		setTimeout(() => createRoot(root).render(<App />), 0)
	}
	try {
		// mark that the app mounted (useful for smoke tests)
		document.body.dataset.appMounted = 'true'
	} catch {}
}

if (document.readyState === 'loading') {
	document.addEventListener('DOMContentLoaded', mount)
} else {
	mount()
}
