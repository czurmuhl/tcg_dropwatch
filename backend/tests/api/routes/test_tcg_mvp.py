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


def test_source_crud_is_superuser_only(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers: dict[str, str],
) -> None:
    product = create_product(client, superuser_token_headers)

    response = client.get(
        f"{settings.API_V1_STR}/sources/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403

    response = client.post(
        f"{settings.API_V1_STR}/sources/",
        headers=superuser_token_headers,
        json={
            "product_id": product["id"],
            "retailer_name": "Demo Retailer",
            "url": "https://example.com/product",
            "price_selector": ".price",
            "stock_selector": ".stock",
            "is_active": True,
        },
    )
    assert response.status_code == 200
    source = response.json()
    assert source["retailer_name"] == "Demo Retailer"

    response = client.put(
        f"{settings.API_V1_STR}/sources/{source['id']}",
        headers=superuser_token_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


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
        },
    )
    assert response.status_code == 200
    assert response.json()["observed_price"] == 150

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
            "email_enabled": True,
        },
    )
    assert response.status_code == 200
    watchlist = response.json()
    assert watchlist["product_id"] == product["id"]

    response = client.put(
        f"{settings.API_V1_STR}/watchlists/{watchlist['id']}",
        headers=superuser_token_headers,
        json={"email_enabled": False},
    )
    assert response.status_code == 403

    response = client.put(
        f"{settings.API_V1_STR}/watchlists/{watchlist['id']}",
        headers=normal_user_token_headers,
        json={"email_enabled": False},
    )
    assert response.status_code == 200
    assert response.json()["email_enabled"] is False


def test_scrape_run_placeholder_is_superuser_only(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers: dict[str, str],
) -> None:
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
