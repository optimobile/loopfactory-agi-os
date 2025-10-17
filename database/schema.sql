-- Loop Factory AI - Complete Database Schema
-- Supports all 11 companies under the ecosystem
-- Created: October 17, 2025

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CORE TABLES (Loop Factory AI)
-- ============================================================================

-- Loops (discovered automation opportunities)
CREATE TABLE loops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_url TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL, -- github, reddit, user_submission, etc.
    content_type TEXT NOT NULL, -- text_description, code_snippet, tutorial, etc.
    raw_content TEXT,
    metadata JSONB DEFAULT '{}',
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_loops_source_type ON loops(source_type);
CREATE INDEX idx_loops_discovered_at ON loops(discovered_at DESC);
CREATE INDEX idx_loops_metadata ON loops USING GIN(metadata);

-- Features (extracted from loops)
CREATE TABLE features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loop_id UUID NOT NULL REFERENCES loops(id) ON DELETE CASCADE,
    has_code BOOLEAN DEFAULT FALSE,
    code_language TEXT,
    code_complexity REAL DEFAULT 0.0,
    code_lines INTEGER DEFAULT 0,
    title_length INTEGER DEFAULT 0,
    description_length INTEGER DEFAULT 0,
    has_tutorial BOOLEAN DEFAULT FALSE,
    has_documentation BOOLEAN DEFAULT FALSE,
    popularity_score REAL DEFAULT 0.0,
    author_reputation REAL DEFAULT 0.0,
    recency_score REAL DEFAULT 0.0,
    primary_category TEXT,
    secondary_categories TEXT[] DEFAULT '{}',
    keywords TEXT[] DEFAULT '{}',
    automation_type TEXT,
    complexity_level TEXT, -- beginner, intermediate, advanced
    estimated_value REAL DEFAULT 0.0,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(loop_id)
);

CREATE INDEX idx_features_loop_id ON features(loop_id);
CREATE INDEX idx_features_primary_category ON features(primary_category);
CREATE INDEX idx_features_estimated_value ON features(estimated_value DESC);

-- Quality Scores
CREATE TABLE quality_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loop_id UUID NOT NULL REFERENCES loops(id) ON DELETE CASCADE,
    overall_score REAL NOT NULL,
    approval_decision TEXT NOT NULL, -- approved, rejected, needs_review
    confidence REAL DEFAULT 0.0,
    reasoning JSONB DEFAULT '[]',
    scored_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(loop_id)
);

CREATE INDEX idx_quality_scores_loop_id ON quality_scores(loop_id);
CREATE INDEX idx_quality_scores_decision ON quality_scores(approval_decision);
CREATE INDEX idx_quality_scores_overall_score ON quality_scores(overall_score DESC);

-- Agents (approved loops deployed as products)
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loop_id UUID REFERENCES loops(id) ON DELETE SET NULL,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    long_description TEXT,
    category TEXT,
    tags TEXT[] DEFAULT '{}',
    price_usd REAL DEFAULT 0.0,
    pricing_model TEXT DEFAULT 'subscription', -- subscription, one_time, usage_based
    stripe_product_id TEXT,
    stripe_price_id TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    purchase_count INTEGER DEFAULT 0,
    rating_average REAL DEFAULT 0.0,
    rating_count INTEGER DEFAULT 0,
    deployed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_agents_company_id ON agents(company_id);
CREATE INDEX idx_agents_slug ON agents(slug);
CREATE INDEX idx_agents_category ON agents(category);
CREATE INDEX idx_agents_is_active ON agents(is_active);
CREATE INDEX idx_agents_is_featured ON agents(is_featured);
CREATE INDEX idx_agents_price_usd ON agents(price_usd);

-- ============================================================================
-- COMPANY MANAGEMENT
-- ============================================================================

-- Companies (the 11 SaaS companies)
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL UNIQUE,
    industry TEXT NOT NULL,
    description TEXT,
    logo_url TEXT,
    primary_color TEXT DEFAULT '#3B82F6',
    is_active BOOLEAN DEFAULT TRUE,
    launch_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_companies_slug ON companies(slug);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_is_active ON companies(is_active);

