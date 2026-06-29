import type { ProductPublic } from "@/client"

export const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
})

export function formatCurrency(value?: number | null) {
  if (value == null) {
    return "n/a"
  }
  return currencyFormatter.format(value)
}

export function formatDate(value?: string | null) {
  if (!value) {
    return "n/a"
  }
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value))
}

export function getProductMap(products: ProductPublic[]) {
  return new Map(products.map((product) => [product.id, product]))
}
