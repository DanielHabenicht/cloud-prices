from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class PricePoint(Base):
    __tablename__ = "azure_price_points"

    id: Mapped[int] = mapped_column(primary_key=True)
    # All prices are in USD so we do not nead to persist it
    # curreny_code: Mapped[str] = mapped_column(String(3))
    tier_minimum_units: Mapped[float]
    retail_price: Mapped[float]
    unit_price: Mapped[float]
    effective_start_date: Mapped[datetime]
    
    ## TODO
    unit_of_measure: Mapped[str]
    is_primary: Mapped[bool]
    reservations: Mapped[Optional[str]]
    import_date: Mapped[datetime]

    consumption_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("azure_consumption_types.id"), index=True)
    consumption_type: Mapped["Type"] = relationship(back_populates="price_points")

    meter_id: Mapped[Optional[int]] = mapped_column(ForeignKey("azure_meters.id"), index=True)
    meter: Mapped["Meter"] = relationship(back_populates="price_points")

    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey("azure_regions.id"), index=True)
    region: Mapped["Region"] = relationship(back_populates="price_points")

    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("azure_locations.id"), index=True)
    location: Mapped["Location"] = relationship(back_populates="price_points")

    product_id: Mapped[Optional[str]] = mapped_column(ForeignKey("azure_products.id"), index=True)
    product: Mapped["Product"] = relationship(back_populates="price_points")

    # sku: Mapped[str] = mapped_column(ForeignKey("azure_sku.id"))
    # sku: Mapped["Sku"] = relationship(back_populates="azure_sku")

    service_id: Mapped[Optional[str]] = mapped_column(ForeignKey("azure_services.id"), index=True)
    service: Mapped["Service"] = relationship(back_populates="price_points")


    def __repr__(self) -> str:
        return f"PricePoint(id={self.id!r})"


class Type(Base):
    __tablename__ = "azure_consumption_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price_points: Mapped[List["PricePoint"]] = relationship(
        back_populates="consumption_type", cascade="all, delete-orphan"
    )

class Meter(Base):
    __tablename__ = "azure_meters"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    price_points: Mapped[List["PricePoint"]] = relationship(
        back_populates="meter", cascade="all, delete-orphan"
    )

class Region(Base):
    __tablename__ = "azure_regions"
    id: Mapped[int] = mapped_column(primary_key=True)
    arm_name: Mapped[str]
    price_points: Mapped[List["PricePoint"]] = relationship(
        back_populates="region", cascade="all, delete-orphan"
    )

class Location(Base):
    __tablename__ = "azure_locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price_points: Mapped[List["PricePoint"]] = relationship(
        back_populates="location", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "azure_products"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    price_points: Mapped[List["PricePoint"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Product(id={self.id!r})"
    
class Sku(Base):
    __tablename__ = "azure_skus"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    def __repr__(self) -> str:
        return f"Sku(id={self.id!r})"
    
class Service(Base):
    __tablename__ = "azure_services"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    # TODO:
    family: Mapped[Optional[str]] = mapped_column(String(30))

    price_points: Mapped[List["PricePoint"]] = relationship(
        back_populates="service", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Service(id={self.id!r})"