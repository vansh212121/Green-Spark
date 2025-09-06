import logging
import uuid
from typing import Dict
from fastapi import APIRouter, Depends, status, Query, File, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.db.session import get_session
from src.app.models.user_model import User
from src.app.services.bill_service import bill_service
from src.app.schemas.bill_schema import (
    BillUploadRequest,
    BillUploadResponse,
    BillConfirmRequest,
    BillResponse,
    BillDetailedResponse,
    BillListResponse,
    BillSearchParams,
)
from src.app.utils.deps import (
    get_current_verified_user,
    get_pagination_params,
    PaginationParams,
    require_user,
    require_admin,
    rate_limit_api,
)

# --NEW IMPORTS---
from src.app.core.config import settings
import boto3

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Bills"],
    prefix="/bills",
)


@router.get(
    "/all",
    response_model=BillListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all bills",
    description="Get a paginated and filterable list of all bills.",
    dependencies=[
        Depends(require_admin),
        Depends(rate_limit_api),
    ],  # Simplified the auth check
)
async def get_all_bills(
    *,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
    pagination: PaginationParams = Depends(get_pagination_params),
    search_params: BillSearchParams = Depends(BillSearchParams),
    order_by: str = Query("created_at", description="Field to order by"),
    order_desc: bool = Query(True, description="Order descending"),
):
    """Get all User's with pagination and filtering support"""

    return await bill_service.get_user_bills(
        db=db,
        skip=pagination.skip,
        user_id=current_user.id,
        limit=pagination.limit,
        order_by=order_by,
        order_desc=order_desc,
        filters=search_params.model_dump(exclude_none=True),
    )


@router.get(
    "/{bill_id}",
    status_code=status.HTTP_200_OK,
    response_model=BillDetailedResponse,
    summary="Get bill by id",
    description="Get all information for the bill by id",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def get_bill_by_id(
    *,
    bill_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """Get Bill by it's ID"""

    return await bill_service.get_bill_by_id(
        db=db,
        current_user=current_user,
        bill_id=bill_id,
    )


@router.delete(
    "/{bill_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],
    summary="Delete bill by id",
    description="Delete all information for the bill by id",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def delete_bill(
    *,
    bill_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """Delete a bill by it's ID"""

    await bill_service.delete_bill(
        db=db, bill_id_to_delete=bill_id, current_user=current_user
    )

    return {"message": "Bill deleted successfully"}


@router.post(
    "/upload",
    response_model=BillUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a bill",
    description="Upload a bill by its Filename",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def request_upload_url(
    *,
    upload_request: BillUploadRequest,
    current_user: User = Depends(get_current_verified_user),
):
    """Get a secure presigned URL to upload a bill PDF."""
    # This call is now correct because the service function accepts the parameter.
    return bill_service.create_upload_url(
        user=current_user,
        filename=upload_request.filename,
        content_type=upload_request.content_type,
    )


@router.post(
    "/confirm",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=BillResponse,
    summary="Confirm a bill",
    description="confirm a bill upload",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def confirm_bill_upload(
    *,
    db: AsyncSession = Depends(get_session),
    confirm_data: BillConfirmRequest,
    current_user: User = Depends(get_current_verified_user),
):
    """Confirm a file upload is complete and start the async parsing task."""
    return await bill_service.confirm_upload_and_start_parsing(
        db=db, user=current_user, confirm_data=confirm_data
    )


@router.post(
    "/bills/{bill_id}/estimate",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=Dict[str, str],
    summary="Trigger the bill estimation task",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def trigger_bill_estimation(
    *,
    db: AsyncSession = Depends(get_session),
    bill_id: uuid.UUID,
    current_user: User = Depends(get_current_verified_user),
):
    """Manually trigger the appliance estimation task for a bill."""
    await bill_service.trigger_estimation_for_bill(
        db=db, bill_id=bill_id, current_user=current_user
    )
    return {"message": "Appliance estimation has been queued."}


@router.post(
    "/direct-upload",
    status_code=status.HTTP_200_OK,
    summary="Directly upload file to S3 (testing only)",
    description="Upload a file to MinIO/S3 and return the file_uri for use in /confirm."
)
async def direct_upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_verified_user),
):
    # 1. Init boto3 client (direct, not via s3_service)
    s3_client = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
    )
    bucket_name = settings.S3_BUCKET_NAME

    # 2. Generate object key
    object_key = f"{current_user.id}/{uuid.uuid4()}-{file.filename}"

    # 3. Upload file directly to S3
    s3_client.upload_fileobj(file.file, bucket_name, object_key)

    # 4. Build file_uri (same format your confirm API expects)
    file_uri = f"s3://{bucket_name}/{object_key}"

    return {"file_uri": file_uri}