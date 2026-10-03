import os
import random
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import Account, Category, Transaction, User


@dataclass(frozen=True)
class SeedUser:
    email: str
    display_name: str
    role: str
    password_env: str


DEMO_USERS = (
    SeedUser("demo@expense-tracker.example", "Demo User", "user", "DEMO_PASSWORD"),
    SeedUser("admin@expense-tracker.example", "Admin User", "admin", "ADMIN_PASSWORD"),
    SeedUser("root@expense-tracker.example", "Root User", "root", "ROOT_PASSWORD"),
)

EXPENSE_CATEGORIES = [
    ("Oziq-ovqat", "🍎"), ("Restoran va kafe", "🍽️"), ("Transport", "🚕"),
    ("Uy-joy", "🏠"), ("Kommunal", "💡"), ("Internet va aloqa", "📱"),
    ("Sog'liq", "💊"), ("Ta'lim", "📚"), ("Kiyim-kechak", "👕"),
    ("Ko'ngilochar", "🎬"), ("Xaridlar", "🛍️"), ("Sayohat", "✈️"),
    ("Sport", "🏃"), ("Obunalar", "📺"), ("Boshqa", "📦"),
]
INCOME_CATEGORIES = [
    ("Maosh", "💰"), ("Bonus", "🎁"), ("Freelance", "💻"),
    ("Investitsiya", "📈"), ("Sovg'a", "🎉"), ("Boshqa daromad", "➕"),
]

MERCHANTS = {
    "Oziq-ovqat": ["Korzinka", "Makro", "Havas", "Carrefour", "Baraka Market", "Olma Market"],
    "Restoran va kafe": ["Evos", "Bellissimo Pizza", "Oqtepa Lavash", "Feed Up", "Bon!", "Safia"],
    "Transport": ["Yandex Go", "MyTaxi", "UzAuto Petrol", "UNG Petro", "EVOS Taxi"],
    "Uy-joy": ["Ijara to'lovi", "Uy ta'miri", "Mebel Market", "Texnomart"],
    "Kommunal": ["Hududgazta'minot", "Toshkent Suv Ta'minoti", "Hududiy Elektr Tarmoqlari"],
    "Internet va aloqa": ["Beeline", "Ucell", "Uztelecom", "Mobiuz"],
    "Sog'liq": ["Dori-Darmon", "Apteka", "Medion", "Shifo Nur"],
    "Ta'lim": ["Coursera", "Udemy", "Najot Ta'lim", "Kitoblar olami"],
    "Kiyim-kechak": ["LC Waikiki", "Zara", "DeFacto", "Koton"],
    "Ko'ngilochar": ["Kinoteatr", "PlayStation", "Bowling", "Konsert"],
    "Xaridlar": ["Uzum Market", "Wildberries", "Texnomart", "Media Park"],
    "Sayohat": ["Uzbekistan Airways", "Booking", "Airbnb", "Travel Agency"],
    "Sport": ["Sportmaster", "Fitness Club", "Swimming Pool"],
    "Obunalar": ["Netflix", "YouTube Premium", "Spotify", "Google One"],
    "Boshqa": ["Naqd pul", "Xizmat ko'rsatish", "Kuryer"],
}

AMOUNTS = {
    "Oziq-ovqat": (25000, 450000), "Restoran va kafe": (30000, 300000),
    "Transport": (10000, 180000), "Uy-joy": (1500000, 6500000),
    "Kommunal": (70000, 700000), "Internet va aloqa": (30000, 250000),
    "Sog'liq": (30000, 900000), "Ta'lim": (80000, 1500000),
    "Kiyim-kechak": (120000, 1800000), "Ko'ngilochar": (30000, 500000),
    "Xaridlar": (50000, 2500000), "Sayohat": (300000, 8000000),
    "Sport": (80000, 800000), "Obunalar": (15000, 250000),
    "Boshqa": (20000, 600000),
}


