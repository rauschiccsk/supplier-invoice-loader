# -*- coding: utf-8 -*-
"""
L&Š Invoice Loader - Pydantic Models
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InvoiceRequest(BaseModel):
    """Request model pre príjem faktúry z n8n"""
    file_b64: str = Field(..., description="PDF súbor v base64")
    filename: Optional[str] = Field("invoice.pdf", description="Názov súboru")
    message_id: Optional[str] = Field(None, description="Gmail message ID")
    gmail_id: Optional[str] = Field(None, description="Gmail thread ID")
    from_email: Optional[str] = Field(None, alias="from", description="Email odosielateľa")
    subject: Optional[str] = Field(None, description="Predmet emailu")
    received_date: Optional[str] = Field(None, description="Dátum prijatia")

    class Config:
        populate_by_name = True  # Allow both 'from' and 'from_email'


class InvoiceResponse(BaseModel):
    """Response model pre API"""
    status: str = Field(..., description="success alebo error")
    message: str = Field(..., description="Správa")
    invoice_id: Optional[int] = Field(None, description="ID faktúry v DB")
    duplicate: bool = Field(False, description="Či je faktúra duplicitná")
    pdf_path: Optional[str] = Field(None, description="Cesta k PDF súboru")
    xml_path: Optional[str] = Field(None, description="Cesta k XML súboru (budúcnosť)")


class HealthResponse(BaseModel):
    """Response model pre health check"""
    status: str
    timestamp: str
    storage_ok: bool
    database_ok: bool
