"""
Uber Eats Reports endpoints
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date

from app.core.config import settings
from app.db.session import get_db
from app.schemas.reports import (
    Report,
    ReportList,
    ReportRequest,
    ScheduledReport,
    ReportType,
    ReportFormat,
    ReportStatus,
    SalesSummary,
    ItemPerformance,
    CustomerInsights,
    DeliveryPerformance,
    FinancialSummary,
)
from app.schemas.base import BaseResponse
from app.services.uber_eats import UberEatsReportService
from app.api.dependencies.auth import get_uber_eats_token

router = APIRouter()


@router.post("/generate", response_model=Report)
async def generate_report(
    report_request: ReportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Report:
    """
    Generate a new report
    
    Initiates report generation. Report will be processed asynchronously.
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        report = await report_service.generate_report(report_request)
        
        # Process report generation in background
        background_tasks.add_task(
            report_service.process_report_generation,
            report.id
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


@router.get("/", response_model=ReportList)
async def list_reports(
    report_type: Optional[ReportType] = None,
    status: Optional[ReportStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> ReportList:
    """
    List generated reports
    
    Returns list of previously generated reports with filtering options
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        reports = await report_service.list_reports(
            report_type=report_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return reports
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reports: {str(e)}",
        )


@router.get("/{report_id}", response_model=Report)
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Report:
    """
    Get report details
    
    Returns report metadata and download URL if ready
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        report = await report_service.get_report(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found",
            )
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch report: {str(e)}",
        )


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> Dict[str, Any]:
    """
    Get report download URL
    
    Returns a temporary download URL for the report file
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        download_info = await report_service.get_report_download_url(report_id)
        if not download_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Download not available for report {report_id}",
            )
        return download_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get download URL: {str(e)}",
        )


@router.delete("/{report_id}", response_model=BaseResponse)
async def delete_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> BaseResponse:
    """
    Delete a report
    
    Removes report and associated data
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        success = await report_service.delete_report(report_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found",
            )
        
        return BaseResponse(
            success=True,
            message=f"Report {report_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete report: {str(e)}",
        )


@router.get("/sales/summary", response_model=SalesSummary)
async def get_sales_summary(
    store_id: str,
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> SalesSummary:
    """
    Get sales summary
    
    Returns aggregated sales data for the specified period
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        summary = await report_service.get_sales_summary(
            store_id=store_id,
            start_date=start_date,
            end_date=end_date,
        )
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sales summary: {str(e)}",
        )


@router.get("/items/performance", response_model=List[ItemPerformance])
async def get_item_performance(
    store_id: str,
    start_date: date,
    end_date: date,
    category_id: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> List[ItemPerformance]:
    """
    Get item performance metrics
    
    Returns performance data for menu items
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        performance = await report_service.get_item_performance(
            store_id=store_id,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            limit=limit,
        )
        return performance
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch item performance: {str(e)}",
        )


@router.get("/customers/insights", response_model=CustomerInsights)
async def get_customer_insights(
    store_id: str,
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> CustomerInsights:
    """
    Get customer insights
    
    Returns customer behavior and demographics data
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        insights = await report_service.get_customer_insights(
            store_id=store_id,
            start_date=start_date,
            end_date=end_date,
        )
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch customer insights: {str(e)}",
        )


@router.get("/financial/summary", response_model=FinancialSummary)
async def get_financial_summary(
    store_id: str,
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> FinancialSummary:
    """
    Get financial summary
    
    Returns detailed financial breakdown including fees and payouts
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        summary = await report_service.get_financial_summary(
            store_id=store_id,
            start_date=start_date,
            end_date=end_date,
        )
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch financial summary: {str(e)}",
        )


@router.post("/scheduled", response_model=ScheduledReport)
async def create_scheduled_report(
    scheduled_report: ScheduledReport,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> ScheduledReport:
    """
    Create a scheduled report
    
    Sets up automatic report generation on a schedule
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        scheduled = await report_service.create_scheduled_report(scheduled_report)
        return scheduled
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scheduled report: {str(e)}",
        )


@router.get("/scheduled", response_model=List[ScheduledReport])
async def list_scheduled_reports(
    store_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> List[ScheduledReport]:
    """
    List scheduled reports
    
    Returns all configured scheduled reports
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        scheduled_reports = await report_service.list_scheduled_reports(
            store_id=store_id,
            is_active=is_active,
        )
        return scheduled_reports
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch scheduled reports: {str(e)}",
        )


@router.delete("/scheduled/{scheduled_report_id}", response_model=BaseResponse)
async def delete_scheduled_report(
    scheduled_report_id: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_uber_eats_token),
) -> BaseResponse:
    """
    Delete a scheduled report
    
    Removes scheduled report configuration
    """
    report_service = UberEatsReportService(db, token)
    
    try:
        success = await report_service.delete_scheduled_report(scheduled_report_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheduled report {scheduled_report_id} not found",
            )
        
        return BaseResponse(
            success=True,
            message=f"Scheduled report {scheduled_report_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scheduled report: {str(e)}",
        )