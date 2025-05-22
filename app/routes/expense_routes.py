from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import date, timedelta
from app.models import ExpenseCreate, ExpenseUpdate, ExpenseOut
from app.auth import get_current_user
from app.database import get_pool

router = APIRouter()

@router.post("/expenses", response_model=ExpenseOut)
async def add_expense(data: ExpenseCreate, user=Depends(get_current_user)):
    pool = get_pool()
    row = await pool.fetchrow(
        "INSERT INTO expenses (user_id, amount, category, description, expense_date) VALUES ($1, $2, $3, $4, $5) RETURNING *",
        user["id"], data.amount, data.category, data.description, data.expense_date
    )
    return dict(row)

@router.get("/expenses", response_model=List[ExpenseOut])
async def list_expenses(
    filter: Optional[str] = Query(None, regex="^(week|month|quarter|custom)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user=Depends(get_current_user)
):
    pool = get_pool()
    query = "SELECT * FROM expenses WHERE user_id = $1"
    params = [user["id"]]
    today = date.today()

    if filter == "week":
        query += " AND expense_date BETWEEN $2 AND $3"
        params += [today - timedelta(days=7), today]
    elif filter == "month":
        query += " AND expense_date BETWEEN $2 AND $3"
        params += [today - timedelta(days=30), today]
    elif filter == "quarter":
        query += " AND expense_date BETWEEN $2 AND $3"
        params += [today - timedelta(days=90), today]
    elif filter == "custom":
        if not (start_date and end_date):
            raise HTTPException(400, "Custom filter requires start_date and end_date")
        query += " AND expense_date BETWEEN $2 AND $3"
        params += [start_date, end_date]

    query += " ORDER BY expense_date DESC"
    rows = await pool.fetch(query, *params)
    return [dict(r) for r in rows]

@router.put("/expenses/{expense_id}", response_model=ExpenseOut)
async def update_expense(expense_id: int, data: ExpenseUpdate, user=Depends(get_current_user)):
    if not data.dict(exclude_unset=True):
        raise HTTPException(400, "No data provided")

    pool = get_pool()
    base_query = "UPDATE expenses SET"
    values = []
    clauses = []
    idx = 1

    for field, value in data.dict(exclude_unset=True).items():
        clauses.append(f" {field} = ${idx}")
        values.append(value)
        idx += 1

    values += [expense_id, user["id"]]
    query = base_query + ",".join(clauses) + f" WHERE id = ${idx} AND user_id = ${idx + 1} RETURNING *"
    row = await pool.fetchrow(query, *values)
    if not row:
        raise HTTPException(404, "Expense not found")
    return dict(row)

@router.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(expense_id: int, user=Depends(get_current_user)):
    pool = get_pool()
    result = await pool.execute("DELETE FROM expenses WHERE id = $1 AND user_id = $2", expense_id, user["id"])
    if result.endswith("0"):
        raise HTTPException(404, "Expense not found")
