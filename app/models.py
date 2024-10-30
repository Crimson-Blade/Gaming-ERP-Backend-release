from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from pytz import timezone
from .database import Base

class Registration(Base):
    __tablename__ = 'registrations'

    user_id = Column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone('UTC')))
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    bill = Column(Float, nullable=True)
    membership = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    systems = relationship('System', back_populates='registration')
    orders = relationship('Order', back_populates='registration')

class System(Base):
    __tablename__ = 'systems'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUIDType(as_uuid=True), ForeignKey('registrations.user_id'))
    name = Column(String, nullable=False)  # lounge, consoles, other
    amount = Column(Float, nullable=False)  # Price per hour
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)

    registration = relationship('Registration', back_populates='systems')

class Menu(Base):
    __tablename__ = 'menu'

    item_id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, nullable=False)
    item_price = Column(Float, nullable=False)
    item_photo = Column(String, nullable=True)  # Path or URL to photo

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUIDType(as_uuid=True), ForeignKey('registrations.user_id'))
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone('UTC')))
    registration = relationship('Registration', back_populates='orders')