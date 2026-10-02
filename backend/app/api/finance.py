from datetime import date, timedelta
import hashlib
import json
from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Account, Category, Transaction, User
from app.services.audit import record_audit
from app.schemas.finance import (
    AccountCreate,
    AccountResponse,
    CategoryCreate,
    CategoryResponse,
    SummaryResponse,
    TransactionCreate,
    TransactionResponse,
)

router = APIRouter(prefix="/finance", tags=["finance"])


def ensure_account(db: Session, user_id: str, account_id: str) -> Account:
    account = db.scalar(select(Account).where(Account.id == account_id, Account.user_id == user_id))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


def ensure_category(db: Session, user_id: str, category_id: str | None, kind: str) -> Category | None:
    if category_id is None:
        return None
    category = db.scalar(
        select(Category).where(Category.id == category_id, Category.user_id == user_id, Category.kind == kind)
    )
    if not category:
        raise HTTPException(status_code=400, detail="Category does not match transaction type")
    return category


@router.get("/accounts", response_model=list[AccountResponse])
def list_accounts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(Account).where(Account.user_id == user.id).order_by(Account.created_at)).all())


@router.post("/accounts", response_model=AccountResponse, status_code=201)
def create_account(payload: AccountCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = Account(
        user_id=user.id,
        name=payload.name.strip(),
        currency=payload.currency.upper(),
        opening_balance=payload.opening_balance,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    record_audit(db, user_id=user.id, action="account.create", resource_type="account", resource_id=account.id)
    db.commit()
    return account


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(Category).where(Category.user_id == user.id).order_by(Category.name)).all())


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(payload: CategoryCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.scalar(
        select(Category).where(Category.user_id == user.id, Category.name == payload.name, Category.kind == payload.kind)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")
    category = Category(user_id=user.id, name=payload.name.strip(), kind=payload.kind, icon=payload.icon)
    db.add(category)
    db.commit()
    db.refresh(category)
    record_audit(db, user_id=user.id, action="category.create", resource_type="category", resource_id=category.id)
    db.commit()
    return category


@router.get("/transactions", response_model=list[TransactionResponse])
def list_transactions(
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    account_id: str | None = Query(default=None),
    transaction_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0, le=100000),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Transaction).where(Transaction.user_id == user.id)
    if from_date:
        stmt = stmt.where(Transaction.transaction_date >= from_date)
    if to_date:
        stmt = stmt.where(Transaction.transaction_date <= to_date)
    if account_id:
        stmt = stmt.where(Transaction.account_id == account_id)
    if transaction_type:
        if transaction_type not in {"income", "expense"}:
            raise HTTPException(status_code=400, detail="Invalid transaction_type")
        stmt = stmt.where(Transaction.type == transaction_type)
    stmt = stmt.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


@router.post("/transactions", response_model=TransactionResponse, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not idempotency_key or len(idempotency_key) > 255:
        raise HTTPException(status_code=400, detail="Idempotency-Key is required and must be <= 255 characters")
    request_hash = hashlib.sha256(payload.model_dump_json().encode("utf-8")).hexdigest()
    existing = db.scalar(
        select(Transaction).where(Transaction.user_id == user.id, Transaction.idempotency_key == idempotency_key)
    )
    if existing:
        if existing.request_hash != request_hash:
            raise HTTPException(status_code=409, detail="Idempotency-Key was already used for a different request")
        return existing
    account = ensure_account(db, user.id, payload.account_id)
    if payload.currency.upper() != account.currency:
        raise HTTPException(status_code=400, detail="Transaction currency must match account currency")
    ensure_category(db, user.id, payload.category_id, payload.type)
    transaction = Transaction(
        user_id=user.id,
        account_id=account.id,
        category_id=payload.category_id,
        type=payload.type,
        amount=payload.amount,
        currency=payload.currency.upper(),
        description=payload.description.strip(),
        transaction_date=payload.transaction_date,
        notes=payload.notes,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
    )
    db.add(transaction)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(
            select(Transaction).where(
                Transaction.user_id == user.id, Transaction.idempotency_key == idempotency_key
            )
        )
        if existing:
            if existing.request_hash != request_hash:
                raise HTTPException(status_code=409, detail="Idempotency-Key was already used for a different request")
            return existing
        raise
    db.refresh(transaction)
    record_audit(db, user_id=user.id, action="transaction.create", resource_type="transaction", resource_id=transaction.id)
    db.commit()
    return transaction


@router.get("/accounts/{account_id}/balance")
def account_balance(account_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = ensure_account(db, user.id, account_id)
    income = db.scalar(select(func.coalesce(func.sum(Transaction.amount), Decimal("0"))).where(
        Transaction.user_id == user.id, Transaction.account_id == account.id, Transaction.type == "income"
    )) or Decimal("0")
    expenses = db.scalar(select(func.coalesce(func.sum(Transaction.amount), Decimal("0"))).where(
        Transaction.user_id == user.id, Transaction.account_id == account.id, Transaction.type == "expense"
    )) or Decimal("0")
    balance = account.opening_balance + income - expenses
    return {"account_id": account.id, "currency": account.currency, "balance": format(balance, "f")}


@router.get("/reports/category-breakdown")
def category_breakdown(
    from_date: date,
    to_date: date,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be <= to_date")
    rows = db.execute(
        select(Category.name, func.sum(Transaction.amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Transaction.type == "expense",
            Transaction.transaction_date.between(from_date, to_date),
            Transaction.currency == user.base_currency,
        )
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()
    return [{"category": name, "amount": amount} for name, amount in rows]


@router.get("/summary", response_model=SummaryResponse)
def summary(
    from_date: date | None = None,
    to_date: date | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not from_date and not to_date:
        today = date.today()
        from_date, to_date = today.replace(day=1), today
    elif not from_date:
        from_date = to_date - timedelta(days=30)
    elif not to_date:
        to_date = from_date + timedelta(days=30)
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be <= to_date")

    rows = db.execute(
        select(Transaction.type, func.coalesce(func.sum(Transaction.amount), Decimal("0")), func.count(Transaction.id))
        .where(
            Transaction.user_id == user.id,
            Transaction.transaction_date >= from_date,
            Transaction.transaction_date <= to_date,
            Transaction.currency == user.base_currency,
        )
        .group_by(Transaction.type)
    ).all()
    income = Decimal("0")
    expenses = Decimal("0")
    count = 0
    for kind, total, row_count in rows:
        count += row_count
        if kind == "income":
            income = total
        elif kind == "expense":
            expenses = total
    return SummaryResponse(
        from_date=from_date,
        to_date=to_date,
        income=income,
        expenses=expenses,
        net=income - expenses,
        transaction_count=count,
    )
