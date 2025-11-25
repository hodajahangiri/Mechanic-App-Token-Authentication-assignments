from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Table, Column, Integer, ForeignKey, Float


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)


ticket_mechanics = Table(
    "ticket_mechanics",
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
    # Relationship with service_tickets
    service_tickets : Mapped[list["Service_tickets"]] = relationship("Service_tickets", back_populates="customer")

class Service_tickets(Base):
    __tablename__ = "service_tickets"

    id : Mapped[int] = mapped_column(primary_key=True)
    customer_id : Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'), nullable=False)
    service_desc : Mapped[str] = mapped_column(String(400), nullable=True)
    price : Mapped[float] = mapped_column(Float, nullable=False)
    VIN : Mapped[str] = mapped_column(String(100), nullable=False)
    # Relationship with customer
    customer : Mapped["Customers"] = relationship("Customers", back_populates="service_tickets")
    # Relationship with mechanics
    mechanics : Mapped[list["Mechanics"]] = relationship("Mechanics", secondary= ticket_mechanics, back_populates="tickets")
    # Relationship with parts
    parts : Mapped[list["Parts"]] = relationship("Parts", back_populates="service_ticket")


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
    # Relationship with service_tickets
    tickets : Mapped[list["Service_tickets"]] = relationship("Service_tickets", secondary=ticket_mechanics, back_populates="mechanics")


class Parts(Base):
    __tablename__ = "parts"

    id : Mapped[int] = mapped_column(primary_key=True)
    ticket_id : Mapped[int] = mapped_column(Integer, ForeignKey('service_tickets.id'), nullable=True)
    desc_id : Mapped[int] = mapped_column(Integer, ForeignKey('part_descriptions.id'),nullable=False)
    serial_number : Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    # Relationship with service_tickets
    service_ticket : Mapped["Service_tickets"] = relationship("Service_tickets", back_populates="parts")
    # Relationship with pert_descriptions
    part_description : Mapped["PartDescriptions"] = relationship("PartDescriptions", back_populates="parts")

class PartDescriptions(Base):
    __tablename__ = "part_descriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(225), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    made_in : Mapped[str] = mapped_column(String(200), nullable=False)
    # Relationship with parts
    parts : Mapped[list["Parts"]] = relationship("Parts", back_populates="part_description")
