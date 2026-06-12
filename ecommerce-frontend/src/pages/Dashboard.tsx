import { useEffect, useState } from 'react'
import { DJANGO_API } from '../config/api'
import { Link, useNavigate } from 'react-router-dom'
import { Download, Package, User } from 'lucide-react'

interface OrderItemRow {
  name: string
  qty: number
  price: string
}

interface Order {
  id: number
  order_number: string
  status: string
  total_amount: string
  created_at: string
  items: OrderItemRow[]
}

export default function Dashboard() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const token = localStorage.getItem('jwt_token')

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }
    fetch(`${DJANGO_API}/users/orders/`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => {
        if (res.status === 401) {
          navigate('/login')
          return null
        }
        return res.json()
      })
      .then(data => {
        if (data == null) return
        const list = Array.isArray(data) ? data : (data as { results?: Order[] }).results ?? []
        setOrders(list)
      })
      .finally(() => setLoading(false))
  }, [token, navigate])

  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      <div className="flex items-center gap-3 mb-8">
        <User className="w-8 h-8 text-nw-green-600" />
        <h1 className="text-3xl font-bold text-nw-navy">Mon compte</h1>
      </div>

      <div className="nw-card p-6 mb-8">
        <h2 className="text-xl font-semibold text-nw-navy mb-4 flex items-center gap-2">
          <Package className="w-5 h-5" /> Mes commandes
        </h2>
        {loading ? (
          <p className="text-nw-gray-500">Chargement...</p>
        ) : orders.length === 0 ? (
          <p className="text-nw-gray-500">Aucune commande.</p>
        ) : (
          <div className="space-y-4">
            {orders.map(o => (
              <div key={o.id} className="border border-nw-gray-200 rounded-lg p-4 flex justify-between items-center hover:bg-nw-gray-50 transition-colors gap-4 flex-wrap">
                <div className="min-w-0">
                  <p className="font-bold text-nw-navy">{o.order_number}</p>
                  <p className="text-sm text-nw-gray-500">
                    {new Date(o.created_at).toLocaleDateString('fr-FR')} • {o.status}
                  </p>
                  <div className="text-xs text-nw-gray-600 mt-1">
                    {o.items?.map(i => `${i.name} (×${i.qty})`).join(', ')}
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-nw-green-600">{o.total_amount} €</p>
                  <span className="text-xs text-nw-gray-500 flex items-center gap-1 mt-1 justify-end">
                    <Download className="w-3 h-3" /> PDF envoyé par email
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <Link to="/products" className="nw-btn-secondary inline-block">← Retour au catalogue</Link>
    </div>
  )
}
