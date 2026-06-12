import { useState, type FormEvent } from 'react'
import { DJANGO_API } from '../config/api'
import { Link } from 'react-router-dom'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      const res = await fetch(`${DJANGO_API}/users/reset-request/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })
      const data = (await res.json()) as { message?: string }
      setMessage(data.message ?? 'Si un compte existe, un lien a été envoyé.')
    } catch {
      setMessage('Erreur réseau.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-nw-gray-50 py-12 px-4">
      <div className="nw-card p-6 md:p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-nw-navy text-center mb-6">Mot de passe oublié</h1>
        <p className="text-sm text-nw-gray-600 mb-4">Indiquez votre email : vous recevrez un lien (ou consultez la console Django en dev).</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            className="nw-input"
            placeholder="Email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
          />
          <button type="submit" className="nw-btn-primary w-full" disabled={loading}>
            {loading ? 'Envoi...' : 'Envoyer le lien'}
          </button>
        </form>
        {message && <p className="text-sm text-nw-green-700 mt-4 text-center">{message}</p>}
        <p className="text-center text-sm text-nw-gray-600 mt-4">
          <Link to="/login" className="text-nw-green-600 font-medium">Retour à la connexion</Link>
        </p>
      </div>
    </div>
  )
}
