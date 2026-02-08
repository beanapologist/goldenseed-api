# GoldenSeed API

**Deterministic Procedural Generation as a Service**

Generate infinite, reproducible content from tiny seeds. Same seed → same output, always.

Perfect for games, testing, generative art, and scientific simulations.

## Features

- ✅ **Deterministic** - Same seed always produces identical output
- ✅ **Verifiable** - Hash proves output authenticity
- ✅ **Perfect Statistics** - 50/50 coin flip guaranteed
- ✅ **Fast** - Serverless, global CDN
- ✅ **Simple** - RESTful API, easy integration

⚠️ **Not cryptographically secure** - Use for generation/testing, not passwords/keys

---

## Quick Start

### 1. Get API Key

Demo key for testing:
```
Bearer gs_demo_key_12345
```

### 2. Generate Content

```bash
curl -X POST https://goldenseed-api.vercel.app/api/v1/generate \
  -H "Authorization: Bearer gs_demo_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "seed": 12345,
    "chunks": 100,
    "format": "hex"
  }'
```

### 3. Response

```json
{
  "data": ["a1b2c3d4...", ...],
  "hash": "sha256...",
  "chunks_generated": 100,
  "seed": 12345,
  "verification_url": "https://goldenseed.io/verify/abc123"
}
```

---

## API Endpoints

### POST /api/v1/generate

Generate deterministic entropy from a seed.

**Request:**
```json
{
  "seed": 12345,
  "chunks": 100,
  "format": "hex" | "json" | "binary",
  "skip": 0  // optional
}
```

**Response:**
```json
{
  "data": [...],
  "hash": "sha256...",
  "chunks_generated": 100,
  "seed": 12345,
  "verification_url": "..."
}
```

### GET /api/v1/stats/coinflip

Demonstrate perfect 50/50 distribution.

**Query Params:**
- `seed` (default: 0)
- `flips` (default: 100000, max: 1000000)

**Response:**
```json
{
  "heads": 500123,
  "tails": 499877,
  "total": 1000000,
  "heads_ratio": 0.500123,
  "perfect_balance": true,
  "message": "..."
}
```

### POST /api/v1/batch

Generate from multiple seeds.

**Request:**
```json
{
  "seeds": [1, 2, 3],
  "chunks_per_seed": 100
}
```

**Response:**
```json
{
  "results": [
    {"seed": 1, "data": [...], ...},
    ...
  ]
}
```

---

## Local Development

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Run Server

```bash
python main.py
```

API available at: http://localhost:8000

Docs available at: http://localhost:8000/docs

### 3. Test

```bash
# Health check
curl http://localhost:8000/

# Generate
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer gs_demo_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"seed": 42, "chunks": 10}'

# Coin flip stats
curl "http://localhost:8000/api/v1/stats/coinflip?seed=42&flips=100000"
```

---

## Deployment (Vercel)

### 1. Install Vercel CLI

```bash
npm i -g vercel
```

### 2. Login

```bash
vercel login
```

### 3. Deploy

```bash
cd goldenseed-api
vercel --prod
```

Your API will be live at: `https://your-project.vercel.app`

---

## Use Cases

### 🎮 Game Development

```python
import requests

def generate_world(seed):
    response = requests.post(
        "https://goldenseed-api.vercel.app/api/v1/generate",
        headers={"Authorization": "Bearer YOUR_API_KEY"},
        json={"seed": seed, "chunks": 1000}
    )
    return response.json()

world = generate_world(seed=12345)
print(f"Generated world with hash: {world['hash']}")
```

### 🎨 Generative Art

```javascript
async function generateArt(seed) {
  const response = await fetch('https://goldenseed-api.vercel.app/api/v1/generate', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ seed, chunks: 100 })
  });
  
  const data = await response.json();
  return data.data; // Use for procedural art parameters
}
```

### 🧪 Testing & QA

```python
def test_with_deterministic_data():
    # Always generate same test data
    response = requests.post(
        "https://goldenseed-api.vercel.app/api/v1/generate",
        headers={"Authorization": "Bearer YOUR_API_KEY"},
        json={"seed": 42, "chunks": 10}
    )
    
    test_data = response.json()['data']
    # Use test_data for reproducible tests
    assert process_data(test_data) == expected_result
```

---

## Pricing

| Tier | Price/mo | Chunks/mo | Rate Limit |
|------|----------|-----------|------------|
| **Free** | $0 | 10,000 | 100/min |
| **Indie** | $10 | 1,000,000 | 1,000/min |
| **Studio** | $100 | 10,000,000 | 10,000/min |
| **Enterprise** | Custom | Unlimited | Unlimited |

Get your API key: https://goldenseed.io/pricing

---

## Tech Stack

- **Backend:** FastAPI (Python)
- **Hosting:** Vercel (serverless)
- **Core:** [golden-seed](https://github.com/COINjecture-Network/seed)
- **Auth:** API keys (Clerk/Auth0 for production)
- **Payments:** Stripe

---

## Roadmap

- [x] Core API (`/generate`, `/verify`, `/stats`)
- [x] Batch endpoint
- [ ] User dashboard
- [ ] Unity SDK
- [ ] Unreal SDK
- [ ] Stripe integration
- [ ] Usage analytics
- [ ] Custom seed domains
- [ ] Seed marketplace

---

## License

GPL-3.0+ (same as golden-seed library)

---

## Links

- **Landing Page:** https://goldenseed.io *(coming soon)*
- **GitHub:** https://github.com/beanapologist/seed
- **PyPI:** https://pypi.org/project/golden-seed/
- **Moltbook:** @FavaBot

---

## Support

Questions? Issues?

- **GitHub Issues:** https://github.com/beanapologist/goldenseed-api/issues
- **Email:** support@goldenseed.io
- **Twitter:** @beanapologist

---

**Built with 💛 by the GoldenSeed community**

*Deterministic streams for a procedural world*
