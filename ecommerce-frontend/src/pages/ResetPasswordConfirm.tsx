import { useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

export default function ResetPasswordConfirm() {
  const { uid, token } = useParams<{ uid: string; token: string }>()
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    if (password !== password2) {
      setError('Les mots de passe ne correspondent pas.')
      return
    }
    if (!uid || !token) {
      setError('Lien invalide.')
      return
    }
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/v1/users/reset-confirm/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid, token, new_password: password }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        setError((err as { error?: string }).error ?? 'Échec')
        return
      }
      navigate('/login')
    } catch {
      setError('Erreur réseau.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-nw-gray-50 py-12 px-4">
      <div className="nw-card p-6 md:p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-nw-navy text-center mb-6">Nouveau mot de passe</h1>
        {error && <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm mb-4">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="password" className="nw-input" placeholder="Nouveau mot de passe" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} />
          <input type="password" className="nw-input" placeholder="Confirmer" value={password2} onChange={e => setPassword2(e.target.value)} required />
          <button type="submit" className="nw-btn-primary w-full" disabled={loading}>{loading ? 'Enregistrement...' : 'Enregistrer'}</button>
        </form>
        <p className="text-center text-sm text-nw-gray-600 mt-4">
          <Link to="/login" className="text-nw-green-600 font-medium">Connexion</Link>
        </p>
      </div>
    </div>
  )
}
