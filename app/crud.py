from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, date
from pytz import timezone
from sqlalchemy import func, extract
import uuid

# Registrations
def create_registration(db: Session, registration: schemas.RegistrationCreate):
    db_registration = models.Registration(
        name=registration.name,
        phone_number=registration.phone_number
    )
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    return db_registration

def get_registration(db: Session, user_id: uuid.UUID):
    return db.query(models.Registration).filter(models.Registration.user_id == user_id).first()

def search_registrations(db: Session, date=None, name=None, phone_number=None, onlyActive=None):
    query = db.query(models.Registration)
     # Apply the active filter after the main filters
    if onlyActive:
        query = query.filter(models.Registration.active == True)
    # Apply the existing filters
    if date:
        query = query.filter(func.date(models.Registration.date) == date)
    if name:
        query = query.filter(models.Registration.name.ilike(f"%{name}%"))
    if phone_number:
        query = query.filter(models.Registration.phone_number.ilike(f"%{phone_number}%"))
    
    
    return query.all()


# Systems
def create_system(db: Session, user_id: uuid.UUID, system: schemas.SystemCreate):
    db_system = models.System(
        user_id=user_id,
        name=system.name,
        amount=system.amount,
        start_time=system.start_time,
        end_time=system.end_time
    )
    db.add(db_system)
    db.commit()
    db.refresh(db_system)
    return db_system

def get_systems_by_user(db: Session, user_id: uuid.UUID):
    return db.query(models.System).filter(models.System.user_id == user_id).all()

def update_system_end_time(db: Session, system_id: int):
    system = db.query(models.System).filter(models.System.id == system_id).first()
    if system and not system.end_time:  # Only update if end_time is not set
        system.end_time = datetime.now(timezone('UTC'))
        print(system.end_time)
        # Set current time as end time
        db.commit()
        db.refresh("endtime:",system)
    return system

# Function to set the end_time for all systems without an end_time for a specific user
def set_end_time_for_active_systems(db: Session, user_id: str):
    active_systems = db.query(models.System).filter(models.System.user_id == user_id, models.System.end_time == None).all()
    current_time = datetime.now(timezone('UTC'))
    for system in active_systems:
        system.end_time = current_time  # Set current time as end time
    db.commit()  # Commit changes after updating all systems
    return active_systems

