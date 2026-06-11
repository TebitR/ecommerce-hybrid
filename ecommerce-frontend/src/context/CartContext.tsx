import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export interface CartItem {
  id: string
  product_id: string      // MongoDB ID (string)
  postgres_id: number     // Django ID (ENTIER - crucial pour le checkout)
  name: string
  price_ht: string
  price_ttc: string
  quantity: number
}

interface CartContextType {
  cart: CartItem[]
  addToCart: (product: any, qty?: number) => void
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
    return saved ? JSON.parse(saved) : []
  })

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart))
  }, [cart])

  const addToCart = (product: any, qty = 1) => {
    setCart(prev => {
      const existing = prev.find(i => i.product_id === product.id)
      if (existing) {
        return prev.map(i => i.product_id === product.id ? { ...i, quantity: i.quantity + qty } : i)
      }
      // Conversion EXPLICITE en number pour postgres_id
      const pgId = product.postgres_id !== undefined ? Number(product.postgres_id) : 1
      return [...prev, { 
        id: Date.now().toString(), 
        product_id: product.id, 
        postgres_id: pgId,  // ← ENTIER garanti
        name: product.name, 
        price_ht: product.price_ht, 
        price_ttc: product.price_ttc, 
        quantity: qty 
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
  const totalTTC = cart.reduce((s, i) => s + parseFloat(i.price_ttc) * i.quantity, 0)

  return (
    <CartContext.Provider value={{ cart, addToCart, removeFromCart, updateQuantity, clearCart, totalItems, totalTTC }}>
      {children}
    </CartContext.Provider>
  )
}

export const useCart = () => {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}
