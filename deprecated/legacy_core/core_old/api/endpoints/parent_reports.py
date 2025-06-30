"""
📊 Parent Reports API Endpoint - Task 7
API للتقارير الوالدية مع تحليل التقدم المتقدم باستخدام NLP وLLM
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import services
from src.application.services.parent_report_service import ParentReportService

# ================ PYDANTIC MODELS ================

class ProgressAnalysisRequest(BaseModel):
    """Request model for progress analysis"""
    child_id: int = Field(..., description="Child's unique identifier")
    period_days: int = Field(7, description="Number of days to analyze", ge=1, le=30)

class ProgressMetricsResponse(BaseModel):
    """Response model for progress metrics"""
    child_id: int
    analysis_date: str
    total_unique_words: int
    new_words_this_period: List[str]
    vocabulary_complexity_score: float
    emotional_intelligence_score: float
    cognitive_development_score: float
    developmental_concerns: List[str]
    intervention_recommendations: List[str]
    urgency_level: int

class LLMRecommendationResponse(BaseModel):
    """Response model for LLM recommendations"""
    category: str
    recommendation: str
    reasoning: str
    implementation_steps: List[str]
    priority_level: int

class ParentReportResponse(BaseModel):
    """Complete parent report response"""
    report_id: str
    metrics: ProgressMetricsResponse
    recommendations: List[LLMRecommendationResponse]
    generated_at: str

class ReportListResponse(BaseModel):
    """Response for listing reports"""
    reports: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int

# ================ API ROUTER ================

router = APIRouter(prefix="/parent_reports", tags=["Parent Reports"])
logger = logging.getLogger(__name__)

# Initialize service (in production, this would use dependency injection)
report_service = ParentReportService()

# ================ API ENDPOINTS ================

@router.get(
    "/{child_id}",
    response_model=ParentReportResponse,
    summary="Get latest parent report for child",
    description="Generate or retrieve the latest progress analysis report for a child"
)
async def get_parent_report(
    child_id: int = Path(..., description="Child's unique identifier", ge=1),
    force_regenerate: bool = Query(False, description="Force generate new report even if recent one exists"),
    include_recommendations: bool = Query(True, description="Include LLM recommendations")
) -> ParentReportResponse:
    """
    Task 7: Get or generate parent report with advanced progress analysis
    
    Returns comprehensive analysis including:
    - NLP-based vocabulary analysis
    - Emotional intelligence assessment
    - Cognitive development metrics
    - LLM-generated personalized recommendations
    """
    try:
        logger.info(f"📊 Task 7: Generating parent report for child {child_id}")
        
        # Check if recent report exists (within last 24 hours)
        if not force_regenerate:
            recent_report = await _get_recent_report(child_id)
            if recent_report:
                logger.info(f"✅ Returning existing report for child {child_id}")
                return _format_report_response(recent_report)
        
        # Generate new comprehensive report using Task 7 methods
        report_data = await report_service.generate_and_store_report(child_id)
        
        # Format response
        response = ParentReportResponse(
            report_id=report_data['report_id'],
            metrics=ProgressMetricsResponse(**report_data['metrics']),
            recommendations=[
                LLMRecommendationResponse(**rec) 
                for rec in report_data['recommendations']
            ] if include_recommendations else [],
            generated_at=report_data['generated_at']
        )
        
        logger.info(f"✅ Task 7 report generated successfully for child {child_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to generate report for child {child_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate parent report: {str(e)}"
        )

@router.post(
    "/analyze",
    response_model=ProgressMetricsResponse,
    summary="Analyze child progress using advanced NLP",
    description="Perform advanced progress analysis using NLP and machine learning"
)
async def analyze_child_progress(
    request: ProgressAnalysisRequest
) -> ProgressMetricsResponse:
    """
    Task 7: Advanced progress analysis endpoint
    
    Performs:
    - NLP vocabulary analysis
    - Emotional intelligence assessment  
    - Cognitive development evaluation
    - Developmental concern identification
    """
    try:
        logger.info(f"🧠 Task 7: Analyzing progress for child {request.child_id}")
        
        # Perform advanced analysis
        metrics = await report_service.analyze_progress(request.child_id)
        
        # Convert to response model
        response = ProgressMetricsResponse(
            child_id=metrics.child_id,
            analysis_date=metrics.analysis_date.isoformat(),
            total_unique_words=metrics.total_unique_words,
            new_words_this_period=metrics.new_words_this_period,
            vocabulary_complexity_score=metrics.vocabulary_complexity_score,
            emotional_intelligence_score=metrics.emotional_intelligence_score,
            cognitive_development_score=metrics.cognitive_development_score,
            developmental_concerns=metrics.developmental_concerns,
            intervention_recommendations=metrics.intervention_recommendations,
            urgency_level=metrics.urgency_level
        )
        
        logger.info(f"✅ Progress analysis completed for child {request.child_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Progress analysis failed for child {request.child_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Progress analysis failed: {str(e)}"
        )

@router.get(
    "/{child_id}/recommendations",
    response_model=List[LLMRecommendationResponse],
    summary="Generate LLM recommendations",
    description="Generate personalized recommendations using LLM with Chain-of-Thought prompting"
)
async def generate_recommendations(
    child_id: int = Path(..., description="Child's unique identifier", ge=1)
) -> List[LLMRecommendationResponse]:
    """
    Task 7: Generate LLM recommendations with Chain-of-Thought prompting
    """
    try:
        logger.info(f"🤖 Task 7: Generating LLM recommendations for child {child_id}")
        
        # First analyze progress
        metrics = await report_service.analyze_progress(child_id)
        
        # Generate LLM recommendations
        recommendations = await report_service.generate_llm_recommendations(child_id, metrics)
        
        # Convert to response models
        response = [
            LLMRecommendationResponse(**rec) 
            for rec in recommendations
        ]
        
        logger.info(f"✅ Generated {len(response)} recommendations for child {child_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Recommendation generation failed for child {child_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation generation failed: {str(e)}"
        )

@router.get(
    "/{child_id}/history",
    response_model=ReportListResponse,
    summary="Get report history for child",
    description="Retrieve historical reports for a child with pagination"
)
async def get_report_history(
    child_id: int = Path(..., description="Child's unique identifier", ge=1),
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(10, description="Number of reports per page", ge=1, le=50),
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)")
) -> ReportListResponse:
    """
    Get historical reports for a child with filtering and pagination
    """
    try:
        logger.info(f"📋 Getting report history for child {child_id}")
        
        # Get historical reports (this would query the database in production)
        reports = await _get_historical_reports(
            child_id, page, page_size, start_date, end_date
        )
        
        response = ReportListResponse(
            reports=reports['reports'],
            total_count=reports['total_count'],
            page=page,
            page_size=page_size
        )
        
        logger.info(f"✅ Retrieved {len(reports['reports'])} reports for child {child_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to get report history for child {child_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get report history: {str(e)}"
        )

@router.delete(
    "/{child_id}/reports/{report_id}",
    summary="Delete a specific report",
    description="Delete a specific report by ID"
)
async def delete_report(
    child_id: int = Path(..., description="Child's unique identifier", ge=1),
    report_id: str = Path(..., description="Report ID to delete")
) -> JSONResponse:
    """
    Delete a specific report
    """
    try:
        logger.info(f"🗑️ Deleting report {report_id} for child {child_id}")
        
        # Delete report (this would delete from database in production)
        success = await _delete_report(child_id, report_id)
        
        if success:
            logger.info(f"✅ Report {report_id} deleted successfully")
            return JSONResponse(
                content={"message": "Report deleted successfully"},
                status_code=200
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )
        
    except Exception as e:
        logger.error(f"❌ Failed to delete report {report_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete report: {str(e)}"
        )

@router.get(
    "/health",
    summary="Health check for parent reports service",
    description="Check if the parent reports service is healthy"
)
async def health_check() -> JSONResponse:
    """
    Health check endpoint for the parent reports service
    """
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "parent_reports",
            "version": "Task7_v1.0",
            "features": {
                "nlp_analysis": True,
                "llm_recommendations": True,
                "chain_of_thought": True,
                "progress_tracking": True
            }
        }
        
        return JSONResponse(content=health_status, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=503
        )

# ================ HELPER FUNCTIONS ================

async def _get_recent_report(child_id: int) -> Optional[Dict[str, Any]]:
    """Check if a recent report exists (within last 24 hours)"""
    try:
        # In production, this would query the database
        # For now, return None to always generate new reports
        return None
    except Exception as e:
        logger.error(f"Failed to check for recent report: {e}")
        return None

async def _get_historical_reports(
    child_id: int, 
    page: int, 
    page_size: int,
    start_date: Optional[str],
    end_date: Optional[str]
) -> Dict[str, Any]:
    """Get historical reports with pagination and filtering"""
    try:
        # In production, this would query the parent_reports table
        # For now, return mock data
        mock_reports = [
            {
                "report_id": f"task7_{child_id}_20241201_120000",
                "generated_at": "2024-12-01T12:00:00Z",
                "urgency_level": 1,
                "total_unique_words": 25,
                "vocabulary_complexity_score": 0.6
            },
            {
                "report_id": f"task7_{child_id}_20241128_120000", 
                "generated_at": "2024-11-28T12:00:00Z",
                "urgency_level": 0,
                "total_unique_words": 22,
                "vocabulary_complexity_score": 0.55
            }
        ]
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_reports = mock_reports[start_idx:end_idx]
        
        return {
            "reports": paginated_reports,
            "total_count": len(mock_reports)
        }
        
    except Exception as e:
        logger.error(f"Failed to get historical reports: {e}")
        return {"reports": [], "total_count": 0}

async def _delete_report(child_id: int, report_id: str) -> bool:
    """Delete a specific report"""
    try:
        # In production, this would delete from the database
        # For now, simulate successful deletion
        logger.info(f"Simulating deletion of report {report_id} for child {child_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete report: {e}")
        return False

def _format_report_response(report_data: Dict[str, Any]) -> ParentReportResponse:
    """Format database report data into API response"""
    return ParentReportResponse(
        report_id=report_data.get('report_id', ''),
        metrics=ProgressMetricsResponse(**report_data.get('metrics', {})),
        recommendations=[
            LLMRecommendationResponse(**rec) 
            for rec in report_data.get('recommendations', [])
        ],
        generated_at=report_data.get('generated_at', datetime.now().isoformat())
    )

# ================ EXAMPLE USAGE ================

async def test_endpoints():
    """Example usage of the parent reports endpoints"""
    
    # Test progress analysis
    print("🧠 Testing progress analysis...")
    request = ProgressAnalysisRequest(child_id=123, period_days=7)
    metrics = await analyze_child_progress(request)
    print(f"✅ Analysis completed: {metrics.total_unique_words} unique words")
    
    # Test recommendation generation
    print("🤖 Testing LLM recommendations...")
    recommendations = await generate_recommendations(123)
    print(f"✅ Generated {len(recommendations)} recommendations")
    
    # Test full report generation
    print("📊 Testing full report generation...")
    report = await get_parent_report(123)
    print(f"✅ Report generated with ID: {report.report_id}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_endpoints()) 