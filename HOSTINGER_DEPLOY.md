# Deploy Landing Page to Hostinger

## Quick Manual Upload (2 minutes)

1. **Login to Hostinger:** https://hpanel.hostinger.com
2. **Go to File Manager:**
   - Select your domain (goldenseed.coinjecture.com or whatever domain you're using)
   - Navigate to `public_html/`
3. **Upload:**
   - Click "Upload" button
   - Select `/data/.openclaw/workspace/goldenseed-api/landing/index.html`
   - If there's an existing index.html, replace it
4. **Done!** 
   - Visit your domain to see the live site
   - All three interactive demos will work immediately

## File Location
`/data/.openclaw/workspace/goldenseed-api/landing/index.html`

## What's Included
- 🌱 Live API demo (real-time generation)
- 🎨 Seed fingerprint visualizer
- 🗺️ Procedural dungeon generator
- All demos auto-generate on page load

---

**Note:** The landing page calls the live Vercel API (`https://goldenseed-api.vercel.app`) so everything works out of the box!
