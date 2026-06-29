import { useMutation, useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { Play, Store } from "lucide-react"
import { Suspense } from "react"

import {
  ProductsService,
  ScrapesService,
  SourcesService,
  UsersService,
} from "@/client"
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
import useCustomToast from "@/hooks/useCustomToast"
import { formatDate, getProductMap } from "@/utils/tcg"

export const Route = createFileRoute("/_layout/sources")({
  component: Sources,
  beforeLoad: async () => {
    const user = await UsersService.readUserMe()
    if (!user.is_superuser) {
      throw redirect({
        to: "/",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Sources - TCG DropWatch",
      },
    ],
  }),
})

function getSourcesQueryOptions() {
  return {
    queryFn: async () => {
      const [products, sources] = await Promise.all([
        ProductsService.readProducts({ skip: 0, limit: 100 }),
        SourcesService.readSources({ skip: 0, limit: 100 }),
      ])

      return { products, sources }
    },
    queryKey: ["sources"],
  }
}

function SourcesContent() {
  const { data } = useSuspenseQuery(getSourcesQueryOptions())
  const productMap = getProductMap(data.products.data)
  const { showSuccessToast } = useCustomToast()
  const runScrape = useMutation({
    mutationFn: () => ScrapesService.runScrape({ requestBody: {} }),
    onSuccess: (response) => {
      showSuccessToast(response.message)
    },
  })

  if (data.sources.data.length === 0) {
    return (
      <Card className="rounded-lg">
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <div className="mb-4 rounded-full bg-muted p-4">
            <Store className="size-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold">No retailer sources yet</h3>
          <p className="text-muted-foreground">
            Source configuration will appear here after products are seeded.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-end">
        <Button onClick={() => runScrape.mutate()} disabled={runScrape.isPending}>
          <Play />
          {runScrape.isPending ? "Running" : "Run scrape"}
        </Button>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Retailer</TableHead>
            <TableHead>Product</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>URL</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.sources.data.map((source) => {
            const product = productMap.get(source.product_id)
            return (
              <TableRow key={source.id}>
                <TableCell className="font-medium">
                  {source.retailer_name}
                </TableCell>
                <TableCell>{product?.name ?? "Unknown product"}</TableCell>
                <TableCell>
                  <Badge variant={source.is_active ? "default" : "outline"}>
                    {source.is_active ? "active" : "paused"}
                  </Badge>
                </TableCell>
                <TableCell>{formatDate(source.created_at)}</TableCell>
                <TableCell className="max-w-sm truncate">
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-primary hover:underline"
                  >
                    {source.url}
                  </a>
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </div>
  )
}

function Sources() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Sources</h1>
        <p className="text-muted-foreground">
          Admin source configuration for retailer product pages and scrape runs.
        </p>
      </div>
      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>Retailer Sources</CardTitle>
        </CardHeader>
        <CardContent>
          <Suspense
            fallback={
              <div className="text-sm text-muted-foreground">
                Loading sources...
              </div>
            }
          >
            <SourcesContent />
          </Suspense>
        </CardContent>
      </Card>
    </div>
  )
}
