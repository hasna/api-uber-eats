"""Integration tests for database operations."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import uuid

from app.db.session import engine
from app.db.base import Base
from app.db.models.auth import AuthToken
from app.db.models.store import Store, StoreStatus
from app.db.models.user import User


@pytest.fixture
async def db_session():
    """Create a test database session."""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with AsyncSession(engine) as session:
        yield session
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_auth_token_crud(db_session):
    """Test CRUD operations for AuthToken."""
    # Create
    token = AuthToken(
        access_token="test_token_123",
        refresh_token="refresh_token_123",
        token_type="Bearer",
        scope="eats.store eats.order",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        is_active=True
    )
    
    db_session.add(token)
    await db_session.commit()
    await db_session.refresh(token)
    
    assert token.id is not None
    assert token.access_token == "test_token_123"
    assert token.is_active is True
    
    # Read
    from sqlalchemy import select
    stmt = select(AuthToken).where(AuthToken.access_token == "test_token_123")
    result = await db_session.execute(stmt)
    retrieved_token = result.scalar_one()
    
    assert retrieved_token.id == token.id
    assert retrieved_token.refresh_token == "refresh_token_123"
    
    # Update
    retrieved_token.is_active = False
    await db_session.commit()
    
    stmt = select(AuthToken).where(AuthToken.id == token.id)
    result = await db_session.execute(stmt)
    updated_token = result.scalar_one()
    
    assert updated_token.is_active is False
    
    # Delete
    await db_session.delete(updated_token)
    await db_session.commit()
    
    stmt = select(AuthToken).where(AuthToken.id == token.id)
    result = await db_session.execute(stmt)
    deleted_token = result.scalar_one_or_none()
    
    assert deleted_token is None


@pytest.mark.asyncio
async def test_store_crud(db_session):
    """Test CRUD operations for Store."""
    # Create
    store = Store(
        uber_eats_id="store_123",
        name="Test Restaurant",
        address="123 Test Street",
        phone_number="555-1234",
        status=StoreStatus.ONLINE,
        latitude=40.7128,
        longitude=-74.0060,
        hours={
            "monday": {"open": "09:00", "close": "22:00"},
            "tuesday": {"open": "09:00", "close": "22:00"}
        }
    )
    
    db_session.add(store)
    await db_session.commit()
    await db_session.refresh(store)
    
    assert store.id is not None
    assert store.uber_eats_id == "store_123"
    assert store.name == "Test Restaurant"
    assert store.status == StoreStatus.ONLINE
    
    # Read
    from sqlalchemy import select
    stmt = select(Store).where(Store.uber_eats_id == "store_123")
    result = await db_session.execute(stmt)
    retrieved_store = result.scalar_one()
    
    assert retrieved_store.id == store.id
    assert retrieved_store.latitude == 40.7128
    assert retrieved_store.longitude == -74.0060
    assert "monday" in retrieved_store.hours
    
    # Update
    retrieved_store.status = StoreStatus.OFFLINE
    retrieved_store.phone_number = "555-5678"
    await db_session.commit()
    
    stmt = select(Store).where(Store.id == store.id)
    result = await db_session.execute(stmt)
    updated_store = result.scalar_one()
    
    assert updated_store.status == StoreStatus.OFFLINE
    assert updated_store.phone_number == "555-5678"
    
    # Delete
    await db_session.delete(updated_store)
    await db_session.commit()
    
    stmt = select(Store).where(Store.id == store.id)
    result = await db_session.execute(stmt)
    deleted_store = result.scalar_one_or_none()
    
    assert deleted_store is None


@pytest.mark.asyncio
async def test_user_crud(db_session):
    """Test CRUD operations for User."""
    # Create
    user = User(
        uber_eats_id="user_123",
        email="test@example.com",
        name="Test User",
        is_active=True,
        roles=["restaurant_owner"]
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    assert user.id is not None
    assert user.uber_eats_id == "user_123"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert "restaurant_owner" in user.roles
    
    # Read
    from sqlalchemy import select
    stmt = select(User).where(User.email == "test@example.com")
    result = await db_session.execute(stmt)
    retrieved_user = result.scalar_one()
    
    assert retrieved_user.id == user.id
    assert retrieved_user.name == "Test User"
    
    # Update
    retrieved_user.name = "Updated User"
    retrieved_user.is_active = False
    await db_session.commit()
    
    stmt = select(User).where(User.id == user.id)
    result = await db_session.execute(stmt)
    updated_user = result.scalar_one()
    
    assert updated_user.name == "Updated User"
    assert updated_user.is_active is False
    
    # Delete
    await db_session.delete(updated_user)
    await db_session.commit()
    
    stmt = select(User).where(User.id == user.id)
    result = await db_session.execute(stmt)
    deleted_user = result.scalar_one_or_none()
    
    assert deleted_user is None


@pytest.mark.asyncio
async def test_relationships(db_session):
    """Test relationships between models."""
    # Create user
    user = User(
        uber_eats_id="user_123",
        email="owner@example.com",
        name="Store Owner",
        is_active=True,
        roles=["restaurant_owner"]
    )
    
    # Create store
    store = Store(
        uber_eats_id="store_123",
        name="Test Restaurant",
        address="123 Test Street",
        phone_number="555-1234",
        status=StoreStatus.ONLINE,
        latitude=40.7128,
        longitude=-74.0060,
        hours={}
    )
    
    # Associate user with store
    user.stores.append(store)
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(store)
    
    # Test relationship
    assert len(user.stores) == 1
    assert user.stores[0].id == store.id
    assert store.owner_id == user.id


@pytest.mark.asyncio
async def test_token_expiration_query(db_session):
    """Test querying tokens by expiration status."""
    # Create expired token
    expired_token = AuthToken(
        access_token="expired_token",
        token_type="Bearer",
        scope="eats.store",
        expires_at=datetime.utcnow() - timedelta(hours=1),
        is_active=True
    )
    
    # Create valid token
    valid_token = AuthToken(
        access_token="valid_token",
        token_type="Bearer",
        scope="eats.store",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        is_active=True
    )
    
    db_session.add(expired_token)
    db_session.add(valid_token)
    await db_session.commit()
    
    # Query for valid tokens
    from sqlalchemy import select
    stmt = select(AuthToken).where(
        AuthToken.is_active == True,
        AuthToken.expires_at > datetime.utcnow()
    )
    result = await db_session.execute(stmt)
    valid_tokens = result.scalars().all()
    
    assert len(valid_tokens) == 1
    assert valid_tokens[0].access_token == "valid_token"
    
    # Query for expired tokens
    stmt = select(AuthToken).where(
        AuthToken.expires_at <= datetime.utcnow()
    )
    result = await db_session.execute(stmt)
    expired_tokens = result.scalars().all()
    
    assert len(expired_tokens) == 1
    assert expired_tokens[0].access_token == "expired_token"


@pytest.mark.asyncio
async def test_store_status_filtering(db_session):
    """Test filtering stores by status."""
    # Create stores with different statuses
    online_store = Store(
        uber_eats_id="store_online",
        name="Online Store",
        address="123 Online St",
        phone_number="555-1111",
        status=StoreStatus.ONLINE,
        latitude=40.7128,
        longitude=-74.0060,
        hours={}
    )
    
    offline_store = Store(
        uber_eats_id="store_offline",
        name="Offline Store",
        address="456 Offline Ave",
        phone_number="555-2222",
        status=StoreStatus.OFFLINE,
        latitude=40.7589,
        longitude=-73.9851,
        hours={}
    )
    
    paused_store = Store(
        uber_eats_id="store_paused",
        name="Paused Store",
        address="789 Paused Blvd",
        phone_number="555-3333",
        status=StoreStatus.PAUSED,
        latitude=40.7829,
        longitude=-73.9654,
        hours={}
    )
    
    db_session.add(online_store)
    db_session.add(offline_store)
    db_session.add(paused_store)
    await db_session.commit()
    
    # Query online stores
    from sqlalchemy import select
    stmt = select(Store).where(Store.status == StoreStatus.ONLINE)
    result = await db_session.execute(stmt)
    online_stores = result.scalars().all()
    
    assert len(online_stores) == 1
    assert online_stores[0].name == "Online Store"
    
    # Query offline stores
    stmt = select(Store).where(Store.status == StoreStatus.OFFLINE)
    result = await db_session.execute(stmt)
    offline_stores = result.scalars().all()
    
    assert len(offline_stores) == 1
    assert offline_stores[0].name == "Offline Store"
    
    # Query active stores (online + paused)
    stmt = select(Store).where(Store.status.in_([StoreStatus.ONLINE, StoreStatus.PAUSED]))
    result = await db_session.execute(stmt)
    active_stores = result.scalars().all()
    
    assert len(active_stores) == 2
    store_names = [store.name for store in active_stores]
    assert "Online Store" in store_names
    assert "Paused Store" in store_names


@pytest.mark.asyncio
async def test_json_field_operations(db_session):
    """Test JSON field operations."""
    # Create store with complex hours
    store = Store(
        uber_eats_id="json_test_store",
        name="JSON Test Store",
        address="123 JSON St",
        phone_number="555-9999",
        status=StoreStatus.ONLINE,
        latitude=40.7128,
        longitude=-74.0060,
        hours={
            "monday": {"open": "09:00", "close": "22:00", "closed": False},
            "tuesday": {"open": "09:00", "close": "22:00", "closed": False},
            "wednesday": {"open": "09:00", "close": "22:00", "closed": False},
            "thursday": {"open": "09:00", "close": "22:00", "closed": False},
            "friday": {"open": "09:00", "close": "23:00", "closed": False},
            "saturday": {"open": "10:00", "close": "23:00", "closed": False},
            "sunday": {"open": "10:00", "close": "21:00", "closed": False}
        }
    )
    
    db_session.add(store)
    await db_session.commit()
    await db_session.refresh(store)
    
    # Verify JSON data is stored and retrieved correctly
    assert store.hours["monday"]["open"] == "09:00"
    assert store.hours["friday"]["close"] == "23:00"
    assert store.hours["sunday"]["closed"] is False
    
    # Update JSON field
    store.hours["monday"]["closed"] = True
    store.hours["saturday"]["open"] = "11:00"
    await db_session.commit()
    
    # Verify updates
    from sqlalchemy import select
    stmt = select(Store).where(Store.id == store.id)
    result = await db_session.execute(stmt)
    updated_store = result.scalar_one()
    
    assert updated_store.hours["monday"]["closed"] is True
    assert updated_store.hours["saturday"]["open"] == "11:00"
    assert updated_store.hours["friday"]["close"] == "23:00"  # Unchanged