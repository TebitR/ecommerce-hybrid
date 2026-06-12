import { useState } from 'react'
import { DJANGO_API } from '../config/api'
import { Link, useNavigate } from 'react-router-dom'

export default function Register() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // État du formulaire
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    setError('') // Effacer l'erreur à chaque frappe
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    // DEBUG : Voir ce qui est envoyé dans la console navigateur (F12)
    console.log('📤 Payload envoyé à Django:', {
      username: form.username,
      email: form.email,
      password: '***',
      password_confirm: '***',
    })

    try {
      const response = await fetch(`${DJANGO_API}/users/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: form.username,
          email: form.email,
          password: form.password,
          password_confirm: form.password_confirm, // ← Champ OBLIGATOIRE
        }),
      })

      const data = await response.json()
      console.log('📥 Réponse Django:', data)

      if (!response.ok) {
        // Afficher l'erreur exacte de Django dans l'UI
        if (data.non_field_errors) {
          setError(data.non_field_errors.join(' '))
        } else if (data.password) {
          setError(data.password.join(' '))
        } else if (data.email) {
          setError(data.email.join(' '))
        } else {
          setError(JSON.stringify(data))
        }
        return
      }

      // Succès → Redirection
      console.log('✅ Inscription réussie, redirection vers /login')
      navigate('/login')
    } catch (err) {
      console.error('❌ Erreur réseau:', err)
      setError('Erreur de connexion au serveur. Vérifie que Django tourne.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-nw-gray-50 py-12 px-4">
      <div className="nw-card p-6 md:p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-nw-navy text-center mb-6">Créer un compte</h1>

        {/* Affichage des erreurs */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 mb-4 text-sm rounded">
            <p className="font-bold">Erreur :</p>
            <p>{error}</p>
            <p className="mt-2 text-xs opacity-70">💡 Ouvre la console (F12) pour plus de détails</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-nw-gray-700 mb-1">Nom d'utilisateur</label>
            <input
              name="username"
              value={form.username}
              onChange={handleChange}
              className="nw-input"
              placeholder="tebit"
              required
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-nw-gray-700 mb-1">Email</label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              className="nw-input"
              placeholder="test@example.com"
              required
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-nw-gray-700 mb-1">Mot de passe</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              className="nw-input"
              placeholder="••••••••"
              required
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-nw-gray-700 mb-1">Confirmer le mot de passe</label>
            <input
              type="password"
              name="password_confirm"
              value={form.password_confirm}
              onChange={handleChange}
              className="nw-input"
              placeholder="••••••••"
              required
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="nw-btn-primary w-full flex items-center justify-center"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="animate-spin mr-2">⏳</span> Création...
              </>
            ) : "S'inscrire"}
          </button>
        </form>

        <p className="text-center text-sm text-nw-gray-600 mt-6">
          Déjà inscrit ?{' '}
          <Link to="/login" className="text-nw-green-600 font-medium hover:underline">
            Se connecter
          </Link>
        </p>
      </div>
    </div>
  )
}
