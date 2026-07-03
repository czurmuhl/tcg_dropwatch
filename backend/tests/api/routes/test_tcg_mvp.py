import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models import AlertEvent, DropSignal, Product, Watchlist
from tests.utils.user import create_random_user


def create_product(client: TestClient, headers: dict[str, str]) -> dict[str, str]:
    response = client.post(
        f"{settings.API_V1_STR}/products/",
        headers=headers,
        json={
            "game": "Pokemon",
            "name": f"Booster Box {uuid.uuid4()}",
            "product_type": "Booster Box",
            "msrp": 161.64,
            "image_url": None,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_product_crud_permissions(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers: dict[str, str],
) -> None:
    product = create_product(client, superuser_token_headers)

    response = client.get(
        f"{settings.API_V1_STR}/products/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["count"] >= 1

    response = client.get(
        f"{settings.API_V1_STR}/products/",
        headers=normal_user_token_headers,
        params={"q": "Booster"},
    )
    assert response.status_code == 200
    assert any(item["id"] == product["id"] for item in response.json()["data"])

    response = client.post(
        f"{settings.API_V1_STR}/products/",
        headers=normal_user_token_headers,
        json={
            "game": "Lorcana",
            "name": "Illumineer's Trove",
            "product_type": "Bundle",
            "msrp": 49.99,
        },
    )
    assert response.status_code == 403

    response = client.put(
        f"{settings.API_V1_STR}/products/{product['id']}",
        headers=superuser_token_headers,
        json={"msrp": 155.99},
    )
    assert response.status_code == 200
    assert response.json()["msrp"] == 155.99

    response = client.delete(
        f"{settings.API_V1_STR}/products/{product['id']}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"


def test_source_crud_allows_user_owned_scrape_and_social_sources(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers: dict[str, str],
) -> None:
    product = create_product(client, superuser_token_headers)

    response = client.get(
        f"{settings.API_V1_STR}/sources/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200

    response = client.post(
        f"{settings.API_V1_STR}/sources/",
        headers=normal_user_token_headers,
        json={
            "product_id": product["id"],
            "retailer_name": "Demo Retailer",
            "label": "Primary preorder page",
            "source_kind": "retailer_site",
            "url": "https://example.com/product",
            "price_selector": ".price",
            "stock_selector": ".stock",
            "is_active": True,
        },
    )
    assert response.status_code == 200
    source = response.json()
    assert source["retailer_name"] == "Demo Retailer"
    assert source["label"] == "Primary preorder page"
    assert source["owner_id"] is not None

    response = client.put(
        f"{settings.API_V1_STR}/sources/{source['id']}",
        headers=normal_user_token_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    response = client.post(
        f"{settings.API_V1_STR}/sources/",
        headers=normal_user_token_headers,
        json={
            "retailer_name": "Pokemon Deals Feed",
            "label": "Restock posts",
            "source_kind": "social_feed",
            "url": "https://social.example/pokemon-deals",
            "platform": "x",
            "account_name": "@pokemon_deals",
            "is_active": True,
        },
    )
    assert response.status_code == 200
    social_source = response.json()
    assert social_source["product_id"] is None
    assert social_source["source_kind"] == "social_feed"
    assert social_source["account_name"] == "@pokemon_deals"

    response = client.get(
        f"{settings.API_V1_STR}/sources/{social_source['id']}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200


def test_signal_listing_and_manual_creation_permissions(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers: dict[str, str],
) -> None:
    product = create_product(client, superuser_token_headers)

    response = client.post(
        f"{settings.API_V1_STR}/signals/",
        headers=normal_user_token_headers,
        json={
            "product_id": product["id"],
            "observed_price": 150,
            "stock_status": "in_stock",
            "source_type": "manual",
        },
    )
    assert response.status_code == 403

    response = client.post(
        f"{settings.API_V1_STR}/signals/",
        headers=superuser_token_headers,
        json={
            "product_id": product["id"],
            "observed_price": 150,
            "stock_status": "in_stock",
            "source_type": "manual",
            "url": "https://example.com/drop",
            "processing_status": "processed",
        },
    )
    assert response.status_code == 200
    assert response.json()["observed_price"] == 150
    assert response.json()["processing_status"] == "processed"

    response = client.get(
        f"{settings.API_V1_STR}/signals/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["count"] >= 1


def test_watchlist_crud_ownership(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers: dict[str, str],
) -> None:
    product = create_product(client, superuser_token_headers)

    response = client.post(
        f"{settings.API_V1_STR}/watchlists/",
        headers=normal_user_token_headers,
        json={
            "product_id": product["id"],
            "msrp_margin_percent": 10,
            "max_price": 170,
            "is_active": True,
            "email_enabled": True,
            "notify_on_restock": True,
            "notify_on_price_drop": True,
            "notification_cooldown_minutes": 30,
        },
    )
    assert response.status_code == 200
    watchlist = response.json()
    assert watchlist["product_id"] == product["id"]
    assert watchlist["notification_cooldown_minutes"] == 30

    response = client.put(
        f"{settings.API_V1_STR}/watchlists/{watchlist['id']}",
        headers=superuser_token_headers,
        json={"email_enabled": False},
    )
    assert response.status_code == 403

    response = client.put(
        f"{settings.API_V1_STR}/watchlists/{watchlist['id']}",
        headers=normal_user_token_headers,
        json={"email_enabled": False, "notify_on_price_drop": False},
    )
    assert response.status_code == 200
    assert response.json()["email_enabled"] is False
    assert response.json()["notify_on_price_drop"] is False


def test_dashboard_returns_current_user_tcg_summary(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    product = create_product(client, superuser_token_headers)

    watchlist_response = client.post(
        f"{settings.API_V1_STR}/watchlists/",
        headers=normal_user_token_headers,
        json={
            "product_id": product["id"],
            "msrp_margin_percent": 10,
            "email_enabled": True,
        },
    )
    assert watchlist_response.status_code == 200
    watchlist = watchlist_response.json()

    signal = DropSignal(
        product_id=uuid.UUID(product["id"]),
        observed_price=150,
        stock_status="in_stock",
        source_type="manual",
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)

    alert = AlertEvent(
        owner_id=uuid.UUID(watchlist["owner_id"]),
        watchlist_id=uuid.UUID(watchlist["id"]),
        signal_id=signal.id,
        channel="email",
        status="sent",
        public_message="Email alert sent.",
    )
    db.add(alert)
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/dashboard/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    dashboard = response.json()
    assert dashboard["counts"]["watchlists"] >= 1
    assert dashboard["counts"]["products"] >= 1
    assert any(item["id"] == watchlist["id"] for item in dashboard["watchlists"])
    assert any(item["id"] == str(signal.id) for item in dashboard["signals"])


def test_scrape_run_placeholder_is_superuser_only(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers: dict[str, str],
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/scrapes/twitter/pokemon-drops",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    simulated_drops = response.json()
    assert simulated_drops["count"] >= 1
    assert simulated_drops["data"][0]["game"] == "Pokemon"
    assert simulated_drops["data"][0]["author_handle"].startswith("@")

    response = client.get(
        f"{settings.API_V1_STR}/scrapes/twitter/pokemon-drops",
        headers=normal_user_token_headers,
        params={"q": "Prismatic", "limit": 1},
    )
    assert response.status_code == 200
    filtered_drops = response.json()
    assert filtered_drops["count"] == 1
    assert "Prismatic" in filtered_drops["data"][0]["product_name"]

    response = client.post(
        f"{settings.API_V1_STR}/scrapes/run",
        headers=normal_user_token_headers,
        json={},
    )
    assert response.status_code == 403

    response = client.post(
        f"{settings.API_V1_STR}/scrapes/run",
        headers=superuser_token_headers,
        json={},
    )
    assert response.status_code == 200
    assert (
        response.json()["message"]
        == "Scrape runner is scaffolded but not implemented yet."
    )


def test_user_delete_cascades_watchlists_and_alerts(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    user = create_random_user(db)
    product = Product(
        game="Lorcana",
        name=f"Starter Deck {uuid.uuid4()}",
        product_type="Starter Deck",
        msrp=16.99,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    watchlist = Watchlist(product_id=product.id, owner_id=user.id)
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)

    signal = DropSignal(
        product_id=product.id,
        observed_price=15.99,
        stock_status="in_stock",
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)

    alert = AlertEvent(
        owner_id=user.id,
        watchlist_id=watchlist.id,
        signal_id=signal.id,
        channel="email",
        status="sent",
    )
    db.add(alert)
    db.commit()
    watchlist_id = watchlist.id
    alert_id = alert.id

    response = client.delete(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    assert (
        db.exec(select(Watchlist).where(Watchlist.id == watchlist_id)).first() is None
    )
    assert db.exec(select(AlertEvent).where(AlertEvent.id == alert_id)).first() is None
