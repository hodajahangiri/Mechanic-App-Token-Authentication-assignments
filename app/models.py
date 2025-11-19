from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Table, Column, Integer, ForeignKey, Float


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)


ticket_mechanic = Table(
    "ticket_mechanic",
    Base.metadata,
    Column("service_ticket_id", Integer, ForeignKey("service_tickets.id"),nullable=False),
    Column("mechanic_id", Integer, ForeignKey("mechanics.id"),nullable=False)
)

class Customers(Base):
    __tablename__ = "customers"

    id : Mapped[int] = mapped_column(primary_key=True)
    first_name : Mapped[str] = mapped_column(String(250), nullable=False)
    last_name : Mapped[str] = mapped_column(String(250), nullable=False)
    email : Mapped[str] = mapped_column(String(350), nullable=False, unique=True)
    password : Mapped[str] = mapped_column(String(200), nullable=False)
    phone : Mapped[str] = mapped_column(String(50), nullable=False)
    address : Mapped[str] = mapped_column(String(500), nullable=True)
    # relationship with service_tickets
    service_tickets : Mapped[list["Service_tickets"]] = relationship("Service_tickets", back_populates="customer")

class Service_tickets(Base):
    __tablename__ = "service_tickets"

    id : Mapped[int] = mapped_column(primary_key=True)
    customer_id : Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'), nullable=False)
    service_desc : Mapped[str] = mapped_column(String(400), nullable=True)
    price : Mapped[float] = mapped_column(Float, nullable=False)
    VIN : Mapped[str] = mapped_column(String(100), nullable=False)
    # relationship with customer
    customer : Mapped["Customers"] = relationship("Customers", back_populates="service_tickets")
    # relationship with mechanics
    mechanics : Mapped[list["Mechanics"]] = relationship("Mechanics", secondary= ticket_mechanic, back_populates="tickets")


class Mechanics(Base):
    __tablename__ = "mechanics"

    id : Mapped[int] = mapped_column(primary_key=True)
    first_name : Mapped[str] = mapped_column(String(250), nullable=False)
    last_name : Mapped[str] = mapped_column(String(250), nullable=False)
    email : Mapped[str] = mapped_column(String(350), nullable=False, unique=True)
    password : Mapped[str] = mapped_column(String(200), nullable=False)
    phone : Mapped[str] = mapped_column(String(50), nullable=False)
    address : Mapped[str] = mapped_column(String(500), nullable=True)
    salary : Mapped[float] = mapped_column(Float, nullable=False)
    # relationship with service_tickets
    tickets : Mapped[list["Service_tickets"]] = relationship("Service_tickets", secondary=ticket_mechanic, back_populates="mechanics")