-- Insert the 11 companies
INSERT INTO companies (name, slug, domain, industry, description) VALUES
('Loop Factory AI', 'loopfactory', 'loopfactory.ai', 'AI Agent Marketplace', 'AI agent marketplace powering industry automation'),
('KoiKeeper AI', 'koikeeper', 'koikeeper.ai', 'Koi Pond Management', 'AI-powered koi pond management and care'),
('FishKeeper AI', 'fishkeeper', 'fishkeeper.ai', 'Aquarium Management', 'Smart aquarium management for hobbyists and professionals'),
('LandLaw AI', 'landlaw', 'landlaw.ai', 'Property Legal', 'AI legal assistant for landlords and property managers'),
('Social Media Mananger AI', 'socialmediamananger', 'socialmediamananger.ai', 'Social Media Automation', 'Automated social media management and content generation'),
('MuckAway AI', 'muckaway', 'muckaway.ai', 'Waste Management', 'AI-powered waste management and logistics optimization'),
('GrabHire AI', 'grabhire', 'grabhire.ai', 'Equipment Rental', 'Smart equipment rental marketplace'),
('PlantHire AI', 'planthire', 'planthire.ai', 'Plant Hire', 'Heavy equipment hire and fleet management'),
('DIYHelp AI', 'diyhelp', 'diyhelp.ai', 'DIY/Home Improvement', 'AI assistant for DIY projects and home improvement'),
('PokerHUD AI', 'pokerhud', 'pokerhud.ai', 'Poker Analytics', 'AI-powered poker analytics and strategy'),
('CommercialVehicle AI', 'commercialvehicle', 'commercialvehicle.ai', 'Fleet Management', 'Commercial fleet management and optimization');

-- ============================================================================
-- USER MANAGEMENT
-- ============================================================================

-- Users (leverages Supabase Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    stripe_customer_id TEXT UNIQUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_stripe_customer_id ON users(stripe_customer_id);

-- User Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    stripe_subscription_id TEXT UNIQUE,
    status TEXT NOT NULL, -- active, canceled, past_due, etc.
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_agent_id ON subscriptions(agent_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- Purchases (one-time purchases)
CREATE TABLE purchases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    stripe_payment_intent_id TEXT UNIQUE,
    amount_usd REAL NOT NULL,
    status TEXT NOT NULL, -- succeeded, pending, failed
    purchased_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_purchases_user_id ON purchases(user_id);
CREATE INDEX idx_purchases_agent_id ON purchases(agent_id);
CREATE INDEX idx_purchases_purchased_at ON purchases(purchased_at DESC);

-- ============================================================================
-- CONTENT & MARKETING
-- ============================================================================

-- Blog Posts (auto-generated)
CREATE TABLE blog_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    slug TEXT NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    featured_image_url TEXT,
    author_name TEXT DEFAULT 'AI Assistant',
    seo_title TEXT,
    seo_description TEXT,
    keywords TEXT[] DEFAULT '{}',
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP WITH TIME ZONE,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, slug)
);

CREATE INDEX idx_blog_posts_company_id ON blog_posts(company_id);
CREATE INDEX idx_blog_posts_slug ON blog_posts(slug);
CREATE INDEX idx_blog_posts_is_published ON blog_posts(is_published);
CREATE INDEX idx_blog_posts_published_at ON blog_posts(published_at DESC);

-- Social Media Posts (auto-generated and scheduled)
CREATE TABLE social_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    platform TEXT NOT NULL, -- twitter, linkedin, facebook, instagram
    content TEXT NOT NULL,
    media_urls TEXT[] DEFAULT '{}',
    hashtags TEXT[] DEFAULT '{}',
    status TEXT DEFAULT 'scheduled', -- scheduled, posted, failed
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    posted_at TIMESTAMP WITH TIME ZONE,
    platform_post_id TEXT,
    engagement_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_social_posts_company_id ON social_posts(company_id);
CREATE INDEX idx_social_posts_platform ON social_posts(platform);
CREATE INDEX idx_social_posts_status ON social_posts(status);
CREATE INDEX idx_social_posts_scheduled_for ON social_posts(scheduled_for);

-- ============================================================================
-- AUTOMATION & OUTREACH
-- ============================================================================

-- Leads (captured from various sources)
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    company_name TEXT,
    job_title TEXT,
    phone TEXT,
    source TEXT, -- website, outreach, referral, etc.
    status TEXT DEFAULT 'new', -- new, contacted, qualified, converted, lost
    score INTEGER DEFAULT 0, -- 0-100 lead score
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_leads_company_id ON leads(company_id);
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_score ON leads(score DESC);

