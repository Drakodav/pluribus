-- Immich Database Extension Initialization SQL
-- Reference: https://docs.immich.app/administration/postgres-standalone/

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS cube;
CREATE EXTENSION IF NOT EXISTS earthdistance;
CREATE EXTENSION IF NOT EXISTS vector;
