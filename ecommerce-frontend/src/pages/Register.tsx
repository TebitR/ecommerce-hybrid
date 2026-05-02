import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'

export default function Register() {
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    const payload = {
      username: form.username,
      email: form.email,
      password: form.password,
      password_confirm: form.password_confirm,
    }
    console.log('Payload envoyé:', {
      username: form.username,
      email: form.email,
      password: '***',
      password_confirm: '***',
    })
    try {
      const res = await fetch('http://localhost:8000/api/v1/users/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}))
        console.warn('Réponse inscription:', res.status, detail)
        throw new Error('Erreur inscription')
      }
      navigate('/login')
    } catch {
      setError('Erreur lors de l\'inscription')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-nw-gray-50 py-12 px-4">
      <div className="nw-card p-6 md:p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-nw-navy text-center mb-6">Créer un compte</h1>
        {error && <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm mb-4">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input className="nw-input" placeholder="Nom d'utilisateur" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} required />
          <input type="email" className="nw-input" placeholder="Email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required />
          <input type="password" className="nw-input" placeholder="Mot de passe" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required />
          <input type="password" className="nw-input" placeholder="Confirmer mot de passe" value={form.password_confirm} onChange={e => setForm({ ...form, password_confirm: e.target.value })} required />
          <button type="submit" className="nw-btn-primary w-full" disabled={loading}>{loading ? 'Création...' : 'S\'inscrire'}</button>
        </form>
        <p className="text-center text-sm text-nw-gray-600 mt-4">
          Déjà inscrit ? <Link to="/login" className="text-nw-green-600 font-medium">Connexion</Link>
        </p>
      </div>
    </div>
  )
}
