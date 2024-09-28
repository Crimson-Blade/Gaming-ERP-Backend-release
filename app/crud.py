from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
from pytz import timezone
from sqlalchemy import func
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