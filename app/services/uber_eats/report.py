"""
Uber Eats Reporting Service
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.services.uber_eats.base import UberEatsBaseService
from app.schemas.reports import (
    SalesReport,
    OrderReport,
    MenuPerformanceReport,
    StorePerformanceReport,
    ReportPeriod,
    ReportFormat,
)

logger = structlog.get_logger()


class UberEatsReportService(UberEatsBaseService):
    """Service for generating Uber Eats reports and analytics"""
    
    def __init__(self, db: AsyncSession, access_token: str):
        super().__init__(db, access_token)
    
    async def get_sales_report(
        self,
        store_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: ReportPeriod = ReportPeriod.DAILY,
    ) -> Optional[SalesReport]:
        """
        Get sales report for specified period
        
        Uber Eats API: GET /v1/eats/reports/sales
        """
        try:
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "period": period.value,
            }
            
            if store_id:
                params["store_id"] = store_id
            
            response_data = await self.get("/v1/eats/reports/sales", params=params)
            return SalesReport(**response_data)
            
        except Exception as e:
            logger.error("Failed to get sales report", store_id=store_id, error=str(e))
            return None
    
    async def get_order_report(
        self,
        store_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_cancelled: bool = False,
    ) -> Optional[OrderReport]:
        """
        Get detailed order report
        
        Uber Eats API: GET /v1/eats/reports/orders
        """
        try:
            # Default to last 7 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()
            
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "include_cancelled": include_cancelled,
            }
            
            if store_id:
                params["store_id"] = store_id
            
            response_data = await self.get("/v1/eats/reports/orders", params=params)
            return OrderReport(**response_data)
            
        except Exception as e:
            logger.error("Failed to get order report", store_id=store_id, error=str(e))
            return None
    
    async def get_menu_performance_report(
        self,
        store_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[MenuPerformanceReport]:
        """
        Get menu item performance report
        
        Uber Eats API: GET /v1/eats/reports/menu_performance
        """
        try:
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            params = {
                "store_id": store_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            }
            
            response_data = await self.get("/v1/eats/reports/menu_performance", params=params)
            return MenuPerformanceReport(**response_data)
            
        except Exception as e:
            logger.error("Failed to get menu performance report", store_id=store_id, error=str(e))
            return None
    
    async def get_store_performance_report(
        self,
        store_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[StorePerformanceReport]:
        """
        Get comprehensive store performance report
        
        Uber Eats API: GET /v1/eats/reports/store_performance
        """
        try:
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            params = {
                "store_id": store_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            }
            
            response_data = await self.get("/v1/eats/reports/store_performance", params=params)
            return StorePerformanceReport(**response_data)
            
        except Exception as e:
            logger.error("Failed to get store performance report", store_id=store_id, error=str(e))
            return None
    
    async def get_financial_summary(
        self,
        store_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get financial summary including revenue, fees, and payouts
        
        Uber Eats API: GET /v1/eats/reports/financial_summary
        """
        try:
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            }
            
            if store_id:
                params["store_id"] = store_id
            
            return await self.get("/v1/eats/reports/financial_summary", params=params)
            
        except Exception as e:
            logger.error("Failed to get financial summary", store_id=store_id, error=str(e))
            return {}
    
    async def get_customer_insights(
        self,
        store_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get customer behavior insights
        
        Uber Eats API: GET /v1/eats/reports/customer_insights
        """
        try:
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            params = {
                "store_id": store_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            }
            
            return await self.get("/v1/eats/reports/customer_insights", params=params)
            
        except Exception as e:
            logger.error("Failed to get customer insights", store_id=store_id, error=str(e))
            return {}
    
    async def get_operational_metrics(
        self,
        store_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get operational metrics like prep times, acceptance rates
        
        Uber Eats API: GET /v1/eats/reports/operational_metrics
        """
        try:
            # Default to last 7 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()
            
            params = {
                "store_id": store_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            }
            
            return await self.get("/v1/eats/reports/operational_metrics", params=params)
            
        except Exception as e:
            logger.error("Failed to get operational metrics", store_id=store_id, error=str(e))
            return {}
    
    async def export_report(
        self,
        report_type: str,
        store_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: ReportFormat = ReportFormat.CSV,
    ) -> Optional[str]:
        """
        Export report in specified format
        
        Uber Eats API: POST /v1/eats/reports/export
        """
        try:
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            payload = {
                "report_type": report_type,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "format": format.value,
            }
            
            if store_id:
                payload["store_id"] = store_id
            
            response_data = await self.post("/v1/eats/reports/export", data=payload)
            return response_data.get("download_url")
            
        except Exception as e:
            logger.error("Failed to export report", report_type=report_type, error=str(e))
            return None
    
    async def get_peak_hours_analysis(
        self,
        store_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get peak hours analysis for better staffing decisions
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            end_date = datetime.utcnow()
            
            params = {
                "store_id": store_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "analysis_type": "peak_hours",
            }
            
            return await self.get("/v1/eats/reports/analysis", params=params)
            
        except Exception as e:
            logger.error("Failed to get peak hours analysis", store_id=store_id, error=str(e))
            return {}
    
    async def get_competitor_analysis(
        self,
        store_id: str,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get competitor analysis and market positioning
        
        Uber Eats API: GET /v1/eats/reports/competitor_analysis
        """
        try:
            params = {
                "store_id": store_id,
            }
            
            if category:
                params["category"] = category
            
            return await self.get("/v1/eats/reports/competitor_analysis", params=params)
            
        except Exception as e:
            logger.error("Failed to get competitor analysis", store_id=store_id, error=str(e))
            return {}
    
    async def get_delivery_performance(
        self,
        store_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get delivery performance metrics
        
        Uber Eats API: GET /v1/eats/reports/delivery_performance
        """
        try:
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            params = {
                "store_id": store_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            }
            
            return await self.get("/v1/eats/reports/delivery_performance", params=params)
            
        except Exception as e:
            logger.error("Failed to get delivery performance", store_id=store_id, error=str(e))
            return {}
    
    async def get_promotion_effectiveness(
        self,
        store_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get promotion and discount effectiveness report
        
        Uber Eats API: GET /v1/eats/reports/promotion_effectiveness
        """
        try:
            # Default to last 60 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=60)
            if not end_date:
                end_date = datetime.utcnow()
            
            params = {
                "store_id": store_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            }
            
            return await self.get("/v1/eats/reports/promotion_effectiveness", params=params)
            
        except Exception as e:
            logger.error("Failed to get promotion effectiveness", store_id=store_id, error=str(e))
            return {}
    
    # Convenience methods for common reporting needs
    
    async def get_daily_summary(self, store_id: str, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get daily summary report for a specific date"""
        if not date:
            date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        start_date = date
        end_date = date + timedelta(days=1)
        
        sales_report = await self.get_sales_report(store_id, start_date, end_date)
        order_report = await self.get_order_report(store_id, start_date, end_date)
        
        return {
            "date": date.isoformat(),
            "sales": sales_report.model_dump() if sales_report else {},
            "orders": order_report.model_dump() if order_report else {},
        }
    
    async def get_weekly_summary(self, store_id: str) -> Dict[str, Any]:
        """Get weekly summary for the last 7 days"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        sales_report = await self.get_sales_report(store_id, start_date, end_date, ReportPeriod.WEEKLY)
        order_report = await self.get_order_report(store_id, start_date, end_date)
        menu_report = await self.get_menu_performance_report(store_id, start_date, end_date)
        
        return {
            "period": "last_7_days",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "sales": sales_report.model_dump() if sales_report else {},
            "orders": order_report.model_dump() if order_report else {},
            "menu_performance": menu_report.model_dump() if menu_report else {},
        }
    
    async def get_monthly_summary(self, store_id: str) -> Dict[str, Any]:
        """Get monthly summary for the last 30 days"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        sales_report = await self.get_sales_report(store_id, start_date, end_date, ReportPeriod.MONTHLY)
        store_performance = await self.get_store_performance_report(store_id, start_date, end_date)
        financial_summary = await self.get_financial_summary(store_id, start_date, end_date)
        
        return {
            "period": "last_30_days",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "sales": sales_report.model_dump() if sales_report else {},
            "performance": store_performance.model_dump() if store_performance else {},
            "financial": financial_summary,
        }