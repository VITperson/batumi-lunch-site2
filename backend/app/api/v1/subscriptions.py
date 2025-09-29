from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.deps import get_session
from ...db.models.subscriptions import Subscription
from ..v1.schemas import SubscriptionOut

router = APIRouter()


@router.get("/", response_model=list[SubscriptionOut])
async def list_subscriptions(session: AsyncSession = Depends(get_session)) -> list[SubscriptionOut]:
    result = await session.execute(select(Subscription))
    items = result.scalars().all()
    return [
        SubscriptionOut(
            id=sub.id,
            status=sub.status.value,
            next_charge_at=sub.next_charge_at,
            pause_until=sub.pause_until,
            settings=sub.settings,
        )
        for sub in items
    ]
