"""
Product Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.sql import func

from ..db.session import Base


class Product(Base):
	__tablename__ = "products"
	
	id = Column(Integer, primary_key=True, index=True)
	
	# Basic Information
	name = Column(String, nullable=False, index=True)
	version = Column(String, nullable=True, index=True)
	description = Column(Text, nullable=True)
	
	# Specifications and Metadata
	specs = Column(JSON, nullable=True)  # Arbitrary product specifications
	meta_data = Column(JSON, nullable=True)  # Additional structured info
	
	# State
	is_active = Column(Boolean, nullable=False, default=True, index=True)
	
	# Timestamps
	created_at = Column(DateTime(timezone=True), server_default=func.now())
	updated_at = Column(DateTime(timezone=True), onupdate=func.now())
	
	def __repr__(self):
		return f"<Product(id={self.id}, name={self.name}, version={self.version}, active={self.is_active})>"


