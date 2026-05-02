import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'

export interface CartItem {
  id: string
  product_id: string // MongoDB ID
  postgres_id: string // Django ID (checkout)
  name: string
  price_ht: string
  price_ttc: string
  quantity: number
}

interface CartContextType {
  cart: CartItem[]
  addToCart: (product: Record<string, unknown>, qty?: number) => void
  removeFromCart: (productId: string) => void
  updateQuantity: (productId: string, qty: number) => void
  clearCart: () => void
  totalItems: number
  totalTTC: number
}

const CartContext = createContext<CartContextType | undefined>(undefined)

export function CartProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<CartItem[]>(() => {
    const saved = localStorage.getItem('cart')
    if (!saved) return []
    try {
      const parsed: unknown = JSON.parse(saved)
      if (!Array.isArray(parsed)) return []
      return parsed.map((row: Record<string, unknown>) => ({
        ...row,
        postgres_id: String(row.postgres_id ?? row.product_id ?? ''),
      })) as CartItem[]
    } catch {
      return []
    }
  })

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart))
  }, [cart])

  const addToCart = (product: Record<string, unknown>, qty = 1) => {
    const pid = String(product.id ?? '')
    const pgId = product.postgres_id != null ? String(product.postgres_id) : '1'
    setCart(prev => {
      const existing = prev.find(i => i.product_id === pid)
      if (existing) {
        return prev.map(i => i.product_id === pid ? { ...i, quantity: i.quantity + qty } : i)
      }
      return [...prev, {
        id: Date.now().toString(),
        product_id: pid,
        postgres_id: pgId,
        name: String(product.name ?? ''),
        price_ht: String(product.price_ht ?? ''),
        price_ttc: String(product.price_ttc ?? ''),
        quantity: qty,
      }]
    })
  }

  const removeFromCart = (productId: string) => setCart(prev => prev.filter(i => i.product_id !== productId))
  const updateQuantity = (productId: string, qty: number) => {
    if (qty <= 0) return removeFromCart(productId)
    setCart(prev => prev.map(i => i.product_id === productId ? { ...i, quantity: qty } : i))
  }
  const clearCart = () => setCart([])

  const totalItems = cart.reduce((s, i) => s + i.quantity, 0)
  const totalTTC = cart.reduce((s, i) => s + (parseFloat(i.price_ttc) || 0) * i.quantity, 0)

  return (
    <CartContext.Provider value={{ cart, addToCart, removeFromCart, updateQuantity, clearCart, totalItems, totalTTC }}>
      {children}
    </CartContext.Provider>
  )
}

export const useCart = () => {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart doit être utilisé dans <CartProvider>')
  return ctx
}
