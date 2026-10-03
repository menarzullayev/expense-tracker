from datetime import date, timedelta
from time import perf_counter

from app.core.security import hash_password, verify_password


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def make_account_and_category(client, token: str):
    headers = auth(token)
    account = client.post(
        "/v1/finance/accounts",
        headers=headers,
        json={"name": "Main", "currency": "UZS", "opening_balance": "1000000"},
    ).json()
    category = client.post(
        "/v1/finance/categories",
        headers=headers,
        json={"name": "Food", "kind": "expense", "icon": "🍎"},
    ).json()
    return headers, account, category


def test_unit_password_hash_round_trip():
    hashed = hash_password("StrongPass123!")
    assert hashed != "StrongPass123!"
    assert verify_password("StrongPass123!", hashed)
    assert not verify_password("wrong", hashed)


def test_integration_finance_flow(client, registered_user):
    headers, account, category = make_account_and_category(client, registered_user)
    response = client.post(
        "/v1/finance/transactions",
        headers={**headers, "Idempotency-Key": "integration-1"},
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "expense",
            "amount": "25000",
            "currency": "UZS",
            "description": "Lunch",
            "transaction_date": str(date.today()),
        },
    )
    assert response.status_code == 201
    assert client.get("/v1/finance/transactions", headers=headers).status_code == 200


def test_contract_response_shapes(client, registered_user):
    headers, account, category = make_account_and_category(client, registered_user)
    assert {"id", "name", "currency", "opening_balance", "is_archived"} <= set(account)
    assert {"id", "name", "kind"} <= set(category)
    assert {"from_date", "to_date", "income", "expenses", "net", "transaction_count"} <= set(
        client.get("/v1/finance/summary", headers=headers).json()
    )


def test_validation_rejects_invalid_transaction(client, registered_user):
    headers, account, _ = make_account_and_category(client, registered_user)
    response = client.post(
        "/v1/finance/transactions",
        headers={**headers, "Idempotency-Key": "validation-1"},
        json={
            "account_id": account["id"],
            "type": "expense",
            "amount": "-1",
            "currency": "UZS",
            "description": "invalid",
            "transaction_date": str(date.today()),
        },
    )
    assert response.status_code == 422


def test_security_requires_authentication(client):
    assert client.get("/v1/finance/accounts").status_code == 401
    assert client.get("/v1/finance/categories").status_code == 401
    assert client.get("/v1/finance/transactions").status_code == 401


def test_authorization_prevents_cross_user_access(client):
    a = client.post(
        "/v1/auth/register",
        json={"email": "qa-a@example.com", "password": "StrongPass123!", "display_name": "A", "base_currency": "UZS"},
    ).json()["access_token"]
    b = client.post(
        "/v1/auth/register",
        json={"email": "qa-b@example.com", "password": "StrongPass123!", "display_name": "B", "base_currency": "UZS"},
    ).json()["access_token"]
    account = client.post("/v1/finance/accounts", headers=auth(a), json={"name": "Private", "currency": "UZS"}).json()
    assert client.get("/v1/finance/accounts", headers=auth(b)).json() == []
    assert client.get(f"/v1/finance/accounts/{account['id']}/balance", headers=auth(b)).status_code == 404


def test_idempotency_is_exactly_once(client, registered_user):
    headers, account, category = make_account_and_category(client, registered_user)
    payload = {
        "account_id": account["id"],
        "category_id": category["id"],
        "type": "expense",
        "amount": "10000",
        "currency": "UZS",
        "description": "Coffee",
        "transaction_date": str(date.today()),
    }
    h = {**headers, "Idempotency-Key": "exactly-once"}
    first = client.post("/v1/finance/transactions", headers=h, json=payload)
    second = client.post("/v1/finance/transactions", headers=h, json=payload)
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert len(client.get("/v1/finance/transactions", headers=headers).json()) == 1


def test_boundary_filters_are_inclusive(client, registered_user):
    headers, account, category = make_account_and_category(client, registered_user)
    d1 = date.today() - timedelta(days=2)
    d2 = date.today()
    for key, d in (("boundary-1", d1), ("boundary-2", d2)):
        response = client.post(
            "/v1/finance/transactions",
            headers={**headers, "Idempotency-Key": key},
            json={
                "account_id": account["id"],
                "category_id": category["id"],
                "type": "expense",
                "amount": "1000",
                "currency": "UZS",
                "description": key,
                "transaction_date": str(d),
            },
        )
        assert response.status_code == 201
    result = client.get(
        "/v1/finance/transactions",
        headers=headers,
        params={"from_date": str(d1), "to_date": str(d2)},
    )
    assert len(result.json()) == 2


def test_data_integrity_balance_and_report(client, registered_user):
    headers, account, category = make_account_and_category(client, registered_user)
    client.post(
        "/v1/finance/transactions",
        headers={**headers, "Idempotency-Key": "integrity-1"},
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "expense",
            "amount": "100000",
            "currency": "UZS",
            "description": "Food",
            "transaction_date": str(date.today()),
        },
    )
    balance = client.get(f"/v1/finance/accounts/{account['id']}/balance", headers=headers)
    assert balance.json()["balance"] == "900000.0000"
    report = client.get(
        "/v1/finance/reports/category-breakdown",
        headers=headers,
        params={"from_date": str(date.today()), "to_date": str(date.today())},
    )
    assert report.json()[0]["category"] == "Food"


def test_smoke_critical_endpoints(client, registered_user):
    headers, _, _ = make_account_and_category(client, registered_user)
    paths = [
        "/v1/auth/me",
        "/v1/finance/accounts",
        "/v1/finance/categories",
        "/v1/finance/transactions",
        "/v1/finance/summary",
    ]
    assert all(client.get(path, headers=headers).status_code == 200 for path in paths)


def test_resilience_malformed_payload(client, registered_user):
    headers = auth(registered_user)
    response = client.post(
        "/v1/finance/categories",
        headers=headers,
        data='{"name":',
    )
    assert response.status_code == 422


def test_performance_transaction_listing(client, registered_user):
    headers, account, category = make_account_and_category(client, registered_user)
    for i in range(100):
        response = client.post(
            "/v1/finance/transactions",
            headers={**headers, "Idempotency-Key": f"perf-{i}"},
            json={
                "account_id": account["id"],
                "category_id": category["id"],
                "type": "expense",
                "amount": "1000",
                "currency": "UZS",
                "description": f"tx-{i}",
                "transaction_date": str(date.today()),
            },
        )
        assert response.status_code == 201
    started = perf_counter()
    response = client.get("/v1/finance/transactions?limit=100", headers=headers)
    elapsed = perf_counter() - started
    assert response.status_code == 200
    assert len(response.json()) == 100
    assert elapsed < 1.0


def test_regression_duplicate_category(client, registered_user):
    headers = auth(registered_user)
    body = {"name": "Food", "kind": "expense"}
    assert client.post("/v1/finance/categories", headers=headers, json=body).status_code == 201
    assert client.post("/v1/finance/categories", headers=headers, json=body).status_code == 409
