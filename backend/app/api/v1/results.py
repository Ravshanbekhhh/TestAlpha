"""
Results endpoints - submitting and retrieving test results.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.database import get_db
from app.schemas.result import ResultSubmit, ResultResponse, UserResultSummary, MCQAnswerResponse, WrittenAnswerResponse
from app.services.session_service import get_session_by_token, mark_session_submitted
from app.services.grading_service import grade_and_save_result, get_user_results
from app.models.result import Result, MCQAnswer, WrittenAnswer
from app.models.test import Test


router = APIRouter()


@router.post("/submit", response_model=ResultResponse, status_code=status.HTTP_201_CREATED)
async def submit_test(
    submission: ResultSubmit,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit test answers for grading.
    MCQ answers are auto-graded, written answers stored for manual review.
    Idempotent: if already submitted, returns existing result.
    """
    # Get session
    session = await get_session_by_token(db, submission.session_token)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # If already submitted, return existing result instead of error
    if session.is_submitted:
        stmt = select(Result).where(Result.session_id == session.id)
        existing = await db.execute(stmt)
        existing_result = existing.scalars().first()
        
        if existing_result:
            # Load answers for existing result
            stmt = select(MCQAnswer).where(MCQAnswer.result_id == existing_result.id)
            mcq_result = await db.execute(stmt)
            mcq_answers_list = mcq_result.scalars().all()
            
            stmt = select(WrittenAnswer).where(WrittenAnswer.result_id == existing_result.id)
            written_result = await db.execute(stmt)
            written_answers_list = written_result.scalars().all()
            
            return ResultResponse(
                id=existing_result.id,
                user_id=existing_result.user_id,
                test_id=existing_result.test_id,
                mcq_score=existing_result.mcq_score,
                written_score=existing_result.written_score,
                total_score=existing_result.total_score,
                submitted_at=existing_result.submitted_at,
                mcq_answers=[MCQAnswerResponse.model_validate(a) for a in mcq_answers_list],
                written_answers=[WrittenAnswerResponse.model_validate(a) for a in written_answers_list]
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test already submitted but result not found"
        )
    
    # Note: we don't block expired sessions from submitting
    # because the timer auto-submits right when/after the session expires
    
    # Grade and save result
    try:
        result = await grade_and_save_result(db, session, submission)
        
        # Mark session as submitted
        await mark_session_submitted(db, session.id)
        
        # Load MCQ answers and written answers with explicit queries (avoid lazy loading)
        stmt = select(MCQAnswer).where(MCQAnswer.result_id == result.id)
        mcq_result = await db.execute(stmt)
        mcq_answers_list = mcq_result.scalars().all()
        
        stmt = select(WrittenAnswer).where(WrittenAnswer.result_id == result.id)
        written_result = await db.execute(stmt)
        written_answers_list = written_result.scalars().all()
        
        # Build response manually to avoid lazy loading issues
        return ResultResponse(
            id=result.id,
            user_id=result.user_id,
            test_id=result.test_id,
            mcq_score=result.mcq_score,
            written_score=result.written_score,
            total_score=result.total_score,
            submitted_at=result.submitted_at,
            mcq_answers=[MCQAnswerResponse.model_validate(a) for a in mcq_answers_list],
            written_answers=[WrittenAnswerResponse.model_validate(a) for a in written_answers_list]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[UserResultSummary])
async def get_user_results_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all results for a user (for Telegram bot).
    """
    results = await get_user_results(db, user_id)
    
    # Build summaries with test info
    summaries = []
    for result in results:
        stmt = select(Test).where(Test.id == result.test_id)
        test_result = await db.execute(stmt)
        test = test_result.scalars().first()
        
        summaries.append(UserResultSummary(
            test_title=test.title if test else "Unknown Test",
            test_code=test.test_code if test else "",
            mcq_score=result.mcq_score,
            written_score=result.written_score,
            total_score=result.total_score,
            submitted_at=result.submitted_at
        ))
    
    return summaries


@router.get("/{result_id}", response_model=ResultResponse)
async def get_result(
    result_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed result by ID.
    """
    stmt = select(Result).where(Result.id == result_id)
    result = await db.execute(stmt)
    result_record = result.scalars().first()
    
    if not result_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found"
        )
    
    # Load relationships
    stmt = select(MCQAnswer).where(MCQAnswer.result_id == result_id)
    mcq_result = await db.execute(stmt)
    result_record.mcq_answers = mcq_result.scalars().all()
    
    stmt = select(WrittenAnswer).where(WrittenAnswer.result_id == result_id)
    written_result = await db.execute(stmt)
    result_record.written_answers = written_result.scalars().all()
    
    return ResultResponse.model_validate(result_record)
