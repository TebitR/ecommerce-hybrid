import { useEffect, useState } from 'react'
import { API_BASE } from '../config/api'
import { useParams, Link } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import { Star, CheckCircle, Truck, Shield } from 'lucide-react'

interface Product {
  id: string
  postgres_id: string
  name: string
  slug: string
  price_ht: string | number
  price_ttc: string | number
  stock_available: number
  description?: string
  category?: { name: string }
  rating?: { average: number; count: number }
  attributes?: Record<string, unknown>
}

export default function ProductDetail() {
  const { slug } = useParams()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const { addToCart } = useCart()

  useEffect(() => {
    if (!slug) return
    let cancelled = false
    fetch(`${API_BASE}/products/${encodeURIComponent(slug)}`)
      .then(res => {
        if (!res.ok) throw new Error('not found')
        return res.json()
      })
      .then(data => {
        if (cancelled) return
        const p = data.product as Product
        setProduct(p)
      })
      .catch(() => {
        if (!cancelled) setProduct(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [slug])

  if (loading) return <div className="container mx-auto px-4 py-12 text-center">Chargement...</div>
  if (!product) return <div className="container mx-auto px-4 py-12 text-center">Produit introuvable</div>

  const desc =
    product.description ||
    (typeof product.attributes?.description === 'string' ? product.attributes.description : null) ||
    'Ce produit de haute qualité répond à tous vos besoins. Performance, durabilité et design moderne sont au rendez-vous.'

  const priceTtc = String(product.price_ttc)
  const avg = product.rating?.average ?? 0

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-16">
        <div className="nw-card aspect-square bg-nw-gray-50 flex items-center justify-center text-9xl">
          📦
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            {product.category?.name && <span className="nw-badge">{product.category.name}</span>}
            {product.stock_available <= 5 && product.stock_available > 0 && (
              <span className="text-xs text-red-600 bg-red-50 px-2 py-0.5 rounded-full">Stock limité</span>
            )}
          </div>

          <h1 className="text-3xl font-bold text-nw-navy mb-4">{product.name}</h1>

          <div className="flex items-center gap-2 mb-6">
            <div className="flex text-nw-green-600">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className={`w-5 h-5 ${i < Math.round(avg) ? 'fill-current' : 'text-nw-gray-200 fill-nw-gray-200'}`} />
              ))}
            </div>
            <span className="text-sm text-nw-gray-500">({product.rating?.count ?? 0} avis)</span>
          </div>

          <div className="text-4xl font-bold text-nw-green-600 mb-2">{priceTtc} €</div>
          <p className="text-nw-gray-500 mb-6">TVA incluse • Livraison gratuite</p>

          <p className="text-nw-gray-700 leading-relaxed mb-8">{desc}</p>

          <div className="flex gap-4 mb-8">
            <button
              type="button"
              disabled={product.stock_available === 0}
              onClick={() => addToCart(product as unknown as Record<string, unknown>, 1)}
              className="nw-btn-primary flex-1 disabled:opacity-50"
            >
              {product.stock_available > 0 ? 'Ajouter au panier' : 'Indisponible'}
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm text-nw-gray-600">
            <div className="flex items-center gap-2"><Truck className="w-4 h-4 text-nw-green-600 shrink-0" /> Livraison sous 24h</div>
            <div className="flex items-center gap-2"><Shield className="w-4 h-4 text-nw-green-600 shrink-0" /> Garantie 2 ans</div>
            <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-nw-green-600 shrink-0" /> Satisfait ou remboursé</div>
            <div className="flex items-center gap-2"><Star className="w-4 h-4 text-nw-green-600 shrink-0" /> Top qualité</div>
          </div>
        </div>
      </div>

      <div className="text-center">
        <Link to="/products" className="text-nw-navy hover:text-nw-green-600 font-medium">← Retour au catalogue</Link>
      </div>
    </div>
  )
}
