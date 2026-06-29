import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Bell, Boxes, Radio, TrendingDown } from "lucide-react"
import { Suspense } from "react"

import { ProductsService, SignalsService, WatchlistsService } from "@/client"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { formatCurrency, formatDate, getProductMap } from "@/utils/tcg"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - TCG DropWatch",
      },
    ],
  }),
})

function getDashboardQueryOptions() {
  return {
    queryFn: async () => {
      const [products, signals, watchlists] = await Promise.all([
        ProductsService.readProducts({ skip: 0, limit: 100 }),
        SignalsService.readSignals({ skip: 0, limit: 10 }),
        WatchlistsService.readWatchlists({ skip: 0, limit: 100 }),
      ])

      return { products, signals, watchlists }
    },
    queryKey: ["dashboard"],
  }
}

function DashboardContent() {
  const { data } = useSuspenseQuery(getDashboardQueryOptions())
  const productMap = getProductMap(data.products.data)
  const latestSignal = data.signals.data[0]
  const latestProduct = latestSignal
    ? productMap.get(latestSignal.product_id)
    : undefined

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">TCG DropWatch</h1>
        <p className="text-muted-foreground">
          Track near-MSRP drops across Pokemon, Lorcana, and other TCG products.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="rounded-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-medium">Products</CardTitle>
            <Boxes className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.products.count}</div>
            <p className="text-xs text-muted-foreground">catalog entries</p>
          </CardContent>
        </Card>
        <Card className="rounded-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-medium">Signals</CardTitle>
            <Radio className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.signals.count}</div>
            <p className="text-xs text-muted-foreground">drop observations</p>
          </CardContent>
        </Card>
        <Card className="rounded-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-medium">Watchlist</CardTitle>
            <Bell className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.watchlists.count}</div>
            <p className="text-xs text-muted-foreground">email alert rules</p>
          </CardContent>
        </Card>
        <Card className="rounded-lg">
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-medium">Latest Price</CardTitle>
            <TrendingDown className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(latestSignal?.observed_price)}
            </div>
            <p className="text-xs text-muted-foreground">
              {latestProduct?.name ?? "no signals yet"}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>Recent Signals</CardTitle>
        </CardHeader>
        <CardContent>
          {data.signals.data.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No drop signals have been recorded yet.
            </p>
          ) : (
            <div className="flex flex-col gap-3">
              {data.signals.data.slice(0, 5).map((signal) => {
                const product = productMap.get(signal.product_id)
                return (
                  <div
                    key={signal.id}
                    className="flex flex-col gap-2 rounded-md border p-3 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-medium">
                          {product?.name ?? "Unknown product"}
                        </p>
                        {product ? (
                          <Badge variant="secondary">{product.game}</Badge>
                        ) : null}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {signal.stock_status} · {formatDate(signal.observed_at)}
                      </p>
                    </div>
                    <div className="text-lg font-semibold">
                      {formatCurrency(signal.observed_price)}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function Dashboard() {
  return (
    <Suspense
      fallback={
        <div className="text-sm text-muted-foreground">Loading dashboard...</div>
      }
    >
      <DashboardContent />
    </Suspense>
  )
}
