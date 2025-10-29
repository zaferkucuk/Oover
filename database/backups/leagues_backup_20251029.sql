-- =====================================================
-- LEAGUES TABLE BACKUP
-- =====================================================
-- Created: 2025-10-29
-- Purpose: Pre-migration backup for Leagues Feature (Phase 1.1)
-- Total Records: 19 leagues
-- Source: Supabase (Oover Project)
-- =====================================================

-- IMPORTANT NOTES:
-- 1. This backup was created BEFORE any schema changes
-- 2. Current schema already uses snake_case convention
-- 3. No camelCase fields found (sportId, externalId, etc.)
-- 4. No deprecated fields found (season, country)
-- 5. All foreign keys (sport_id, country_id) are in place
-- =====================================================

-- Current Schema (Pre-Migration):
-- 
-- CREATE TABLE leagues (
--   id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
--   sport_id        uuid NOT NULL REFERENCES sports(id),
--   external_id     text,
--   name            text NOT NULL,
--   country_id      uuid REFERENCES countries(id),
--   logo            text,
--   is_active       boolean DEFAULT true,
--   created_at      timestamp DEFAULT CURRENT_TIMESTAMP,
--   updated_at      timestamp
-- );

-- =====================================================
-- DATA BACKUP (19 Leagues)
-- =====================================================

-- Restore command (if needed):
-- DELETE FROM leagues WHERE id IN (...);
-- Then run the INSERT statements below

