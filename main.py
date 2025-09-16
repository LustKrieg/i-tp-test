from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Numeric, String, select, update, insert, and_
from sqlalchemy.orm import sessionmaker

# ---------- Настройки ----------
DATABASE_URL = "postgresql://postgres:postgres@db:5432/mydb"  # user:password@host:port/db
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
metadata = MetaData()

# ---------- Таблицы ----------
clients = Table("clients", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("address", String)
)

categories = Table("categories", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("parent_id", Integer)
)

items = Table("items", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("category_id", Integer),
    Column("price", Numeric),
    Column("stock_quantity", Integer)
)

orders = Table("orders", metadata,
    Column("id", Integer, primary_key=True),
    Column("client_id", Integer),
    Column("status", String)
)

order_items = Table("order_items", metadata,
    Column("order_id", Integer, primary_key=True),
    Column("item_id", Integer, primary_key=True),
    Column("quantity", Integer),
    Column("unit_price", Numeric)
)

# Создаем таблицы при старте
metadata.create_all(engine)

# ---------- FastAPI ----------
app = FastAPI(title="Order API")

class AddItemReq(BaseModel):
    item_id: int
    quantity: int

@app.post("/orders/{order_id}/items")
def add_item_to_order(order_id: int = Path(...), req: AddItemReq = None):
    if req is None or req.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    session = SessionLocal()
    try:
        # Проверка заказа
        ord_row = session.execute(select(orders).where(orders.c.id == order_id)).fetchone()
        if not ord_row:
            raise HTTPException(status_code=404, detail="Order not found")

        # Блокировка товара
        item_row = session.execute(select(items).where(items.c.id == req.item_id).with_for_update()).fetchone()
        if not item_row:
            raise HTTPException(status_code=404, detail="Item not found")
        if item_row.stock_quantity < req.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {item_row.stock_quantity}")

        # Проверка, есть ли уже в заказе
        oi = session.execute(select(order_items).where(and_(order_items.c.order_id == order_id,
                                                           order_items.c.item_id == req.item_id))).fetchone()
        if oi:
            session.execute(update(order_items)
                            .where(and_(order_items.c.order_id == order_id, order_items.c.item_id == req.item_id))
                            .values(quantity=oi.quantity + req.quantity))
        else:
            session.execute(insert(order_items).values(order_id=order_id,
                                                       item_id=req.item_id,
                                                       quantity=req.quantity,
                                                       unit_price=item_row.price))

        # Уменьшение склада
        session.execute(update(items)
                        .where(items.c.id == req.item_id)
                        .values(stock_quantity = items.c.stock_quantity - req.quantity))

        session.commit()
        return {"status": "ok", "order_id": order_id, "item_id": req.item_id, "added": req.quantity}

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()