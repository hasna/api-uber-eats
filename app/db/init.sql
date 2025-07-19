-- Initial database setup for Uber Eats API

-- Create UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE store_status AS ENUM ('ONLINE', 'OFFLINE', 'PAUSED', 'INACTIVE');
CREATE TYPE order_status AS ENUM ('PENDING', 'ACCEPTED', 'DENIED', 'PREPARING', 'READY_FOR_PICKUP', 'DISPATCHED', 'DELIVERED', 'CANCELLED', 'FAILED');
CREATE TYPE order_type AS ENUM ('DELIVERY', 'PICKUP', 'DINE_IN');
CREATE TYPE webhook_status AS ENUM ('PENDING', 'PROCESSING', 'PROCESSED', 'FAILED', 'RETRYING');

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE uber_eats_db TO uber_eats_user;
GRANT ALL ON SCHEMA public TO uber_eats_user;