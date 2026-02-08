# GoldenSeed API - Production Deployment Guide

## 🚀 Zero-Cost Production Stack

- **API Backend:** Vercel (serverless)
- **Database:** Supabase (Postgres)
- **Payments:** Stripe
- **Landing Page:** Hostinger (static)

**Total cost:** $0/month until you have paying customers! 💰

---

## Step 1: Supabase Setup (Database)

### 1.1 Create Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Name: `goldenseed-api`
4. Database Password: (save this!)
5. Region: Choose closest to users
6. Click "Create Project"

### 1.2 Run Schema

1. In Supabase dashboard, click "SQL Editor"
2. Copy contents of `database/schema.sql`
3. Paste and click "Run"
4. Should see: "Success. No rows returned"

### 1.3 Get API Keys

1. Go to Settings → API
2. Copy:
   - **URL:** `https://xxx.supabase.co`
   - **anon key:** (for frontend)
   - **service_role key:** (for backend - KEEP SECRET!)

---

## Step 2: Vercel Deployment (API)

### 2.1 Install Vercel CLI

```bash
npm install -g vercel
```

### 2.2 Login

```bash
vercel login
```

### 2.3 Configure Environment

```bash
cd goldenseed-api
vercel env add SUPABASE_URL
# Paste your Supabase URL

vercel env add SUPABASE_SERVICE_KEY
# Paste your service_role key (production, preview, development)
```

### 2.4 Deploy

```bash
vercel --prod
```

Your API will be live at: `https://goldenseed-api.vercel.app`

---

## Step 3: Test the API

### 3.1 Create Test User

Run this in Supabase SQL Editor:

```sql
-- Create test user
INSERT INTO users (email) VALUES ('test@example.com') RETURNING id;
-- Copy the returned UUID

-- Create subscription (replace USER_ID)
INSERT INTO subscriptions (user_id, tier, chunks_limit, rate_limit, active)
VALUES ('USER_ID', 'free', 10000, 100, true);

-- Create API key (replace USER_ID)
INSERT INTO api_keys (user_id, key_hash, key_prefix, name, active)
VALUES (
    'USER_ID',
    encode(sha256('gs_test_key_12345'::bytea), 'hex'),
    'gs_test_ke',
    'Test Key',
    true
);
```

### 3.2 Test Generate Endpoint

```bash
curl -X POST https://goldenseed-api.vercel.app/api/v1/generate \
  -H "Authorization: Bearer gs_test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "seed": 42,
    "chunks": 10,
    "format": "hex"
  }'
```

Should return JSON with generated data!

### 3.3 Check Usage

Query Supabase:

```sql
SELECT * FROM usage_logs ORDER BY created_at DESC LIMIT 10;
```

Should see your test request logged!

---

## Step 4: Stripe Integration (Optional - for paid tiers)

### 4.1 Create Stripe Account

1. Go to [stripe.com](https://stripe.com)
2. Sign up (free)
3. Get API keys from Dashboard

### 4.2 Create Products

In Stripe Dashboard:

1. Products → Add Product
   - **Indie:** $10/month
   - **Studio:** $100/month
   - **Enterprise:** Custom

2. Copy Price IDs

### 4.3 Add to Vercel

```bash
vercel env add STRIPE_SECRET_KEY
vercel env add STRIPE_PUBLISHABLE_KEY
```

---

## Step 5: Landing Page (Hostinger)

### 5.1 Create Simple Landing

```html
<!DOCTYPE html>
<html>
<head>
    <title>GoldenSeed API</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 50px auto; }
        .hero { text-align: center; padding: 50px 0; }
        .cta { background: #0070f3; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="hero">
        <h1>🌟 GoldenSeed API</h1>
        <p>Deterministic Procedural Generation as a Service</p>
        <p>Same seed → same output. Always.</p>
        <a href="https://goldenseed-api.vercel.app/docs" class="cta">Get API Key</a>
    </div>
</body>
</html>
```

### 5.2 Upload to Hostinger

1. Login to Hostinger
2. File Manager → public_html
3. Upload `index.html`
4. Done! Site live at your domain

---

## Step 6: Create Your First Real User

### 6.1 Signup Flow (Manual for MVP)

When someone wants an API key:

1. Get their email
2. Run in Supabase SQL Editor:

```sql
-- Create user
INSERT INTO users (email, stripe_customer_id)
VALUES ('user@example.com', NULL)
RETURNING id;

-- Create free tier subscription (copy user id from above)
INSERT INTO subscriptions (user_id, tier, chunks_limit, rate_limit, active)
VALUES ('USER_ID_HERE', 'free', 10000, 100, true);

-- Generate API key
SELECT * FROM create_api_key('USER_ID_HERE', 'My API Key');
```

3. Email them the API key: `gs_xxxxx...`

### 6.2 Automate Later

Build a signup page that:
- Collects email
- Creates user + subscription via API
- Emails API key
- (Use Clerk or Auth0 for this)

---

## Monitoring & Maintenance

### Check Usage

```sql
-- Top users
SELECT 
    u.email,
    s.tier,
    SUM(ul.chunks_generated) as total_chunks,
    COUNT(*) as requests
FROM usage_logs ul
JOIN users u ON ul.user_id = u.id
JOIN subscriptions s ON s.user_id = u.id
WHERE ul.created_at >= date_trunc('month', NOW())
GROUP BY u.email, s.tier
ORDER BY total_chunks DESC;
```

### Check Revenue Potential

```sql
-- Users hitting limits (upsell opportunity!)
SELECT 
    u.email,
    s.tier,
    SUM(ul.chunks_generated) as usage,
    s.chunks_limit
FROM usage_logs ul
JOIN users u ON ul.user_id = u.id
JOIN subscriptions s ON s.user_id = u.id
WHERE ul.created_at >= date_trunc('month', NOW())
GROUP BY u.email, s.tier, s.chunks_limit
HAVING SUM(ul.chunks_generated) > (s.chunks_limit * 0.8)
ORDER BY usage DESC;
```

---

## Cost Breakdown

### Free Tier Usage:
- **Vercel:** 100GB bandwidth, 100GB-hrs compute (free)
- **Supabase:** 500MB database, 2GB bandwidth (free)
- **Stripe:** 0% (only charges on transactions)

### When You Need to Upgrade:
- **Vercel Pro:** $20/mo (only needed at ~100k requests/day)
- **Supabase Pro:** $25/mo (only needed at 8GB database)
- **Stripe:** 2.9% + $0.30 per transaction

**Break-even:** ~10 indie users ($100/mo revenue) covers all costs!

---

## Next Steps

1. ✅ Set up Supabase
2. ✅ Deploy to Vercel
3. ✅ Test with dummy user
4. ⏳ Create landing page
5. ⏳ Add Stripe for payments
6. ⏳ Build user dashboard
7. ⏳ Launch on ProductHunt

---

## Support

Questions? Check:
- Vercel docs: https://vercel.com/docs
- Supabase docs: https://supabase.com/docs
- Stripe docs: https://stripe.com/docs

---

**You're production-ready at $0/month! 🎉**

Focus on getting users → revenue will follow → infrastructure scales automatically.
