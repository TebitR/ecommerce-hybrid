import { useState, useEffect, type FormEvent } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { ShoppingCart, User, Search, Shield, Truck, RefreshCw, Headphones, Star, MessageCircle } from 'lucide-react'
import { CartProvider, useCart } from './context/CartContext'
import Checkout from './pages/Checkout'
import ProductDetail from './pages/ProductDetail'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import ForgotPassword from './pages/ForgotPassword'
import ResetPasswordConfirm from './pages/ResetPasswordConfirm'

interface Product {
  id: string
  name: string
  postgres_id?: string
  slug?: string
  price_ht: string | number
  price_ttc: string | number
  stock_available: number
  category?: { name: string }
  rating?: { average: number; count: number }
}

const API_BASE = 'http://localhost:8001/api/v2'
const AUTH_BASE = 'http://localhost:8000/api/v1/auth'

function setUserIdFromAccessToken(access: string) {
  try {
    const part = access.split('.')[1]
    if (!part) return
    const payload = JSON.parse(atob(part)) as { user_id?: number }
    if (payload.user_id != null) localStorage.setItem('user_id', String(payload.user_id))
  } catch {
    /* ignore */
  }
}

async function fetchAPI<T>(endpoint: string, token?: string): Promise<T> {
  const headers: HeadersInit = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${API_BASE}${endpoint}`, { headers })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

async function login(username: string, password: string) {
  const res = await fetch(`${AUTH_BASE}/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) throw new Error('Identifiants incorrects')
  const data = (await res.json()) as { access: string; user_id?: string }
  localStorage.setItem('jwt_token', data.access)
  setUserIdFromAccessToken(data.access)
  if (data.user_id != null) localStorage.setItem('user_id', String(data.user_id))
  return data
}

function logout() {
  localStorage.removeItem('jwt_token')
  localStorage.removeItem('user_id')
}

