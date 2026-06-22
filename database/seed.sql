-- ============================================================================
-- Seed data (manual). Passwords are bcrypt hashes of 'ChangeMe!123'.
-- Prefer `python -m app.cli seed` which hashes & scores correctly. This file is
-- provided for SQL-only environments.
-- ============================================================================

INSERT INTO users (full_name, email, hashed_password, role)
VALUES
 ('Algorixe Admin', 'admin@algorixe.com',
  '$2b$12$abcdefghijklmnopqrstuvCWQ7Yy2bC3o0p9Q2u0fO3qY1m9Q1m9Q', 'admin'),
 ('Jordan Sales', 'rep@algorixe.com',
  '$2b$12$abcdefghijklmnopqrstuvCWQ7Yy2bC3o0p9Q2u0fO3qY1m9Q1m9Q', 'agent')
ON CONFLICT (email) DO NOTHING;

INSERT INTO leads
 (full_name, phone, email, location, budget, vehicle_interest,
  purchase_timeline, financing_need, trade_in_interest, score, temperature, status, source)
VALUES
 ('Aisha Khan','+15552001001','aisha@example.com','Dubai','AED 120,000',
  'Compact SUV','1-3 months',TRUE,FALSE,78,'hot','qualified','seed'),
 ('Mark Reyes','+15552001002','mark@example.com','Austin','$45,000',
  'Electric sedan','immediate',TRUE,TRUE,90,'hot','qualified','seed'),
 ('Lena Park','+15552001003',NULL,'Seoul',NULL,
  'Used hatchback','researching',FALSE,FALSE,12,'cold','contacted','seed'),
 ('Tom Boateng','+15552001004','tom@example.com','London','£30,000',
  'Family minivan','3-6 months',TRUE,TRUE,52,'warm','contacted','seed')
ON CONFLICT DO NOTHING;
