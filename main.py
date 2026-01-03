from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, PositiveFloat
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, Date, DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, datetime
from calendar import monthrange

# -----------------------
# Database setup
# -----------------------
DATABASE_URL = "sqlite:///./expenses.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -----------------------
# Models
# -----------------------
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# -----------------------
# App setup
# -----------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Dependencies
# -----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------
# Schemas
# -----------------------
class ExpenseBase(BaseModel):
    amount: PositiveFloat
    category: str
    description: str | None = None
    date: date

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# -----------------------
# Expense Routes
# -----------------------
@app.post("/expenses", response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = Expense(
        amount=expense.amount,
        category=expense.category.lower().strip(),
        description=expense.description,
        date=expense.date
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    db: Session = Depends(get_db)
):
    start_date = date(year, month, 1)
    end_date = date(year, month, monthrange(year, month)[1])

    return (
        db.query(Expense)
        .filter(Expense.date >= start_date)
        .filter(Expense.date <= end_date)
        .order_by(Expense.date.desc())
        .all()
    )

@app.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, updated: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(404, "Expense not found")

    expense.amount = updated.amount
    expense.category = updated.category.lower().strip()
    expense.description = updated.description
    expense.date = updated.date

    db.commit()
    db.refresh(expense)
    return expense

@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(404, "Expense not found")

    db.delete(expense)
    db.commit()

# -----------------------
# SUMMARY (THIS FIXES THE PIE)
# -----------------------
@app.get("/expenses/summary")
def expense_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    db: Session = Depends(get_db)
):
    start_date = date(year, month, 1)
    end_date = date(year, month, monthrange(year, month)[1])

    expenses = (
        db.query(Expense)
        .filter(Expense.date >= start_date)
        .filter(Expense.date <= end_date)
        .all()
    )

    total_spent = sum(e.amount for e in expenses)

    by_category = {}
    for e in expenses:
        by_category[e.category] = by_category.get(e.category, 0) + e.amount

    return {
        "total_spent": round(total_spent, 2),
        "by_category": by_category
    }