# Menu
def create_menu_item(db: Session, menu_item: schemas.MenuCreate):
    db_item = models.Menu(
        item_name=menu_item.item_name,
        item_price=menu_item.item_price,
        item_photo=menu_item.item_photo
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_menu(db: Session):
    return db.query(models.Menu).all()

# Orders
def create_order(db: Session, user_id: uuid.UUID, order: schemas.OrderCreate):
    db_order = models.Order(
        user_id=user_id,
        item_name=order.item_name,
        quantity=order.quantity,
        price=order.price
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders_by_user(db: Session, user_id: uuid.UUID):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()

# Billing
def calculate_total(db: Session, user_id: uuid.UUID):
    # Set end time for all active systems
    set_end_time_for_active_systems(db, user_id)
    
    systems = get_systems_by_user(db, user_id)
    orders = get_orders_by_user(db, user_id)
    
    # total_systems = sum(
    #     system.amount * ((system.end_time - system.start_time).total_seconds() / 3600)
    #     for system in systems if system.end_time
    # )
    # total_orders = sum(order.price * order.quantity for order in orders)
    # total = total_systems + total_orders
    # total = 0
    # print(systems[0].amount)
    #map around all systems items and order to add all the amounts
    total = 0
    for system in systems:
        total += system.amount * ((system.end_time - system.start_time).total_seconds() / 3600)
    for order in orders:
        total += order.price * order.quantity
    print(total)
    return {
        'systems': systems,
        'orders': orders,
        'total_cost': total
    }

def finalize_bill(db: Session, user_id: uuid.UUID, total_cost: float):
    registration = get_registration(db, user_id)
    registration.bill = total_cost
    db.commit()
    db.refresh(registration)
    return registration

# End Session
def end_session(db: Session, user_id: uuid.UUID):
    #finalise bill here
    finalize_bill(db, user_id, 0.0)
    registration = get_registration(db, user_id)
    registration.active = False
    db.commit()
    db.refresh(registration)
    return registration

# Analytics

# Function to get daily, weekly, or monthly registration stats within a date range
def get_registration_stats(db: Session, period: str, start_date: date, end_date: date):
    if period == "daily":
        data = db.query(
            func.date(models.Registration.date).label("day"),
            func.count(models.Registration.user_id).label("registrations")
        ).filter(
            models.Registration.date >= start_date,
            models.Registration.date <= end_date
        ).group_by(func.date(models.Registration.date)).all()

        labels = [str(row.day) for row in data]
        values = [row.registrations for row in data]
        return {"labels": labels, "values": values}

    elif period == "weekly":
        data = db.query(
            func.date_trunc('week', models.Registration.date).label("week"),
            func.count(models.Registration.user_id).label("registrations")
        ).filter(
            models.Registration.date >= start_date,
            models.Registration.date <= end_date
        ).group_by(func.date_trunc('week', models.Registration.date)).all()

        labels = [str(row.week) for row in data]
        values = [row.registrations for row in data]
        return {"labels": labels, "values": values}

    elif period == "monthly":
        data = db.query(
            extract('month', models.Registration.date).label("month"),
            func.count(models.Registration.user_id).label("registrations")
        ).filter(
            models.Registration.date >= start_date,
            models.Registration.date <= end_date
        ).group_by(extract('month', models.Registration.date)).all()

        month_names = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
        labels = [month_names.get(int(row.month), "Unknown") for row in data]
        values = [row.registrations for row in data]
        
        return {"labels": labels, "values": values}
       
from datetime import datetime

# Function to get active and inactive user count
def get_active_inactive_users(db: Session):
    today = datetime.utcnow().date()

    active_users = db.query(func.count(models.Registration.user_id)).filter(
        models.Registration.active == True,
        func.date(models.Registration.date) == today
    ).scalar()

    inactive_users = db.query(func.count(models.Registration.user_id)).filter(
        models.Registration.active == False,
        func.date(models.Registration.date) == today
    ).scalar()

    return {
        "values": [active_users, inactive_users]
    }

# Function to get income stats from systems and orders for a given period and date range
def get_income_stats(db: Session, period: str, start_date: date, end_date: date):
    if period == "daily":
        # Calculate income from systems (services like lounge, consoles, etc.)
        systems_income = db.query(
            func.date(models.System.start_time).label("day"),
            func.sum(models.System.amount * (func.extract('epoch', models.System.end_time - models.System.start_time) / 3600)).label("income")
        ).filter(
            models.System.start_time >= start_date,
            models.System.start_time <= end_date,
            models.System.end_time.isnot(None)
        ).group_by(func.date(models.System.start_time)).all()

        # Calculate income from orders, using a date or timestamp field
        orders_income = db.query(
            func.date(models.Order.created_at).label("day"),  # Assuming 'created_at' is the timestamp field
            func.sum(models.Order.price * models.Order.quantity).label("income")
        ).filter(
            models.Order.created_at >= start_date,
            models.Order.created_at <= end_date,
            models.Order.user_id.in_(
                db.query(models.Registration.user_id).filter(
                    models.Registration.date >= start_date,
                    models.Registration.date <= end_date
                )
            )
        ).group_by(func.date(models.Order.created_at)).all()

        return format_income(merge_incomes_by_day(systems_income, orders_income), "daily")

    # Calculate income from systems (services like lounge, consoles, etc.)
    elif period == "weekly":
        systems_income = db.query(
            func.date_trunc('week', models.System.start_time).label("week"),
            func.sum(models.System.amount * (func.extract('epoch', models.System.end_time - models.System.start_time) / 3600)).label("income")
        ).filter(
            models.System.start_time >= start_date,
            models.System.start_time <= end_date,
            models.System.end_time.isnot(None)
        ).group_by(func.date_trunc('week', models.System.start_time)).all()

        # Calculate income from orders, using a date or timestamp field
        orders_income = db.query(
            func.date_trunc('week', models.Order.created_at).label("week"),  # Use 'created_at' or another date field
            func.sum(models.Order.price * models.Order.quantity).label("income")
        ).filter(
            models.Order.created_at >= start_date,  # Filter based on the date field
            models.Order.created_at <= end_date,
            models.Order.user_id.in_(
                db.query(models.Registration.user_id).filter(
                    models.Registration.date >= start_date,
                    models.Registration.date <= end_date
                )
            )
        ).group_by(func.date_trunc('week', models.Order.created_at)).all()  # Group by the correct date field

        return format_income(merge_incomes_by_week(systems_income, orders_income), "weekly")

    # Calculate income from systems (services like lounge, consoles, etc.)
    elif period == "monthly":
        systems_income = db.query(
            extract('month', models.System.start_time).label("month"),
            func.sum(models.System.amount * (func.extract('epoch', models.System.end_time - models.System.start_time) / 3600)).label("income")
        ).filter(
            models.System.start_time >= start_date,
            models.System.start_time <= end_date,
            models.System.end_time.isnot(None)
        ).group_by(extract('month', models.System.start_time)).all()

        # Calculate income from orders using a date or timestamp field
        orders_income = db.query(
            extract('month', models.Order.created_at).label("month"),  # Use 'created_at' or another date field
            func.sum(models.Order.price * models.Order.quantity).label("income")
        ).filter(
            models.Order.created_at >= start_date,  # Use the correct date field for filtering
            models.Order.created_at <= end_date,
            models.Order.user_id.in_(
                db.query(models.Registration.user_id).filter(
                    models.Registration.date >= start_date,
                    models.Registration.date <= end_date
                )
            )
        ).group_by(extract('month', models.Order.created_at)).all()  # Group by the correct date field

        return format_income(merge_incomes_by_month(systems_income, orders_income), "monthly")

# Function to format the merged income data into the desired structure
def format_income(merged_income, period):
    labels = []
    values = []

    for row in merged_income:
        if period == "daily":
            labels.append(row["date"].strftime("%d/%m"))  # Format as 'dd/mm'
        elif period == "weekly":
            labels.append(row["week"].strftime("Week %U"))  # Format as 'Week <number>'
        elif period == "monthly":
            labels.append(row["month"])  # Month already formatted as 'mmm'
        values.append(row["income"])

    return {"labels": labels, "values": values}


# Functions to merge incomes by day, week, and month remain unchanged, but returning merged dictionary
def merge_incomes_by_day(systems_income, orders_income):
    merged_income = {}
    for row in systems_income:
        merged_income[row.day] = {"date": row.day, "income": row.income}
    
    for row in orders_income:
        if row.day in merged_income:
            merged_income[row.day]["income"] += row.income
        else:
            merged_income[row.day] = {"date": row.day, "income": row.income}

    return list(merged_income.values())


def merge_incomes_by_week(systems_income, orders_income):
    merged_income = {}
    for row in systems_income:
        merged_income[row.week] = {"week": row.week, "income": row.income}
    
    for row in orders_income:
        if row.week in merged_income:
            merged_income[row.week]["income"] += row.income
        else:
            merged_income[row.week] = {"week": row.week, "income": row.income}

    return list(merged_income.values())


def merge_incomes_by_month(systems_income, orders_income):
    merged_income = {}
    month_names = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
    for row in systems_income:
        month_name = month_names.get(int(row.month), "Unknown")
        merged_income[month_name] = {"month": month_name, "income": row.income}
    
    for row in orders_income:
        month_name = month_names.get(int(row.month), "Unknown")
        if month_name in merged_income:
            merged_income[month_name]["income"] += row.income
        else:
            merged_income[month_name] = {"month": month_name, "income": row.income}

    return list(merged_income.values())

from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from datetime import date

from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from datetime import date

# Function to get average session duration within a date range and period (daily, weekly, monthly) only for 'lounge' systems
def get_average_session_duration(db: Session, period: str, start_date: date, end_date: date):
    if period == "daily":
        data = db.query(
            func.date(models.System.start_time).label("day"),
            func.avg(
                func.extract('epoch', (models.System.end_time - models.System.start_time)) / 60  # Convert seconds to hours
            ).label("avg_duration")
        ).filter(
            models.System.start_time >= start_date,
            models.System.start_time <= end_date,
            models.System.end_time.isnot(None),  # Only sessions that have ended
            models.System.name == "lounge"  # Filter for "lounge" systems
        ).group_by(func.date(models.System.start_time)).all()

        labels = [str(row.day) for row in data]
        values = [row.avg_duration for row in data]
        return {"labels": labels, "values": values}

    elif period == "weekly":
        data = db.query(
            func.date_trunc('week', models.System.start_time).label("week"),
            func.avg(
                func.extract('epoch', (models.System.end_time - models.System.start_time)) / 60  # Convert seconds to hours
            ).label("avg_duration")
        ).filter(
            models.System.start_time >= start_date,
            models.System.start_time <= end_date,
            models.System.end_time.isnot(None),  # Only sessions that have ended
            models.System.name == "lounge"  # Filter for "lounge" systems
        ).group_by(func.date_trunc('week', models.System.start_time)).all()

        labels = [str(row.week) for row in data]
        values = [row.avg_duration for row in data]
        return {"labels": labels, "values": values}

    elif period == "monthly":
        data = db.query(
            extract('month', models.System.start_time).label("month"),
            func.avg(
                func.extract('epoch', (models.System.end_time - models.System.start_time)) / 60  # Convert seconds to hours
            ).label("avg_duration")
        ).filter(
            models.System.start_time >= start_date,
            models.System.start_time <= end_date,
            models.System.end_time.isnot(None),  # Only sessions that have ended
            models.System.name == "lounge"  # Filter for "lounge" systems
        ).group_by(extract('month', models.System.start_time)).all()

        month_names = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
        labels = [month_names.get(int(row.month), "Unknown") for row in data]
        values = [row.avg_duration for row in data]
        
        return {"labels": labels, "values": values}

    return {"labels": [], "values": []}  # Return empty response if period is invalid