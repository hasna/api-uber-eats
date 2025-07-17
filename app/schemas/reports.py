"""
Reports-related schemas for Uber Eats API
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from enum import Enum


class ReportType(str, Enum):
    """Report type enumeration"""
    SALES_SUMMARY = "SALES_SUMMARY"
    ORDER_DETAILS = "ORDER_DETAILS"
    ITEM_PERFORMANCE = "ITEM_PERFORMANCE"
    CUSTOMER_INSIGHTS = "CUSTOMER_INSIGHTS"
    DELIVERY_PERFORMANCE = "DELIVERY_PERFORMANCE"
    FINANCIAL_SUMMARY = "FINANCIAL_SUMMARY"
    TAX_REPORT = "TAX_REPORT"
    COMMISSION_REPORT = "COMMISSION_REPORT"
    REFUND_REPORT = "REFUND_REPORT"
    CUSTOM = "CUSTOM"


class ReportFormat(str, Enum):
    """Report output format"""
    CSV = "CSV"
    EXCEL = "EXCEL"
    PDF = "PDF"
    JSON = "JSON"


class ReportFrequency(str, Enum):
    """Report generation frequency"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class DateRange(BaseModel):
    """Date range for reports"""
    start_date: date = Field(description="Start date")
    end_date: date = Field(description="End date")
    
    model_config = ConfigDict(from_attributes=True)


class ReportFilters(BaseModel):
    """Report filtering options"""
    store_ids: Optional[List[str]] = Field(default=None, description="Filter by store IDs")
    order_types: Optional[List[str]] = Field(default=None, description="Filter by order types")
    payment_methods: Optional[List[str]] = Field(default=None, description="Filter by payment methods")
    min_order_value: Optional[float] = Field(default=None, description="Minimum order value")
    max_order_value: Optional[float] = Field(default=None, description="Maximum order value")
    include_cancelled: bool = Field(default=False, description="Include cancelled orders")
    include_refunds: bool = Field(default=True, description="Include refunded orders")
    
    model_config = ConfigDict(from_attributes=True)


class ReportRequest(BaseModel):
    """Report generation request"""
    report_type: ReportType = Field(description="Type of report")
    date_range: DateRange = Field(description="Date range for report")
    format: ReportFormat = Field(default=ReportFormat.CSV, description="Output format")
    filters: Optional[ReportFilters] = Field(default=None, description="Report filters")
    include_details: bool = Field(default=True, description="Include detailed data")
    timezone: str = Field(default="UTC", description="Timezone for report data")
    
    model_config = ConfigDict(from_attributes=True)


class ScheduledReport(ReportRequest):
    """Scheduled report configuration"""
    frequency: ReportFrequency = Field(description="Report frequency")
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6, description="Day of week (0=Monday)")
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31, description="Day of month")
    time_of_day: str = Field(description="Time of day (HH:MM)")
    email_recipients: List[str] = Field(description="Email recipients")
    is_active: bool = Field(default=True, description="Whether schedule is active")
    
    model_config = ConfigDict(from_attributes=True)


class Report(BaseModel):
    """Generated report schema"""
    id: str = Field(description="Report ID")
    report_type: ReportType = Field(description="Type of report")
    status: ReportStatus = Field(description="Report status")
    date_range: DateRange = Field(description="Date range covered")
    format: ReportFormat = Field(description="Output format")
    file_size_bytes: Optional[int] = Field(default=None, description="File size in bytes")
    download_url: Optional[HttpUrl] = Field(default=None, description="Download URL")
    expires_at: Optional[datetime] = Field(default=None, description="URL expiration time")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(description="Creation timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class SalesSummary(BaseModel):
    """Sales summary data"""
    total_revenue: float = Field(description="Total revenue")
    total_orders: int = Field(description="Total number of orders")
    average_order_value: float = Field(description="Average order value")
    total_items_sold: int = Field(description="Total items sold")
    top_selling_items: List[Dict[str, Any]] = Field(description="Top selling items")
    revenue_by_hour: Dict[int, float] = Field(description="Revenue by hour of day")
    revenue_by_day: Dict[str, float] = Field(description="Revenue by day of week")
    
    model_config = ConfigDict(from_attributes=True)


class ItemPerformance(BaseModel):
    """Item performance metrics"""
    item_id: str = Field(description="Item ID")
    item_name: str = Field(description="Item name")
    category: str = Field(description="Item category")
    quantity_sold: int = Field(description="Quantity sold")
    revenue: float = Field(description="Total revenue")
    average_price: float = Field(description="Average selling price")
    popularity_rank: int = Field(description="Popularity ranking")
    return_rate: float = Field(description="Return/refund rate")
    
    model_config = ConfigDict(from_attributes=True)


class CustomerInsights(BaseModel):
    """Customer insights data"""
    total_customers: int = Field(description="Total unique customers")
    new_customers: int = Field(description="New customers")
    returning_customers: int = Field(description="Returning customers")
    average_order_frequency: float = Field(description="Average orders per customer")
    customer_lifetime_value: float = Field(description="Average customer lifetime value")
    top_customers: List[Dict[str, Any]] = Field(description="Top customers by revenue")
    
    model_config = ConfigDict(from_attributes=True)


class DeliveryPerformance(BaseModel):
    """Delivery performance metrics"""
    total_deliveries: int = Field(description="Total deliveries")
    average_delivery_time: float = Field(description="Average delivery time in minutes")
    on_time_rate: float = Field(description="On-time delivery rate")
    customer_satisfaction_rate: float = Field(description="Customer satisfaction rate")
    delivery_issues: List[Dict[str, Any]] = Field(description="Common delivery issues")
    
    model_config = ConfigDict(from_attributes=True)


class FinancialSummary(BaseModel):
    """Financial summary report"""
    gross_sales: float = Field(description="Gross sales")
    net_sales: float = Field(description="Net sales after refunds")
    taxes_collected: float = Field(description="Total taxes collected")
    uber_commission: float = Field(description="Uber commission fees")
    delivery_fees: float = Field(description="Delivery fees")
    tips: float = Field(description="Total tips")
    refunds: float = Field(description="Total refunds")
    net_payout: float = Field(description="Net payout amount")
    
    model_config = ConfigDict(from_attributes=True)


class ReportList(BaseModel):
    """List of reports"""
    reports: List[Report] = Field(description="List of reports")
    total: int = Field(description="Total number of reports")
    has_more: bool = Field(description="Whether there are more reports")
    next_cursor: Optional[str] = Field(default=None, description="Cursor for next page")
    
    model_config = ConfigDict(from_attributes=True)