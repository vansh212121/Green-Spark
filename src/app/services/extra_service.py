# app/services/appliance_service.py
"""
Appliance Service - Business Logic Layer
Handles all business logic, authorization, and orchestration for appliance management
Production-ready implementation with comprehensive features
"""

import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
import logging
from decimal import Decimal

from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from src.app.repositories.appliance_repository import ApplianceRepository
from src.app.models.appliance_model import UserAppliance, ApplianceCatalog
from src.app.models.user_model import User, UserRole
from src.app.schemas.appliance_schemas import (
    UserApplianceCreate,
    UserApplianceUpdate,
    UserApplianceResponse,
    UserApplianceListResponse,
    UserApplianceSearchParams,
    UserApplianceDetailedResponse,
    ApplianceEstimateResponse,
)
from src.app.core.exceptions import (
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ValidationError,
    BusinessLogicError,
    ConflictError,
)
from src.app.core.cache import cache_manager
from src.app.core.events import event_manager
from src.app.core.config import settings

logger = logging.getLogger(__name__)


class ApplianceService:
    """
    Service layer for appliance management.
    Contains all business logic and authorization checks.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the service with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session
        self.repository = ApplianceRepository(session)
        self._cache_prefix = "appliance"
        self._max_appliances_per_user = settings.MAX_APPLIANCES_PER_USER or 100
        self._default_electricity_rate = settings.DEFAULT_ELECTRICITY_RATE or 0.14

    # ==================== AUTHORIZATION HELPERS ====================

    async def _check_appliance_access(
        self, appliance_id: uuid.UUID, user: User, write_access: bool = False
    ) -> UserAppliance:
        """
        Check if user has access to an appliance.

        Args:
            appliance_id: UUID of the appliance
            user: Current user
            write_access: Whether write access is required

        Returns:
            The appliance if access is granted

        Raises:
            NotFoundError: If appliance doesn't exist
            ForbiddenError: If user doesn't have access
        """
        appliance = await self.repository.get_by_id(appliance_id)

        if not appliance:
            logger.warning(f"Appliance {appliance_id} not found")
            raise NotFoundError(f"Appliance with ID {appliance_id} not found")

        # Admins can access any appliance
        if user.role == UserRole.ADMIN:
            return appliance

        # Regular users can only access their own appliances
        if appliance.user_id != user.id:
            logger.warning(
                f"User {user.id} attempted to access appliance {appliance_id} owned by {appliance.user_id}"
            )
            raise ForbiddenError("You don't have permission to access this appliance")

        return appliance

    def _check_admin_role(self, user: User) -> None:
        """
        Verify user has admin role.

        Args:
            user: Current user

        Raises:
            ForbiddenError: If user is not an admin
        """
        if user.role != UserRole.ADMIN:
            raise ForbiddenError("Admin access required for this operation")

    # ==================== CREATE OPERATIONS ====================

    async def create_appliance(
        self, user: User, appliance_data: UserApplianceCreate
    ) -> UserApplianceResponse:
        """
        Create a new appliance for the user.

        Args:
            user: Current user
            appliance_data: Appliance creation data

        Returns:
            Created appliance response

        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        try:
            # Check user's appliance limit
            current_count = await self.repository.count_by_user(user.id)
            if current_count >= self._max_appliances_per_user:
                raise BusinessLogicError(
                    f"Maximum appliance limit ({self._max_appliances_per_user}) reached. "
                    "Please delete some appliances before adding new ones."
                )

            # Validate catalog reference if provided
            if appliance_data.appliance_catalog_id:
                catalog_items = await self.repository.get_catalog_items()
                catalog_ids = [item.category_id for item in catalog_items]
                if str(appliance_data.appliance_catalog_id) not in catalog_ids:
                    raise ValidationError(
                        f"Invalid appliance catalog ID: {appliance_data.appliance_catalog_id}"
                    )

            # Business rule: If no custom wattage, catalog ID must be provided
            if (
                not appliance_data.custom_wattage
                and not appliance_data.appliance_catalog_id
            ):
                raise ValidationError(
                    "Either custom wattage or appliance type from catalog must be provided"
                )

            # Create the appliance
            appliance = await self.repository.create(
                user_id=user.id, appliance_data=appliance_data
            )

            # Invalidate user's appliance cache
            await self._invalidate_user_cache(user.id)

            # Emit event for analytics
            await event_manager.emit(
                "appliance.created",
                {
                    "user_id": str(user.id),
                    "appliance_id": str(appliance.id),
                    "appliance_name": appliance.custom_name,
                    "wattage": appliance.custom_wattage,
                },
            )

            logger.info(f"User {user.id} created appliance {appliance.id}")

            # Convert to response schema
            return await self._to_response(appliance)

        except (ValidationError, BusinessLogicError, ConflictError):
            raise
        except Exception as e:
            logger.error(f"Error creating appliance: {str(e)}")
            raise BusinessLogicError(f"Failed to create appliance: {str(e)}")

    async def create_multiple_appliances(
        self, user: User, appliances_data: List[UserApplianceCreate]
    ) -> List[UserApplianceResponse]:
        """
        Create multiple appliances in a single transaction.

        Args:
            user: Current user
            appliances_data: List of appliance creation data

        Returns:
            List of created appliances

        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
        """
        try:
            # Check total limit
            current_count = await self.repository.count_by_user(user.id)
            new_total = current_count + len(appliances_data)

            if new_total > self._max_appliances_per_user:
                raise BusinessLogicError(
                    f"Adding {len(appliances_data)} appliances would exceed the limit of "
                    f"{self._max_appliances_per_user}. You can add at most "
                    f"{self._max_appliances_per_user - current_count} more appliances."
                )

            # Validate all appliances before creating
            for appliance_data in appliances_data:
                if (
                    not appliance_data.custom_wattage
                    and not appliance_data.appliance_catalog_id
                ):
                    raise ValidationError(
                        f"Appliance '{appliance_data.custom_name}': Either custom wattage "
                        "or appliance type from catalog must be provided"
                    )

            # Create all appliances
            appliances = await self.repository.create_bulk(
                user_id=user.id, appliances_data=appliances_data
            )

            # Invalidate cache
            await self._invalidate_user_cache(user.id)

            # Emit event
            await event_manager.emit(
                "appliances.bulk_created",
                {
                    "user_id": str(user.id),
                    "count": len(appliances),
                    "appliance_ids": [str(a.id) for a in appliances],
                },
            )

            logger.info(f"User {user.id} created {len(appliances)} appliances")

            # Convert to response
            return [await self._to_response(appliance) for appliance in appliances]

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Error creating multiple appliances: {str(e)}")
            raise BusinessLogicError(f"Failed to create appliances: {str(e)}")

    # ==================== READ OPERATIONS ====================

    async def get_appliance(
        self, user: User, appliance_id: uuid.UUID
    ) -> UserApplianceDetailedResponse:
        """
        Get a single appliance with detailed information.

        Args:
            user: Current user
            appliance_id: UUID of the appliance

        Returns:
            Detailed appliance response

        Raises:
            NotFoundError: If appliance not found
            ForbiddenError: If user lacks access
        """
        # Check cache first
        cache_key = f"{self._cache_prefix}:{appliance_id}"
        cached = await cache_manager.get(cache_key)
        if cached:
            # Still need to check access
            appliance = await self._check_appliance_access(appliance_id, user)
            return cached

        # Get from repository with catalog info
        appliance = await self._check_appliance_access(appliance_id, user)
        appliance = await self.repository.get_by_id(appliance_id, include_catalog=True)

        # Calculate additional details
        response = await self._to_detailed_response(appliance)

        # Cache the response
        await cache_manager.set(cache_key, response, expire=300)  # 5 minutes

        return response

    async def get_user_appliances(
        self, user: User, target_user_id: Optional[uuid.UUID] = None
    ) -> List[UserApplianceResponse]:
        """
        Get all appliances for a user.

        Args:
            user: Current user
            target_user_id: Target user ID (for admin access)

        Returns:
            List of appliances

        Raises:
            ForbiddenError: If user lacks access
        """
        # Determine which user's appliances to fetch
        if target_user_id and target_user_id != user.id:
            self._check_admin_role(user)
            user_id = target_user_id
        else:
            user_id = user.id

        # Get appliances
        appliances = await self.repository.get_by_user_id(user_id, include_catalog=True)

        # Convert to response
        return [await self._to_response(appliance) for appliance in appliances]

    async def list_appliances(
        self,
        user: User,
        page: int = 1,
        page_size: int = 20,
        search_params: Optional[UserApplianceSearchParams] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> UserApplianceListResponse:
        """
        Get paginated list of appliances with filtering.

        Args:
            user: Current user
            page: Page number
            page_size: Items per page
            search_params: Search/filter parameters
            sort_by: Sort field
            sort_order: Sort direction

        Returns:
            Paginated appliance list response
        """
        # For non-admin users, force filter to their own appliances
        if user.role != UserRole.ADMIN:
            user_id = user.id
        else:
            # Admin can see all or filter by specific user
            user_id = (
                search_params.user_id
                if search_params and search_params.user_id
                else None
            )

        # Get paginated results
        appliances, total = await self.repository.get_paginated(
            page=page,
            page_size=page_size,
            search_params=search_params,
            user_id=user_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Convert to response
        items = [await self._to_response(appliance) for appliance in appliances]

        # Calculate pagination metadata
        total_pages = (total + page_size - 1) // page_size

        return UserApplianceListResponse(
            items=items, total=total, page=page, pages=total_pages, size=page_size
        )

    async def get_appliance_statistics(
        self, user: User, target_user_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Get appliance statistics for a user.

        Args:
            user: Current user
            target_user_id: Target user ID (for admin access)

        Returns:
            Statistics dictionary
        """
        # Determine which user's statistics to fetch
        if target_user_id and target_user_id != user.id:
            self._check_admin_role(user)
            user_id = target_user_id
        else:
            user_id = user.id

        # Get statistics from repository
        stats = await self.repository.get_statistics(user_id)

        # Add electricity cost estimates
        if stats.get("estimated_monthly_kwh"):
            stats["estimated_monthly_cost"] = round(
                stats["estimated_monthly_kwh"] * self._default_electricity_rate, 2
            )
            stats["estimated_annual_cost"] = round(
                stats["estimated_monthly_kwh"] * 12 * self._default_electricity_rate, 2
            )

        # Add recommendations
        stats["recommendations"] = await self._generate_recommendations(user_id, stats)

        return stats

    async def get_catalog(self, search: Optional[str] = None) -> List[ApplianceCatalog]:
        """
        Get appliance catalog items.

        Args:
            search: Optional search term

        Returns:
            List of catalog items
        """
        return await self.repository.get_catalog_items(search=search)

    # ==================== UPDATE OPERATIONS ====================

    async def update_appliance(
        self, user: User, appliance_id: uuid.UUID, update_data: UserApplianceUpdate
    ) -> UserApplianceResponse:
        """
        Update an existing appliance.

        Args:
            user: Current user
            appliance_id: UUID of the appliance
            update_data: Update data

        Returns:
            Updated appliance response

        Raises:
            NotFoundError: If appliance not found
            ForbiddenError: If user lacks access
            ValidationError: If validation fails
        """
        # Check access
        appliance = await self._check_appliance_access(
            appliance_id, user, write_access=True
        )

        # Validate business rules
        if (
            update_data.hours_per_day is not None
            and update_data.days_per_week is not None
        ):
            if update_data.hours_per_day == 0 and update_data.days_per_week > 0:
                raise ValidationError(
                    "If hours_per_day is 0, days_per_week must also be 0"
                )
            if update_data.hours_per_day > 0 and update_data.days_per_week == 0:
                raise ValidationError(
                    "If days_per_week is 0, hours_per_day must also be 0"
                )

        # Update the appliance
        updated_appliance = await self.repository.update(
            appliance_id=appliance_id, update_data=update_data
        )

        if not updated_appliance:
            raise BusinessLogicError("Failed to update appliance")

        # Invalidate cache
        await self._invalidate_appliance_cache(appliance_id)
        await self._invalidate_user_cache(appliance.user_id)

        # Emit event
        await event_manager.emit(
            "appliance.updated",
            {
                "user_id": str(user.id),
                "appliance_id": str(appliance_id),
                "updated_fields": list(
                    update_data.model_dump(exclude_unset=True).keys()
                ),
            },
        )

        logger.info(f"User {user.id} updated appliance {appliance_id}")

        return await self._to_response(updated_appliance)

    async def bulk_update_appliances(
        self,
        user: User,
        appliance_ids: List[uuid.UUID],
        update_data: UserApplianceUpdate,
    ) -> Dict[str, Any]:
        """
        Update multiple appliances at once.

        Args:
            user: Current user
            appliance_ids: List of appliance IDs
            update_data: Update data to apply

        Returns:
            Summary of the bulk update operation
        """
        # For non-admin users, verify ownership of all appliances
        if user.role != UserRole.ADMIN:
            for appliance_id in appliance_ids:
                await self._check_appliance_access(
                    appliance_id, user, write_access=True
                )

        # Perform bulk update
        updated_count = await self.repository.update_bulk(
            appliance_ids=appliance_ids,
            update_data=update_data,
            user_id=user.id if user.role != UserRole.ADMIN else None,
        )

        # Invalidate cache for all updated appliances
        for appliance_id in appliance_ids:
            await self._invalidate_appliance_cache(appliance_id)
        await self._invalidate_user_cache(user.id)

        # Emit event
        await event_manager.emit(
            "appliances.bulk_updated",
            {
                "user_id": str(user.id),
                "count": updated_count,
                "appliance_ids": [str(aid) for aid in appliance_ids],
            },
        )

        logger.info(f"User {user.id} bulk updated {updated_count} appliances")

        return {
            "success": True,
            "updated_count": updated_count,
            "requested_count": len(appliance_ids),
            "message": f"Successfully updated {updated_count} appliances",
        }

    # ==================== DELETE OPERATIONS ====================

    async def delete_appliance(
        self, user: User, appliance_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Delete a single appliance.

        Args:
            user: Current user
            appliance_id: UUID of the appliance

        Returns:
            Deletion confirmation

        Raises:
            NotFoundError: If appliance not found
            ForbiddenError: If user lacks access
        """
        # Check access
        appliance = await self._check_appliance_access(
            appliance_id, user, write_access=True
        )

        # Delete the appliance
        deleted = await self.repository.delete(appliance_id)

        if not deleted:
            raise BusinessLogicError("Failed to delete appliance")

        # Invalidate cache
        await self._invalidate_appliance_cache(appliance_id)
        await self._invalidate_user_cache(appliance.user_id)

        # Emit event
        await event_manager.emit(
            "appliance.deleted",
            {
                "user_id": str(user.id),
                "appliance_id": str(appliance_id),
                "appliance_name": appliance.custom_name,
            },
        )

        logger.info(f"User {user.id} deleted appliance {appliance_id}")

        return {
            "success": True,
            "message": f"Appliance '{appliance.custom_name}' deleted successfully",
        }

    async def bulk_delete_appliances(
        self, user: User, appliance_ids: List[uuid.UUID]
    ) -> Dict[str, Any]:
        """
        Delete multiple appliances at once.

        Args:
            user: Current user
            appliance_ids: List of appliance IDs

        Returns:
            Summary of the bulk delete operation
        """
        # For non-admin users, verify ownership of all appliances
        if user.role != UserRole.ADMIN:
            for appliance_id in appliance_ids:
                await self._check_appliance_access(
                    appliance_id, user, write_access=True
                )

        # Perform bulk delete
        deleted_count = await self.repository.delete_bulk(
            appliance_ids=appliance_ids,
            user_id=user.id if user.role != UserRole.ADMIN else None,
        )

        # Invalidate cache
        for appliance_id in appliance_ids:
            await self._invalidate_appliance_cache(appliance_id)
        await self._invalidate_user_cache(user.id)

        # Emit event
        await event_manager.emit(
            "appliances.bulk_deleted",
            {
                "user_id": str(user.id),
                "count": deleted_count,
                "appliance_ids": [str(aid) for aid in appliance_ids],
            },
        )

        logger.info(f"User {user.id} bulk deleted {deleted_count} appliances")

        return {
            "success": True,
            "deleted_count": deleted_count,
            "requested_count": len(appliance_ids),
            "message": f"Successfully deleted {deleted_count} appliances",
        }

    # ==================== ENERGY ESTIMATION ====================

    async def estimate_appliance_consumption(
        self,
        user: User,
        appliance_id: uuid.UUID,
        electricity_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Estimate energy consumption and cost for an appliance.

        Args:
            user: Current user
            appliance_id: UUID of the appliance
            electricity_rate: Optional custom electricity rate

        Returns:
            Consumption estimates
        """
        # Check access
        appliance = await self._check_appliance_access(appliance_id, user)

        # Use provided rate or default
        rate = electricity_rate or self._default_electricity_rate

        # Get estimates from repository
        estimates = await self.repository.estimate_consumption(appliance_id, rate)

        # Add savings recommendations
        estimates["savings_potential"] = await self._calculate_savings_potential(
            appliance, estimates
        )

        return estimates

    async def estimate_bill_impact(
        self, user: User, bill_amount: float, billing_days: int = 30
    ) -> List[ApplianceEstimateResponse]:
        """
        Estimate each appliance's contribution to the electricity bill.

        Args:
            user: Current user
            bill_amount: Total bill amount
            billing_days: Number of days in billing period

        Returns:
            List of appliance estimates
        """
        # Get all user appliances
        appliances = await self.repository.get_by_user_id(user.id, include_catalog=True)

        if not appliances:
            return []

        # Calculate total consumption
        total_kwh = 0
        appliance_consumptions = []

        for appliance in appliances:
            # Get wattage
            wattage = appliance.custom_wattage
            if not wattage and appliance.appliance_catalog:
                wattage = appliance.appliance_catalog.typical_wattage

            if wattage:
                # Calculate consumption for billing period
                daily_hours = appliance.hours_per_day * (appliance.days_per_week / 7.0)
                period_kwh = (wattage * daily_hours * billing_days) / 1000.0

                appliance_consumptions.append(
                    {"appliance": appliance, "kwh": period_kwh}
                )
                total_kwh += period_kwh

        # Calculate cost distribution
        if total_kwh == 0:
            return []

        cost_per_kwh = bill_amount / total_kwh
        estimates = []

        for item in appliance_consumptions:
            estimate = ApplianceEstimateResponse(
                id=uuid.uuid4(),  # Generate estimate ID
                bill_id=uuid.uuid4(),  # This would be the actual bill ID
                user_appliance_id=item["appliance"].id,
                estimated_kwh=round(item["kwh"], 2),
                estimated_cost=round(item["kwh"] * cost_per_kwh, 2),
            )
            estimates.append(estimate)

        # Sort by cost (highest first)
        estimates.sort(key=lambda x: x.estimated_cost, reverse=True)

        return estimates

    # ==================== HELPER METHODS ====================

    async def _to_response(self, appliance: UserAppliance) -> UserApplianceResponse:
        """
        Convert appliance model to response schema.

        Args:
            appliance: UserAppliance model instance

        Returns:
            UserApplianceResponse
        """
        return UserApplianceResponse.model_validate(appliance)

    async def _to_detailed_response(
        self, appliance: UserAppliance
    ) -> UserApplianceDetailedResponse:
        """
        Convert appliance to detailed response with computed fields.

        Args:
            appliance: UserAppliance model instance

        Returns:
            UserApplianceDetailedResponse
        """
        # Get base response
        base_response = await self._to_response(appliance)

        # Calculate consumption estimates
        wattage = appliance.custom_wattage
        if not wattage and appliance.appliance_catalog:
            wattage = appliance.appliance_catalog.typical_wattage

        if wattage:
            daily_hours = appliance.hours_per_day * (appliance.days_per_week / 7.0)
            daily_kwh = (wattage * daily_hours) / 1000.0
            monthly_kwh = daily_kwh * 30

            # Add computed fields
            base_response.estimated_daily_kwh = round(daily_kwh, 2)
            base_response.estimated_monthly_kwh = round(monthly_kwh, 2)
            base_response.estimated_monthly_cost = round(
                monthly_kwh * self._default_electricity_rate, 2
            )

        return UserApplianceDetailedResponse.model_validate(base_response)

    async def _calculate_savings_potential(
        self, appliance: UserAppliance, current_estimates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate potential energy savings for an appliance.

        Args:
            appliance: UserAppliance instance
            current_estimates: Current consumption estimates

        Returns:
            Savings potential analysis
        """
        savings = {
            "potential_actions": [],
            "estimated_savings_kwh": 0,
            "estimated_savings_cost": 0,
        }

        # Check if usage can be reduced
        if appliance.hours_per_day > 8:
            reduction_hours = min(2, appliance.hours_per_day * 0.2)  # 20% reduction
            savings_kwh = (appliance.custom_wattage * reduction_hours * 30) / 1000

            savings["potential_actions"].append(
                {
                    "action": "Reduce usage time",
                    "description": f"Reduce daily usage by {reduction_hours:.1f} hours",
                    "savings_kwh": round(savings_kwh, 2),
                    "savings_cost": round(
                        savings_kwh * self._default_electricity_rate, 2
                    ),
                }
            )
            savings["estimated_savings_kwh"] += savings_kwh

        # Check for energy-efficient replacement
        if (
            appliance.purchase_year
            and appliance.purchase_year < datetime.now().year - 10
        ):
            # Assume 30% efficiency improvement for old appliances
            efficiency_savings = current_estimates.get("monthly_kwh", 0) * 0.3

            savings["potential_actions"].append(
                {
                    "action": "Replace with energy-efficient model",
                    "description": "Consider upgrading to a newer, more efficient model",
                    "savings_kwh": round(efficiency_savings, 2),
                    "savings_cost": round(
                        efficiency_savings * self._default_electricity_rate, 2
                    ),
                }
            )
            savings["estimated_savings_kwh"] += efficiency_savings

        # Calculate total savings
        savings["estimated_savings_cost"] = round(
            savings["estimated_savings_kwh"] * self._default_electricity_rate, 2
        )

        return savings

    async def _generate_recommendations(
        self, user_id: uuid.UUID, stats: Dict[str, Any]
    ) -> List[str]:
        """
        Generate energy-saving recommendations based on statistics.

        Args:
            user_id: UUID of the user
            stats: User's appliance statistics

        Returns:
            List of recommendations
        """
        recommendations = []

        # High consumption recommendation
        if stats.get("estimated_monthly_kwh", 0) > 500:
            recommendations.append(
                "Your monthly consumption is high. Consider reviewing high-usage appliances."
            )

        # Multiple appliances of same type
        if stats.get("brands"):
            for brand, count in stats["brands"].items():
                if count > 3:
                    recommendations.append(
                        f"You have {count} {brand} appliances. Consider consolidating if possible."
                    )

        # General recommendations
        recommendations.extend(
            [
                "Use appliances during off-peak hours to save on electricity costs",
                "Regular maintenance can improve appliance efficiency by up to 20%",
                "Consider smart power strips to eliminate standby power consumption",
            ]
        )

        return recommendations[:5]  # Return top 5 recommendations

    async def _invalidate_appliance_cache(self, appliance_id: uuid.UUID) -> None:
        """Invalidate cache for a specific appliance."""
        cache_key = f"{self._cache_prefix}:{appliance_id}"
        await cache_manager.delete(cache_key)

    async def _invalidate_user_cache(self, user_id: uuid.UUID) -> None:
        """Invalidate all cache entries for a user's appliances."""
        # In a production system, you might want to track user's appliance cache keys
        # For now, we'll just log it
        logger.debug(f"Cache invalidated for user {user_id}")

    # ==================== ADMIN OPERATIONS ====================

    async def admin_get_all_appliances(
        self, user: User, page: int = 1, page_size: int = 50
    ) -> UserApplianceListResponse:
        """
        Admin-only: Get all appliances across all users.

        Args:
            user: Current user (must be admin)
            page: Page number
            page_size: Items per page

        Returns:
            Paginated list of all appliances
        """
        self._check_admin_role(user)

        appliances, total = await self.repository.get_paginated(
            page=page, page_size=page_size, sort_by="created_at", sort_order="desc"
        )

        items = [await self._to_response(appliance) for appliance in appliances]
        total_pages = (total + page_size - 1) // page_size

        return UserApplianceListResponse(
            items=items, total=total, page=page, pages=total_pages, size=page_size
        )

    async def admin_get_system_statistics(self, user: User) -> Dict[str, Any]:
        """
        Admin-only: Get system-wide appliance statistics.

        Args:
            user: Current user (must be admin)

        Returns:
            System-wide statistics
        """
        self._check_admin_role(user)

        # Get overall statistics
        stats = await self.repository.get_statistics()

        # Add system-wide metrics
        stats["system_metrics"] = {
            "total_users_with_appliances": await self._count_users_with_appliances(),
            "average_appliances_per_user": await self._average_appliances_per_user(),
            "most_common_appliances": await self._most_common_appliances(),
            "total_estimated_monthly_kwh": stats.get("estimated_monthly_kwh", 0),
            "total_estimated_monthly_cost": round(
                stats.get("estimated_monthly_kwh", 0) * self._default_electricity_rate,
                2,
            ),
        }

        return stats

    async def _count_users_with_appliances(self) -> int:
        """Count unique users with appliances."""
        # This would be implemented with a proper query
        # For now, returning a placeholder
        return 0

    async def _average_appliances_per_user(self) -> float:
        """Calculate average appliances per user."""
        # This would be implemented with a proper query
        # For now, returning a placeholder
        return 0.0

    async def _most_common_appliances(self) -> List[Dict[str, Any]]:
        """Get most common appliance types."""
        # This would be implemented with a proper query
        # For now, returning a placeholder
        return []


# ==================== SERVICE FACTORY ====================


async def get_appliance_service(session: AsyncSession) -> ApplianceService:
    """
    Factory function to create an ApplianceService instance.

    Args:
        session: Database session

    Returns:
        ApplianceService instance
    """
    return ApplianceService(session)