function Header({ isAuthenticated, onLogout }: { isAuthenticated: boolean; onLogout: () => void }) {
  const { totalItems } = useCart()
  return (
    <header className="nw-header">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-nw-green-600 rounded flex items-center justify-center"><span className="text-white font-bold text-lg">E</span></div>
          <span className="text-xl font-bold text-nw-navy">E-Shop</span>
        </Link>
        <nav className="hidden md:flex items-center gap-6">
          <Link to="/products" className="text-sm font-medium text-nw-gray-700 hover:text-nw-navy">Catalogue</Link>
          {/* Route /compare désactivée temporairement */}
        </nav>
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <Link to="/cart" className="p-2 hover:bg-nw-gray-100 rounded-full transition-colors relative">
                <ShoppingCart className="w-5 h-5 text-nw-gray-700" />
                {totalItems > 0 && <span className="absolute -top-1 -right-1 bg-nw-green-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center animate-bounce-short">{totalItems}</span>}
              </Link>
              <Link to="/dashboard" className="p-2 hover:bg-nw-gray-100 rounded-full transition-colors" aria-label="Mon compte"><User className="w-5 h-5 text-nw-gray-700" /></Link>
              <button type="button" onClick={onLogout} className="nw-btn-secondary text-sm py-2 px-4">Déconnexion</button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm font-medium text-nw-navy hover:text-nw-green-600">Connexion</Link>
              <Link to="/register" className="nw-btn-primary text-sm py-2 px-4">S&apos;inscrire</Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}

function TrustBar() {
  const items = [{ icon: Shield, text: 'Paiement sécurisé' }, { icon: Truck, text: 'Livraison gratuite' }, { icon: RefreshCw, text: 'Retours gratuits' }, { icon: Headphones, text: 'Support 24/7' }]
  return (
    <div className="bg-nw-gray-50 border-b border-nw-gray-200">
      <div className="container mx-auto px-4 py-3">
        <div className="flex flex-wrap justify-center gap-6 md:gap-10">
          {items.map(({ icon: Icon, text }) => (
            <div key={text} className="flex items-center gap-2 text-sm text-nw-gray-700"><Icon className="w-4 h-4 text-nw-green-600" /><span className="font-medium">{text}</span></div>
          ))}
        </div>
      </div>
    </div>
  )
}

function ProductCard({ product }: { product: Product }) {
  const { addToCart } = useCart()
  const avgRating = product.rating?.average || 0
  const ratingCount = product.rating?.count || 0
  const slugPath = product.slug || product.id
  return (
    <div className="nw-card overflow-hidden group">
      <div className="p-5">
        <div className="flex justify-between items-start mb-3 gap-2">
          <Link to={`/product/${encodeURIComponent(slugPath)}`} className="font-semibold text-nw-gray-900 line-clamp-2 group-hover:text-nw-navy transition-colors cursor-pointer text-left">{product.name}</Link>
          {product.category && <span className="nw-badge shrink-0">{product.category.name}</span>}
        </div>
        <div className="aspect-square bg-nw-gray-50 rounded-lg flex items-center justify-center mb-4 text-4xl opacity-50">📦</div>
        {ratingCount > 0 && (
          <div className="flex items-center gap-1 mb-2">
            <div className="flex">{[...Array(5)].map((_, i) => <Star key={i} className={`w-4 h-4 ${i < Math.round(avgRating) ? 'fill-nw-green-600 text-nw-green-600' : 'fill-nw-gray-200 text-nw-gray-200'}`} />)}</div>
            <span className="text-xs text-nw-gray-500">({ratingCount})</span>
          </div>
        )}
        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-2xl font-bold text-nw-green-600">{String(product.price_ttc)} €</span>
          <span className="text-sm text-nw-gray-500 line-through">{String(product.price_ht)} €</span>
        </div>
        <p className="text-xs text-nw-gray-500 mb-3">TVA incluse • Livraison gratuite</p>
        {product.stock_available <= 3 && product.stock_available > 0 && <div className="flex items-center gap-1 mb-3 text-xs text-red-600 font-medium"><span className="w-2 h-2 bg-red-600 rounded-full animate-pulse" />Plus que {product.stock_available} en stock</div>}
        <button type="button" className="nw-btn-primary w-full" disabled={product.stock_available === 0} onClick={() => addToCart(product as unknown as Record<string, unknown>, 1)}>{product.stock_available > 0 ? 'Ajouter au panier' : 'Indisponible'}</button>
      </div>
    </div>
  )
}

function Home() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const endpoint = searchQuery ? `/search?q=${encodeURIComponent(searchQuery)}&per_page=9` : '/search?per_page=9'
    fetchAPI<{ results: Product[] }>(endpoint).then(data => setProducts(data.results)).catch(console.error).finally(() => setLoading(false))
  }, [searchQuery])

  const categories = ['Informatique', 'Maison', 'Sport']

  return (
    <div>
      <section className="nw-hero">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl">
            <h1 className="text-4xl md:text-5xl font-bold text-nw-navy mb-4 leading-tight">Trouvez les meilleurs produits, comparés objectivement</h1>
            <p className="text-lg text-nw-gray-700 mb-6">Des avis experts, des prix transparents, et une expérience d&apos;achat simplifiée.</p>
            <div className="relative max-w-lg">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-nw-gray-400" />
              <input type="search" value={searchQuery} onChange={e => setSearchQuery(e.target.value)} placeholder="Rechercher un produit..." className="nw-input pl-12 shadow-lg" />
            </div>
            <div className="flex flex-wrap gap-2 mt-4">
              {categories.map(cat => (
                <button key={cat} type="button" onClick={() => setSearchQuery(cat)} className="nw-badge hover:bg-nw-green-100 cursor-pointer transition-colors">{cat}</button>
              ))}
            </div>
          </div>
        </div>
      </section>
      <TrustBar />
      <div className="container mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold text-nw-navy">{searchQuery ? `Résultats pour "${searchQuery}"` : 'Produits recommandés'}</h2>
          <span className="text-sm text-nw-gray-500">{products.length} produits</span>
        </div>
        {loading ? <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{[...Array(6)].map((_, i) => <div key={i} className="nw-card p-5 animate-pulse"><div className="h-48 bg-nw-gray-100 rounded-lg mb-4" /></div>)}</div> : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{products.map(p => <ProductCard key={p.id} product={p} />)}</div>
        )}
      </div>
    </div>
  )
}

function Login() {
  const [username, setUsername] = useState('tebit')
  const [password, setPassword] = useState('adminadmin')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      window.location.href = '/'
    } catch {
      setError('Identifiants incorrects')
    } finally {
      setLoading(false)
    }
  }
  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-nw-gray-50 py-12 px-4">
      <div className="nw-card p-6 md:p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-nw-navy text-center mb-6">Connexion</h1>
        {error && <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm mb-4">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input value={username} onChange={e => setUsername(e.target.value)} className="nw-input" placeholder="Nom d'utilisateur" required />
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="nw-input" placeholder="Mot de passe" required />
          <button type="submit" className="nw-btn-primary w-full" disabled={loading}>{loading ? 'Connexion...' : 'Se connecter'}</button>
        </form>
        <p className="text-center text-xs text-nw-gray-500 mt-2"><Link to="/reset-password" className="hover:underline text-nw-green-600">Mot de passe oublié ?</Link></p>
        <p className="text-center text-sm text-nw-gray-600 mt-4">Pas de compte ? <Link to="/register" className="text-nw-green-600 font-medium">S&apos;inscrire</Link></p>
      </div>
    </div>
  )
}

