-- Seed Data for Loop Factory AI
-- Run this after creating the schema

-- Insert 11 Companies
INSERT INTO companies (name, domain, industry, description, target_market, status) VALUES
('Loop Factory AI', 'loopfactory.ai', 'AI Automation', 'AI Agent Marketplace powering industry automation', 'General Business', 'active'),
('KoiKeeper AI', 'koikeeper.ai', 'Koi Pond Management', 'AI-powered koi pond management and care', 'Koi Enthusiasts', 'active'),
('FishKeeper AI', 'fishkeeper.ai', 'Aquarium Management', 'AI-powered aquarium management and care', 'Aquarium Owners', 'active'),
('LandLaw AI', 'landlaw.ai', 'Property Legal', 'AI-powered property and landlord legal assistance', 'Property Owners', 'active'),
('Social Media Mananger AI', 'socialmediamananger.ai', 'Social Media', 'AI-powered social media management and automation', 'Businesses', 'active'),
('MuckAway AI', 'muckaway.ai', 'Waste Management', 'AI-powered waste management and logistics', 'Waste Companies', 'active'),
('GrabHire AI', 'grabhire.ai', 'Equipment Rental', 'AI-powered equipment rental management', 'Rental Companies', 'active'),
('PlantHire AI', 'planthire.ai', 'Plant Rental', 'AI-powered plant and equipment hire management', 'Construction', 'active'),
('DIYHelp AI', 'diyhelp.ai', 'DIY & Home Improvement', 'AI-powered DIY and home improvement assistance', 'Homeowners', 'active'),
('PokerHUD AI', 'pokerhud.ai', 'Poker Analytics', 'AI-powered poker analytics and HUD', 'Poker Players', 'active'),
('CommercialVehicle AI', 'commercialvehicle.ai', 'Fleet Management', 'AI-powered commercial vehicle and fleet management', 'Fleet Operators', 'active');

-- Insert Sample Agent (from approved loops)
INSERT INTO agents (
  name, slug, description, category, pricing_model, price_usd, 
  company_id, is_featured, is_active, rating_average, rating_count
) VALUES (
  'KoiKeeper Water Quality Monitor',
  'koikeeper-water-quality-monitor',
  'AI-powered water quality monitoring for koi ponds. Automatically tracks pH, temperature, ammonia, and other critical parameters. Sends alerts when values are out of range.',
  'koi_management',
  'subscription',
  29.00,
  (SELECT id FROM companies WHERE domain = 'koikeeper.ai'),
  true,
  true,
  4.8,
  127
);

-- Insert Sample Blog Posts
INSERT INTO blog_posts (
  company_id, title, slug, excerpt, content, author_name, 
  seo_title, seo_description, keywords, status
) VALUES
(
  (SELECT id FROM companies WHERE domain = 'koikeeper.ai'),
  'The Ultimate Guide to Koi Pond Water Quality',
  'ultimate-guide-koi-pond-water-quality',
  'Learn everything you need to know about maintaining perfect water quality in your koi pond',
  '# The Ultimate Guide to Koi Pond Water Quality\n\nMaintaining optimal water quality is crucial for healthy koi...',
  'AI Assistant',
  'Koi Pond Water Quality Guide - KoiKeeper AI',
  'Complete guide to maintaining perfect water quality in your koi pond. Learn about pH, ammonia, nitrites, and more.',
  ARRAY['koi pond', 'water quality', 'koi care', 'pond maintenance'],
  'published'
);

-- Insert Sample Social Media Posts
INSERT INTO social_media_posts (
  company_id, platform, content, hashtags, post_type, status, scheduled_for
) VALUES
(
  (SELECT id FROM companies WHERE domain = 'koikeeper.ai'),
  'twitter',
  'Did you know? Koi can live for over 200 years with proper care! 🐟 Start monitoring your pond water quality with AI today.',
  ARRAY['koi', 'koipond'],
  'tip',
  'scheduled',
  NOW() + INTERVAL '1 day'
),
(
  (SELECT id FROM companies WHERE domain = 'koikeeper.ai'),
  'linkedin',
  'Introducing AI-powered water quality monitoring for koi ponds. Never worry about water parameters again. Get instant alerts when something is wrong.',
  ARRAY['AI', 'automation', 'koi'],
  'promotion',
  'scheduled',
  NOW() + INTERVAL '2 days'
);

-- Update statistics
UPDATE companies SET 
  agent_count = (SELECT COUNT(*) FROM agents WHERE agents.company_id = companies.id),
  updated_at = NOW();

