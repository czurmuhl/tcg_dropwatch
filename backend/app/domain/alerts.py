from app.models import DropSignal, Product, Watchlist


def get_watchlist_threshold(*, product: Product, watchlist: Watchlist) -> float:
    threshold = product.msrp * (1 + watchlist.msrp_margin_percent / 100)
    if watchlist.max_price is not None:
        return min(threshold, watchlist.max_price)
    return threshold


def signal_matches_watchlist(
    *, product: Product, signal: DropSignal, watchlist: Watchlist
) -> bool:
    if signal.product_id != watchlist.product_id:
        return False
    return signal.observed_price <= get_watchlist_threshold(
        product=product, watchlist=watchlist
    )


def scaffold_email_alert_for_signal(
    *, product: Product, signal: DropSignal, watchlist: Watchlist
) -> bool:
    return watchlist.email_enabled and signal_matches_watchlist(
        product=product, signal=signal, watchlist=watchlist
    )