-- TURKEY (2 leagues)
INSERT INTO leagues (id, sport_id, name, logo, external_id, is_active, created_at, updated_at, country_id)
VALUES 
('43071579-6b7a-4999-a882-f50e6dfc1f63', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Süper Lig', NULL, 'api-football-203', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'facbfb4f-b6c2-4122-bc7e-866323fe6b53'),
('fba6eac1-c425-4a23-88b9-0fff4328106c', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', '1. Lig', NULL, 'api-football-204', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'facbfb4f-b6c2-4122-bc7e-866323fe6b53');

-- GERMANY (2 leagues)
INSERT INTO leagues (id, sport_id, name, logo, external_id, is_active, created_at, updated_at, country_id)
VALUES 
('63b405c6-49cc-4c66-b7ab-20e32d5b461c', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Bundesliga', NULL, 'bl-78', true, '2025-10-26 23:18:11.825', '2025-10-26 23:18:11.825', 'fe36c45a-bcfb-48cc-9ff1-654f680cee78'),
('28156e3d-2181-44ef-868b-b4acb5e87bc1', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', '2. Bundesliga', NULL, 'api-football-79', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'fe36c45a-bcfb-48cc-9ff1-654f680cee78');

-- BELGIUM (2 leagues)
INSERT INTO leagues (id, sport_id, name, logo, external_id, is_active, created_at, updated_at, country_id)
VALUES 
('b3e40141-3506-4c0a-a1ff-8b09462d81d0', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Pro League', NULL, 'api-football-144', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'b234d01f-b588-42f0-8d1f-1d5503712466'),
('4057d55a-8d37-4a16-be51-7813a453c8de', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Challenger Pro League', NULL, 'api-football-145', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'b234d01f-b588-42f0-8d1f-1d5503712466');

-- ENGLAND (2 leagues)
INSERT INTO leagues (id, sport_id, name, logo, external_id, is_active, created_at, updated_at, country_id)
VALUES 
('8afd5fc0-4279-47ab-b0cf-f79141f2afd6', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Premier League', NULL, 'pl-39', true, '2025-10-26 23:18:11.466', '2025-10-26 23:18:11.466', 'e704f41b-9e0d-4ad6-996d-96ab528700df'),
('ee8b02e0-4863-40ed-9e27-4f9231f0bf07', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Championship', NULL, 'api-football-40', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'e704f41b-9e0d-4ad6-996d-96ab528700df');

-- CZECH REPUBLIC (1 league)
INSERT INTO leagues (id, sport_id, name, logo, external_id, is_active, created_at, updated_at, country_id)
VALUES 
('68810bc3-c4fe-4157-a55d-51632901561b', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Czech First League', NULL, 'api-football-345', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'ca465f61-59d6-4cd0-a192-6c0e52e5eccc');

-- NETHERLANDS (2 leagues)
INSERT INTO leagues (id, sport_id, name, logo, external_id, is_active, created_at, updated_at, country_id)
VALUES 
('8da51d29-8414-4e30-b847-c9a044b47f47', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Eredivisie', NULL, 'api-football-88', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', '395c9781-1426-4cca-8549-7921d46babf1'),
('63fff8b8-36e6-4ba7-8da7-8ac36c280728', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Eerste Divisie', NULL, 'api-football-89', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', '395c9781-1426-4cca-8549-7921d46babf1');

-- SPAIN (2 leagues)
INSERT INTO leagues (id, sport_id, name, logo, external_id, is_active, created_at, updated_at, country_id)
VALUES 
('e9d7682e-1984-49ed-b0eb-bed28dc1f022', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'La Liga', NULL, 'll-140', true, '2025-10-26 23:18:11.696', '2025-10-26 23:18:11.696', 'c78ede2f-927e-4b47-97b3-4c2e848a4397'),
('cc61412d-4aa6-48ad-9ad4-e297d22c24bd', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'La Liga 2', NULL, 'api-football-141', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'c78ede2f-927e-4b47-97b3-4c2e848a4397');

-- PORTUGAL (2 leagues)
INSERT INTO leagues (id, sport_id, name, logo, external_id, is_active, created_at, updated_at, country_id)
VALUES 
('fde5bc2d-8205-4c62-be92-bd72dc1cf1e4', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Primeira Liga', NULL, 'api-football-94', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'b9fc4192-72e0-432b-acee-48e8b387060e'),
('6cd7ded8-7a2d-48c7-9241-35159287a085', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Liga Portugal 2', NULL, 'api-football-95', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'b9fc4192-72e0-432b-acee-48e8b387060e');

-- FRANCE (2 leagues)
INSERT INTO leagues (id, sport_id, name, logo, external_id, is_active, created_at, updated_at, country_id)
VALUES 
('bf23b295-774b-4be8-a546-38b4eefa2a0b', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Ligue 1', NULL, 'api-football-61', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', '75c93599-e069-4e28-ad69-f3eecf07eddf'),
('8ded45b5-bec6-4847-ac10-1476d54d352e', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Ligue 2', NULL, 'api-football-62', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', '75c93599-e069-4e28-ad69-f3eecf07eddf');

-- ITALY (2 leagues)
INSERT INTO leagues (id, sport_id, name, logo, external_id, is_active, created_at, updated_at, country_id)
VALUES 
('569c2b9d-a023-46f6-ba77-4253df41ecae', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Serie A', NULL, 'api-football-135', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'd172b53a-2bcb-47ff-b4f9-3bf20283eccf'),
('e93b9c49-8d52-4eb6-a8cf-bf76e21a348a', '8dd8ec3b-9d8a-4066-ab33-86fae63cab0a', 'Serie B', NULL, 'api-football-136', true, '2025-10-29 10:59:52.1', '2025-10-29 10:59:52.1', 'd172b53a-2bcb-47ff-b4f9-3bf20283eccf');

-- =====================================================
-- VERIFICATION QUERY
-- =====================================================
-- Run this to verify the backup:
-- SELECT COUNT(*) FROM leagues; -- Should return 19

-- =====================================================
-- BACKUP SUMMARY
-- =====================================================
-- Total Leagues: 19
-- Countries: 10
-- Distribution:
--   - Turkey: 2 (Süper Lig, 1. Lig)
--   - Germany: 2 (Bundesliga, 2. Bundesliga)
--   - Belgium: 2 (Pro League, Challenger Pro League)
--   - England: 2 (Premier League, Championship)
--   - Netherlands: 2 (Eredivisie, Eerste Divisie)
--   - Spain: 2 (La Liga, La Liga 2)
--   - Portugal: 2 (Primeira Liga, Liga Portugal 2)
--   - France: 2 (Ligue 1, Ligue 2)
--   - Italy: 2 (Serie A, Serie B)
--   - Czech Republic: 1 (Czech First League)
-- =====================================================

-- END OF BACKUP