def seed_system_users(db: Session) -> None:
    changed = False
    for spec in DEMO_USERS:
        password = os.getenv(spec.password_env)
        if not password:
            continue
        user = db.scalar(select(User).where(User.email == spec.email))
        if user is None:
            user = User(
                email=spec.email,
                password_hash=hash_password(password),
                display_name=spec.display_name,
                base_currency="UZS",
                role=spec.role,
                is_active=True,
            )
            db.add(user)
            db.flush()
            changed = True
        elif user.role != spec.role or not user.is_active:
            user.role = spec.role
            user.is_active = True
            changed = True
    if changed:
        db.commit()

    if os.getenv("SEED_DEMO_DATA", "").lower() in {"1", "true", "yes"}:
        seed_demo_finance_data(db)


def _category_map(db: Session, user: User) -> dict[tuple[str, str], Category]:
    result: dict[tuple[str, str], Category] = {}
    for name, icon in EXPENSE_CATEGORIES:
        result[("expense", name)] = db.scalar(
            select(Category).where(Category.user_id == user.id, Category.name == name, Category.kind == "expense")
        ) or Category(user_id=user.id, name=name, kind="expense", icon=icon)
    for name, icon in INCOME_CATEGORIES:
        result[("income", name)] = db.scalar(
            select(Category).where(Category.user_id == user.id, Category.name == name, Category.kind == "income")
        ) or Category(user_id=user.id, name=name, kind="income", icon=icon)
    for category in result.values():
        if category.id is None:
            db.add(category)
    db.flush()
    return result


