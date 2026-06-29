import pytest

from app.domain.alerts import (
    get_watchlist_threshold,
    scaffold_email_alert_for_signal,
    signal_matches_watchlist,
)
from app.models import DropSignal, Product, Watchlist


def test_signal_matches_watchlist_with_margin() -> None:
    product = Product(
        game="Pokemon", name="Booster Box", product_type="Booster", msrp=100
    )
    watchlist = Watchlist(product_id=product.id, owner_id=product.id)
    signal = DropSignal(
        product_id=product.id,
        observed_price=109.99,
        stock_status="in_stock",
    )

    assert get_watchlist_threshold(
        product=product, watchlist=watchlist
    ) == pytest.approx(110)
    assert signal_matches_watchlist(product=product, signal=signal, watchlist=watchlist)


def test_signal_uses_max_price_as_threshold_cap() -> None:
    product = Product(game="Lorcana", name="Troves", product_type="Bundle", msrp=50)
    watchlist = Watchlist(
        product_id=product.id,
        owner_id=product.id,
        msrp_margin_percent=20,
        max_price=55,
    )
    signal = DropSignal(
        product_id=product.id,
        observed_price=56,
        stock_status="in_stock",
    )

    assert get_watchlist_threshold(product=product, watchlist=watchlist) == 55
    assert not signal_matches_watchlist(
        product=product, signal=signal, watchlist=watchlist
    )


def test_scaffold_email_alert_requires_enabled_matching_watchlist() -> None:
    product = Product(game="Pokemon", name="ETB", product_type="Box", msrp=60)
    watchlist = Watchlist(
        product_id=product.id,
        owner_id=product.id,
        email_enabled=False,
    )
    signal = DropSignal(
        product_id=product.id,
        observed_price=60,
        stock_status="in_stock",
    )

    assert not scaffold_email_alert_for_signal(
        product=product, signal=signal, watchlist=watchlist
    )
