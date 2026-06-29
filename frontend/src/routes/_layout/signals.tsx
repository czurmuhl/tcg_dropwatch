import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { ExternalLink, Radio } from "lucide-react"
import { Suspense } from "react"

import { ProductsService, SignalsService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
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
import { formatCurrency, formatDate, getProductMap } from "@/utils/tcg"

export const Route = createFileRoute("/_layout/signals")({
  component: Signals,
  head: () => ({
    meta: [
      {
        title: "Signals - TCG DropWatch",
      },
    ],
  }),
})

function getSignalsQueryOptions() {
  return {
    queryFn: async () => {
      const [products, signals] = await Promise.all([
        ProductsService.readProducts({ skip: 0, limit: 100 }),
        SignalsService.readSignals({ skip: 0, limit: 100 }),
      ])

      return { products, signals }
    },
    queryKey: ["signals"],
  }
}

function SignalsContent() {
  const { data } = useSuspenseQuery(getSignalsQueryOptions())
  const productMap = getProductMap(data.products.data)

  if (data.signals.data.length === 0) {
    return (
      <Card className="rounded-lg">
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <div className="mb-4 rounded-full bg-muted p-4">
            <Radio className="size-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold">No signals yet</h3>
          <p className="text-muted-foreground">
            Manual drops and scraper observations will appear here.
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
          <TableHead>Price</TableHead>
          <TableHead>MSRP</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Observed</TableHead>
          <TableHead className="text-right">Source</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.signals.data.map((signal) => {
          const product = productMap.get(signal.product_id)
          return (
            <TableRow key={signal.id}>
              <TableCell className="font-medium">
                {product?.name ?? "Unknown product"}
              </TableCell>
              <TableCell>
                {product ? <Badge variant="secondary">{product.game}</Badge> : "n/a"}
              </TableCell>
              <TableCell>{formatCurrency(signal.observed_price)}</TableCell>
              <TableCell>{formatCurrency(product?.msrp)}</TableCell>
              <TableCell>{signal.stock_status}</TableCell>
              <TableCell>{formatDate(signal.observed_at)}</TableCell>
              <TableCell className="text-right">
                {signal.url ? (
                  <Button variant="ghost" size="icon-sm" asChild>
                    <a href={signal.url} target="_blank" rel="noreferrer">
                      <ExternalLink />
                      <span className="sr-only">Open source</span>
                    </a>
                  </Button>
                ) : (
                  <span className="text-muted-foreground">manual</span>
                )}
              </TableCell>
            </TableRow>
          )
        })}
      </TableBody>
    </Table>
  )
}

function Signals() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Signals</h1>
        <p className="text-muted-foreground">
          Recent TCG drop observations from manual entries and future scrapers.
        </p>
      </div>
      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>Drop Board</CardTitle>
        </CardHeader>
        <CardContent>
          <Suspense
            fallback={
              <div className="text-sm text-muted-foreground">
                Loading signals...
              </div>
            }
          >
            <SignalsContent />
          </Suspense>
        </CardContent>
      </Card>
    </div>
  )
}
