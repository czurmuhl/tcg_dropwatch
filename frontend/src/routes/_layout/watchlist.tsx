import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Bell } from "lucide-react"
import { Suspense } from "react"

import { ProductsService, WatchlistsService } from "@/client"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { formatCurrency, getProductMap } from "@/utils/tcg"

export const Route = createFileRoute("/_layout/watchlist")({
  component: Watchlist,
  head: () => ({
    meta: [
      {
        title: "Watchlist - TCG DropWatch",
      },
    ],
  }),
})

function getWatchlistQueryOptions() {
  return {
    queryFn: async () => {
      const [products, watchlists] = await Promise.all([
        ProductsService.readProducts({ skip: 0, limit: 100 }),
        WatchlistsService.readWatchlists({ skip: 0, limit: 100 }),
      ])

      return { products, watchlists }
    },
    queryKey: ["watchlist"],
  }
}

function getThreshold(msrp?: number, margin = 10, maxPrice?: number | null) {
  if (msrp == null) {
    return null
  }
  const marginPrice = msrp * (1 + margin / 100)
  return maxPrice == null ? marginPrice : Math.min(marginPrice, maxPrice)
}

function WatchlistContent() {
  const { data } = useSuspenseQuery(getWatchlistQueryOptions())
  const productMap = getProductMap(data.products.data)

  if (data.watchlists.data.length === 0) {
    return (
      <Card className="rounded-lg">
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <div className="mb-4 rounded-full bg-muted p-4">
            <Bell className="size-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold">No watchlist rules yet</h3>
          <p className="text-muted-foreground">
            Product alert preferences will appear here after they are created.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Product</TableHead>
          <TableHead>Game</TableHead>
          <TableHead>MSRP</TableHead>
          <TableHead>Margin</TableHead>
          <TableHead>Max Price</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Alert At</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.watchlists.data.map((watchlist) => {
          const product = productMap.get(watchlist.product_id)
          const threshold = getThreshold(
            product?.msrp,
            watchlist.msrp_margin_percent,
            watchlist.max_price,
          )
          return (
            <TableRow key={watchlist.id}>
              <TableCell className="font-medium">
                {product?.name ?? "Unknown product"}
              </TableCell>
              <TableCell>
                {product ? <Badge variant="secondary">{product.game}</Badge> : "n/a"}
              </TableCell>
              <TableCell>{formatCurrency(product?.msrp)}</TableCell>
              <TableCell>{watchlist.msrp_margin_percent ?? 10}%</TableCell>
              <TableCell>{formatCurrency(watchlist.max_price)}</TableCell>
              <TableCell>
                <Badge variant={watchlist.email_enabled ? "default" : "outline"}>
                  {watchlist.email_enabled ? "on" : "off"}
                </Badge>
              </TableCell>
              <TableCell>{formatCurrency(threshold)}</TableCell>
            </TableRow>
          )
        })}
      </TableBody>
    </Table>
  )
}

function Watchlist() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Watchlist</h1>
        <p className="text-muted-foreground">
          Review near-MSRP email alert rules for your tracked products.
        </p>
      </div>
      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>Alert Rules</CardTitle>
        </CardHeader>
        <CardContent>
          <Suspense
            fallback={
              <div className="text-sm text-muted-foreground">
                Loading watchlist...
              </div>
            }
          >
            <WatchlistContent />
          </Suspense>
        </CardContent>
      </Card>
    </div>
  )
}