function Cart() {
  const { cart, removeFromCart, updateQuantity, totalTTC } = useCart()
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])
  if (!mounted) return <div className="container mx-auto px-4 py-12 text-center">Chargement...</div>
  if (cart.length === 0) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <ShoppingCart className="w-16 h-16 text-nw-gray-300 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-nw-gray-900 mb-2">Votre panier est vide</h2>
        <Link to="/products" className="nw-btn-primary">Continuer les achats</Link>
      </div>
    )
  }
  return (
    <div className="container mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-nw-navy mb-8">Votre panier</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-4">
          {cart.map(item => (
            <div key={item.product_id} className="nw-card p-4 flex items-center gap-4">
              <div className="w-20 h-20 bg-nw-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">📦</div>
              <div className="flex-1 min-w-0"><h3 className="font-semibold text-nw-gray-900 mb-1">{item.name}</h3><p className="text-nw-green-600 font-bold">{item.price_ttc} €</p></div>
              <div className="flex items-center gap-2">
                <button type="button" onClick={() => updateQuantity(item.product_id, item.quantity - 1)} className="p-1 hover:bg-nw-gray-100 rounded">−</button>
                <span className="w-8 text-center font-medium">{item.quantity}</span>
                <button type="button" onClick={() => updateQuantity(item.product_id, item.quantity + 1)} className="p-1 hover:bg-nw-gray-100 rounded">+</button>
              </div>
              <button type="button" onClick={() => removeFromCart(item.product_id)} className="p-2 text-red-600 hover:bg-red-50 rounded" aria-label="Supprimer">🗑️</button>
            </div>
          ))}
        </div>
        <div className="lg:col-span-1">
          <div className="nw-card p-6 sticky top-24">
            <h2 className="text-xl font-bold text-nw-navy mb-4">Récapitulatif</h2>
            <div className="border-t border-nw-gray-200 pt-3 flex justify-between text-lg font-bold text-nw-navy"><span>Total TTC</span><span className="text-nw-green-600">{totalTTC.toFixed(2)} €</span></div>
            <Link to="/checkout" className="nw-btn-primary w-full block text-center mt-4">Passer la commande</Link>
            <Link to="/products" className="block text-center mt-3 text-sm text-nw-gray-600 hover:text-nw-navy">Continuer les achats</Link>
          </div>
        </div>
      </div>
    </div>
  )
}

function Footer() {
  const links = [
    { title: 'Cartes', items: ['Meilleures cartes', 'Cashback', 'Voyage'] },
    { title: 'Banque', items: ['Comptes courants', 'Épargne', 'Livrets'] },
    { title: 'Assurance', items: ['Auto', 'Habitation', 'Santé'] },
    { title: 'Prêts', items: ['Immobilier', 'Travaux', 'Conso'] },
  ]
  return (
    <footer className="bg-nw-gray-50 border-t border-nw-gray-200 pt-12 pb-6">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
          {links.map(col => (
            <div key={col.title}>
              <h4 className="font-bold text-nw-navy mb-4">{col.title}</h4>
              <ul className="space-y-2">
                {col.items.map(item => <li key={item}><Link to="#" className="text-sm text-nw-gray-600 hover:text-nw-green-600">{item}</Link></li>)}
              </ul>
            </div>
          ))}
        </div>
        <div className="border-t border-nw-gray-200 pt-6 text-center text-sm text-nw-gray-500">© 2026 E-Shop PRO • Inspiré par NerdWallet</div>
      </div>
    </footer>
  )
}

function ChatBubble() {
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div className="bg-white p-3 rounded-lg shadow-lg mb-2 text-xs text-nw-gray-700 max-w-[200px] animate-fade-in-up hidden md:block">
        👋 Hi, I&apos;m <span className="font-bold text-nw-green-600">NerdAI</span>. Ask me anything!
      </div>
      <button type="button" className="w-14 h-14 bg-nw-green-600 rounded-full flex items-center justify-center shadow-lg hover:bg-nw-green-700 transition-colors" aria-label="Chat">
        <MessageCircle className="w-6 h-6 text-white" />
      </button>
    </div>
  )
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('jwt_token'))

  return (
    <CartProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-white font-sans">
          <Header isAuthenticated={isAuthenticated} onLogout={() => { logout(); setIsAuthenticated(false) }} />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/products" element={<Home />} />
              <Route path="/product/:slug" element={<ProductDetail />} />
              <Route path="/cart" element={<Cart />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/reset-password/:uid/:token" element={<ResetPasswordConfirm />} />
              <Route path="/reset-password" element={<ForgotPassword />} />
            </Routes>
          </main>
          <Footer />
          <ChatBubble />
        </div>
      </BrowserRouter>
    </CartProvider>
  )
}
