import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

export default function Checkout() {
  const { cart, totalTTC, clearCart } = useCart()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [orderId, setOrderId] = useState('')

  const [form, setForm] = useState({
    first_name: 'Tebit', last_name: 'User',
    street: '123 Rue Test', city: 'Paris', zip: '75001', country: 'FR', phone: '0600000000',
    same_as_shipping: true,
  })

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const token = localStorage.getItem('jwt_token')
    if (!token) {
      setError('Vous devez être connecté pour commander.')
      setLoading(false)
      navigate('/login', { state: { from: '/checkout' } })
      return
    }

    const userId = localStorage.getItem('user_id') || '1'

    // Schéma FastAPI CheckoutRequest : user_id, items, shipping_address_id, billing_address_id
    const payload = {
      user_id: userId,
      items: cart.map(item => ({
        product_postgres_id: parseInt(String(item.postgres_id), 10),
        quantity: item.quantity,
      })),
      shipping_address_id: null as number | null,
      billing_address_id: null as number | null,
    }

    try {
      const res = await fetch('http://localhost:8001/api/v2/checkout/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || 'Échec de la commande')
      }
      const data = (await res.json()) as { order_number?: string }
      setOrderId(data.order_number ?? '')
      clearCart()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du paiement. Vérifiez votre panier ou connexion.')
    } finally {
      setLoading(false)
    }
  }

  if (orderId) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center bg-nw-gray-50 py-12">
        <div className="nw-card p-8 max-w-md text-center">
          <CheckCircle className="w-16 h-16 text-nw-green-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-nw-navy mb-2">Commande confirmée !</h2>
          <p className="text-nw-gray-600 mb-6">Merci pour votre achat.</p>
          <div className="bg-nw-gray-100 p-4 rounded-lg mb-6">
            <p className="text-sm text-nw-gray-500">Numéro de commande</p>
            <p className="text-xl font-bold text-nw-navy">{orderId}</p>
          </div>
          <Link to="/products" className="nw-btn-primary block w-full">Retour au catalogue</Link>
        </div>
      </div>
    )
  }

  if (cart.length === 0) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold text-nw-navy mb-4">Votre panier est vide</h2>
        <Link to="/products" className="nw-btn-primary">Voir les produits</Link>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-12 max-w-5xl">
      <h1 className="text-3xl font-bold text-nw-navy mb-8">Finaliser la commande</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="nw-card p-6">
              <h3 className="text-lg font-semibold text-nw-navy mb-4">Adresse de livraison</h3>
              <div className="grid grid-cols-2 gap-4">
                <input required placeholder="Prénom" className="nw-input" value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} />
                <input required placeholder="Nom" className="nw-input" value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} />
                <input required placeholder="Adresse" className="nw-input col-span-2" value={form.street} onChange={e => setForm({ ...form, street: e.target.value })} />
                <input required placeholder="Ville" className="nw-input" value={form.city} onChange={e => setForm({ ...form, city: e.target.value })} />
                <input required placeholder="Code postal" className="nw-input" value={form.zip} onChange={e => setForm({ ...form, zip: e.target.value })} />
                <input required placeholder="Téléphone" className="nw-input col-span-2" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} />
              </div>
              <label className="flex items-center gap-2 mt-4 cursor-pointer">
                <input type="checkbox" checked={form.same_as_shipping} onChange={e => setForm({ ...form, same_as_shipping: e.target.checked })} />
                <span className="text-sm text-nw-gray-700">Adresse de facturation identique</span>
              </label>
            </div>

            {error && (
              <div className="bg-red-50 text-red-700 p-4 rounded-lg flex items-center gap-2">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button type="submit" disabled={loading} className="nw-btn-primary w-full flex items-center justify-center gap-2">
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : `Payer ${totalTTC.toFixed(2)} €`}
            </button>
          </form>
        </div>

        <div className="lg:col-span-1">
          <div className="nw-card p-6 sticky top-24">
            <h3 className="text-lg font-semibold text-nw-navy mb-4">Votre panier</h3>
            <div className="space-y-3 mb-4">
              {cart.map(item => (
                <div key={item.product_id} className="flex justify-between text-sm gap-2">
                  <span className="text-nw-gray-700 truncate">{item.name} (×{item.quantity})</span>
                  <span className="font-medium shrink-0">{(parseFloat(item.price_ttc) * item.quantity).toFixed(2)} €</span>
                </div>
              ))}
            </div>
            <div className="border-t border-nw-gray-200 pt-4 flex justify-between font-bold text-lg">
              <span>Total</span>
              <span className="text-nw-green-600">{totalTTC.toFixed(2)} €</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
