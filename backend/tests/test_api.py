from datetime import date


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_login_me(client):
    register = client.post("/v1/auth/register", json={"email":"a@example.com","password":"StrongPass123!","display_name":"A","base_currency":"UZS"})
    assert register.status_code == 201
    login = client.post("/v1/auth/login", json={"email":"a@example.com","password":"StrongPass123!"})
    assert login.status_code == 200
    me = client.get("/v1/auth/me", headers=auth(login.json()["access_token"]))
    assert me.status_code == 200
    assert me.json()["email"] == "a@example.com"


def test_duplicate_register(client):
    body={"email":"a@example.com","password":"StrongPass123!","display_name":"A","base_currency":"UZS"}
    assert client.post("/v1/auth/register", json=body).status_code == 201
    assert client.post("/v1/auth/register", json=body).status_code == 409


def test_transaction_idempotency_and_balance(client, registered_user):
    headers=auth(registered_user)
    account=client.post("/v1/finance/accounts", headers=headers, json={"name":"Cash","currency":"UZS","opening_balance":"1000000"})
    account_id=account.json()["id"]
    category=client.post("/v1/finance/categories", headers=headers, json={"name":"Food","kind":"expense"})
    category_id=category.json()["id"]
    payload={"account_id":account_id,"category_id":category_id,"type":"expense","amount":"100000","currency":"UZS","description":"Lunch","transaction_date":str(date.today())}
    r1=client.post("/v1/finance/transactions", headers={**headers,"Idempotency-Key":"abc-1"}, json=payload)
    r2=client.post("/v1/finance/transactions", headers={**headers,"Idempotency-Key":"abc-1"}, json=payload)
    assert r1.status_code == 201 and r2.status_code == 201
    assert r1.json()["id"] == r2.json()["id"]
    mismatch=client.post("/v1/finance/transactions", headers={**headers,"Idempotency-Key":"abc-1"}, json={**payload,"amount":"999"})
    assert mismatch.status_code == 409
    txs=client.get("/v1/finance/transactions", headers=headers)
    assert len(txs.json()) == 1
    balance=client.get(f"/v1/finance/accounts/{account_id}/balance", headers=headers)
    assert balance.json()["balance"] == "900000.0000"


def test_currency_mismatch_rejected(client, registered_user):
    headers=auth(registered_user)
    account=client.post("/v1/finance/accounts", headers=headers, json={"name":"Cash","currency":"USD","opening_balance":"100"}).json()
    r=client.post("/v1/finance/transactions", headers={**headers,"Idempotency-Key":"x"}, json={"account_id":account["id"],"type":"expense","amount":"10","currency":"UZS","description":"bad","transaction_date":str(date.today())})
    assert r.status_code == 400


def test_category_type_mismatch_rejected(client, registered_user):
    headers=auth(registered_user)
    account=client.post("/v1/finance/accounts", headers=headers, json={"name":"Cash","currency":"UZS"}).json()
    category=client.post("/v1/finance/categories", headers=headers, json={"name":"Salary","kind":"income"}).json()
    r=client.post("/v1/finance/transactions", headers={**headers,"Idempotency-Key":"x"}, json={"account_id":account["id"],"category_id":category["id"],"type":"expense","amount":"10","currency":"UZS","description":"bad","transaction_date":str(date.today())})
    assert r.status_code == 400


def test_unauthenticated(client):
    assert client.get("/v1/finance/accounts").status_code == 401


def test_health(client):
    assert client.get("/health/live").json() == {"status":"ok"}
    assert client.get("/health/ready").status_code == 200


def test_cross_user_account_isolation(client):
    a = client.post("/v1/auth/register", json={"email":"a@example.com","password":"StrongPass123!","display_name":"A","base_currency":"UZS"}).json()["access_token"]
    b = client.post("/v1/auth/register", json={"email":"b@example.com","password":"StrongPass123!","display_name":"B","base_currency":"UZS"}).json()["access_token"]
    account=client.post("/v1/finance/accounts", headers=auth(a), json={"name":"A Cash","currency":"UZS"}).json()
    assert client.get("/v1/finance/accounts", headers=auth(b)).json() == []
    r=client.post("/v1/finance/transactions", headers={**auth(b),"Idempotency-Key":"cross-user"}, json={"account_id":account["id"],"type":"expense","amount":"1","currency":"UZS","description":"bad","transaction_date":str(date.today())})
    assert r.status_code == 404