def seed_demo_finance_data(db: Session) -> None:
    # Keep this idempotent: a restart must not multiply the test dataset.
    demo = db.scalar(select(User).where(User.email == "demo@expense-tracker.example"))
    if demo is None:
        return
    existing = db.scalar(select(func.count(Transaction.id)).where(Transaction.user_id == demo.id))
    if existing and existing >= 1000:
        return

    accounts = list(db.scalars(select(Account).where(Account.user_id == demo.id).order_by(Account.created_at)).all())
    if not accounts:
        accounts = [
            Account(user_id=demo.id, name="Asosiy karta", currency="UZS", opening_balance=Decimal("8500000")),
            Account(user_id=demo.id, name="Jamg'arma", currency="UZS", opening_balance=Decimal("22000000")),
            Account(user_id=demo.id, name="Naqd pul", currency="UZS", opening_balance=Decimal("1500000")),
        ]
        db.add_all(accounts)
        db.flush()

    categories = _category_map(db, demo)
    rng = random.Random(20261003)
    start = date.today() - timedelta(days=365)
    rows: list[Transaction] = []

    # 12 months of salary + realistic recurring and discretionary spending.
    for month_offset in range(12):
        month_start = (start.replace(day=1) + timedelta(days=32 * month_offset)).replace(day=1)
        salary_day = min(25, 28)
        salary_date = month_start.replace(day=salary_day)
        salary = Decimal(str(rng.randrange(9500000, 14500001, 250000)))
        rows.append(Transaction(
            user_id=demo.id, account_id=accounts[0].id,
            category_id=categories[("income", "Maosh")].id, type="income",
            amount=salary, currency="UZS", description="Oylik maosh",
            transaction_date=salary_date, idempotency_key=f"seed-salary-{month_offset}",
        ))
        if month_offset in {2, 5, 8, 11}:
            bonus = Decimal(str(rng.randrange(800000, 3000001, 100000)))
            rows.append(Transaction(
                user_id=demo.id, account_id=accounts[0].id,
                category_id=categories[("income", "Bonus")].id, type="income",
                amount=bonus, currency="UZS", description="Kvartalik bonus",
                transaction_date=salary_date + timedelta(days=1), idempotency_key=f"seed-bonus-{month_offset}",
            ))

        # Fixed monthly obligations.
        fixed = [
            ("Uy-joy", rng.randrange(2800000, 4200001, 100000), "Oylik ijara"),
            ("Kommunal", rng.randrange(180000, 520001, 20000), "Kommunal to'lovlar"),
            ("Internet va aloqa", rng.randrange(70000, 220001, 10000), "Internet va aloqa"),
            ("Obunalar", rng.randrange(80000, 220001, 10000), "Raqamli obunalar"),
        ]
        for idx, (cat, amount, desc) in enumerate(fixed):
            day = min(5 + idx * 6, 27)
            rows.append(Transaction(
                user_id=demo.id, account_id=accounts[0].id,
                category_id=categories[("expense", cat)].id, type="expense",
                amount=Decimal(amount), currency="UZS",
                description=desc, transaction_date=month_start.replace(day=day),
                idempotency_key=f"seed-fixed-{month_offset}-{idx}",
            ))

        # 65-ish variable transactions per month.
        for n in range(65):
            cat = rng.choices(
                list(AMOUNTS),
                weights=[18, 9, 10, 2, 4, 4, 3, 2, 4, 4, 6, 1, 2, 3, 3],
                k=1,
            )[0]
            lo, hi = AMOUNTS[cat]
            variable_amount = Decimal(rng.randrange(lo, hi + 1, max(1000, (hi - lo) // 30)))
            day = rng.randrange(1, 29)
            if month_offset == 11 and cat in {"Kiyim-kechak", "Xaridlar"}:
                variable_amount = variable_amount * Decimal("1.25")
            merchant = rng.choice(MERCHANTS[cat])
            rows.append(Transaction(
                user_id=demo.id, account_id=accounts[0].id,
                category_id=categories[("expense", cat)].id, type="expense",
                amount=variable_amount, currency="UZS",
                description=merchant, transaction_date=month_start.replace(day=day),
                idempotency_key=f"seed-tx-{month_offset}-{n}",
            ))

        # Occasional freelance income.
        if month_offset % 3 == 1:
            freelance_amount = Decimal(rng.randrange(700000, 2800001, 100000))
            rows.append(Transaction(
                user_id=demo.id, account_id=accounts[0].id,
                category_id=categories[("income", "Freelance")].id, type="income",
                amount=freelance_amount, currency="UZS", description="Freelance loyiha",
                transaction_date=month_start.replace(day=18),
                idempotency_key=f"seed-freelance-{month_offset}",
            ))

    # Add deterministic savings transfers as income-side test data in a separate account.
    # The current model has no transfer type, so these are represented as savings income
    # solely to exercise account/category/date aggregation.
    for n in range(12):
        d = (start.replace(day=1) + timedelta(days=32 * n)).replace(day=10)
        saving_amount = Decimal(rng.randrange(500000, 1800001, 100000))
        rows.append(Transaction(
            user_id=demo.id, account_id=accounts[1].id,
            category_id=categories[("income", "Boshqa daromad")].id, type="income",
            amount=saving_amount, currency="UZS", description="Jamg'armaga tushum",
            transaction_date=d, idempotency_key=f"seed-saving-{n}",
        ))

    # Top up with varied rows until the requested test volume is exactly 1000.
    while len(rows) < 1000:
        n = len(rows)
        month_offset = n % 12
        month_start = (start.replace(day=1) + timedelta(days=32 * month_offset)).replace(day=1)
        cat = rng.choice(list(AMOUNTS))
        lo, hi = AMOUNTS[cat]
        extra_amount = Decimal(rng.randrange(lo, hi + 1, 1000))
        rows.append(Transaction(
            user_id=demo.id, account_id=rng.choice(accounts).id,
            category_id=categories[("expense", cat)].id, type="expense",
            amount=extra_amount, currency="UZS",
            description=rng.choice(MERCHANTS[cat]),
            transaction_date=month_start.replace(day=rng.randrange(1, 29)),
            idempotency_key=f"seed-extra-{n}",
        ))

    db.add_all(rows[:1000])
    db.commit()