-- Outreach Campaigns
CREATE TABLE outreach_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    template_subject TEXT NOT NULL,
    template_body TEXT NOT NULL,
    status TEXT DEFAULT 'draft', -- draft, active, paused, completed
    sent_count INTEGER DEFAULT 0,
    opened_count INTEGER DEFAULT 0,
    replied_count INTEGER DEFAULT 0,
    converted_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_outreach_campaigns_company_id ON outreach_campaigns(company_id);
CREATE INDEX idx_outreach_campaigns_status ON outreach_campaigns(status);

-- Outreach Messages
CREATE TABLE outreach_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID REFERENCES outreach_campaigns(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT DEFAULT 'scheduled', -- scheduled, sent, opened, replied, bounced
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    replied_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_outreach_messages_campaign_id ON outreach_messages(campaign_id);
CREATE INDEX idx_outreach_messages_lead_id ON outreach_messages(lead_id);
CREATE INDEX idx_outreach_messages_status ON outreach_messages(status);
CREATE INDEX idx_outreach_messages_scheduled_for ON outreach_messages(scheduled_for);

-- ============================================================================
-- SUPPORT & ENGAGEMENT
-- ============================================================================

-- Support Tickets
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'open', -- open, in_progress, resolved, closed
    priority TEXT DEFAULT 'medium', -- low, medium, high, urgent
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_support_tickets_company_id ON support_tickets(company_id);
CREATE INDEX idx_support_tickets_user_id ON support_tickets(user_id);
CREATE INDEX idx_support_tickets_status ON support_tickets(status);
CREATE INDEX idx_support_tickets_priority ON support_tickets(priority);

-- Ticket Messages
CREATE TABLE ticket_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    is_from_staff BOOLEAN DEFAULT FALSE,
    is_from_ai BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ticket_messages_ticket_id ON ticket_messages(ticket_id);
CREATE INDEX idx_ticket_messages_created_at ON ticket_messages(created_at);

-- Reviews & Ratings
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title TEXT,
    comment TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_id, user_id)
);

CREATE INDEX idx_reviews_agent_id ON reviews(agent_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_created_at ON reviews(created_at DESC);

-- ============================================================================
-- ANALYTICS & TRACKING
-- ============================================================================

-- Page Views
CREATE TABLE page_views (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    page_path TEXT NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id TEXT,
    referrer TEXT,
    user_agent TEXT,
    ip_address INET,
    country TEXT,
    city TEXT,
    viewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_page_views_company_id ON page_views(company_id);
CREATE INDEX idx_page_views_page_path ON page_views(page_path);
CREATE INDEX idx_page_views_viewed_at ON page_views(viewed_at DESC);

-- Events (custom tracking)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_name TEXT NOT NULL,
    event_data JSONB DEFAULT '{}',
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_events_company_id ON events(company_id);
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_event_name ON events(event_name);
CREATE INDEX idx_events_created_at ON events(created_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Users can view their own subscriptions
CREATE POLICY "Users can view own subscriptions" ON subscriptions
    FOR SELECT USING (auth.uid() = user_id);

-- Users can view their own purchases
CREATE POLICY "Users can view own purchases" ON purchases
    FOR SELECT USING (auth.uid() = user_id);

-- Users can view their own tickets
CREATE POLICY "Users can view own tickets" ON support_tickets
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create tickets" ON support_tickets
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can view messages on their tickets
CREATE POLICY "Users can view own ticket messages" ON ticket_messages
    FOR SELECT USING (
        ticket_id IN (
            SELECT id FROM support_tickets WHERE user_id = auth.uid()
        )
    );

-- Users can create reviews for agents they purchased
CREATE POLICY "Users can create reviews" ON reviews
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view all reviews" ON reviews
    FOR SELECT USING (true);

-- Public read access for certain tables
CREATE POLICY "Public can view companies" ON companies
    FOR SELECT USING (is_active = true);

CREATE POLICY "Public can view active agents" ON agents
    FOR SELECT USING (is_active = true);

CREATE POLICY "Public can view published blog posts" ON blog_posts
    FOR SELECT USING (is_published = true);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_loops_updated_at BEFORE UPDATE ON loops
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blog_posts_updated_at BEFORE UPDATE ON blog_posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_social_posts_updated_at BEFORE UPDATE ON social_posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_outreach_campaigns_updated_at BEFORE UPDATE ON outreach_campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_outreach_messages_updated_at BEFORE UPDATE ON outreach_messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_support_tickets_updated_at BEFORE UPDATE ON support_tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA MIGRATION
-- ============================================================================

-- This will be populated from existing JSON files
-- See migration script: migrate_json_to_supabase.py

