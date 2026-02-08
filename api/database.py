"""
Database connection and query helpers for GoldenSeed API
Uses Supabase (Postgres) for data storage
"""

import os
from typing import Optional, Dict, Any
import hashlib
from datetime import datetime
from supabase import create_client, Client

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")  # Service role key (backend only)

supabase: Optional[Client] = None

def init_supabase():
    """Initialize Supabase client"""
    global supabase
    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        return True
    return False

def hash_api_key(key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(key.encode()).hexdigest()

async def verify_api_key(key: str) -> Optional[Dict[str, Any]]:
    """
    Verify API key and return user + subscription info
    Returns None if invalid
    """
    if not supabase:
        return None
    
    key_hash = hash_api_key(key)
    
    try:
        # Get API key record
        key_result = supabase.table("api_keys").select(
            "id, user_id, active"
        ).eq("key_hash", key_hash).eq("active", True).execute()
        
        if not key_result.data or len(key_result.data) == 0:
            return None
        
        key_record = key_result.data[0]
        user_id = key_record["user_id"]
        
        # Get user info
        user_result = supabase.table("users").select(
            "id, email"
        ).eq("id", user_id).execute()
        
        if not user_result.data:
            return None
        
        user = user_result.data[0]
        
        # Get subscription info
        sub_result = supabase.table("subscriptions").select(
            "tier, chunks_limit, rate_limit, active"
        ).eq("user_id", user_id).eq("active", True).execute()
        
        if not sub_result.data or len(sub_result.data) == 0:
            return None
        
        subscription = sub_result.data[0]
        
        # Update last_used_at
        supabase.table("api_keys").update({
            "last_used_at": datetime.utcnow().isoformat()
        }).eq("id", key_record["id"]).execute()
        
        return {
            "user_id": user_id,
            "api_key_id": key_record["id"],
            "email": user["email"],
            "tier": subscription["tier"],
            "chunks_limit": subscription["chunks_limit"],
            "rate_limit": subscription["rate_limit"]
        }
    
    except Exception as e:
        print(f"Error verifying API key: {e}")
        return None

async def get_monthly_usage(user_id: str) -> int:
    """Get user's current month usage (chunks generated)"""
    if not supabase:
        return 0
    
    try:
        result = supabase.rpc("get_monthly_usage", {"p_user_id": user_id}).execute()
        return result.data or 0
    except Exception as e:
        print(f"Error getting usage: {e}")
        return 0

async def check_rate_limit(user_id: str, limit: int) -> bool:
    """Check if user is within rate limit (requests per minute)"""
    if not supabase:
        return True  # Fail open in dev
    
    try:
        result = supabase.rpc("check_rate_limit", {
            "p_user_id": user_id,
            "p_limit": limit
        }).execute()
        return result.data or False
    except Exception as e:
        print(f"Error checking rate limit: {e}")
        return True  # Fail open

async def log_usage(
    user_id: str,
    api_key_id: str,
    endpoint: str,
    chunks_generated: int,
    response_time_ms: int,
    status_code: int
):
    """Log API usage for billing and analytics"""
    if not supabase:
        return
    
    try:
        supabase.table("usage_logs").insert({
            "user_id": user_id,
            "api_key_id": api_key_id,
            "endpoint": endpoint,
            "chunks_generated": chunks_generated,
            "response_time_ms": response_time_ms,
            "status_code": status_code
        }).execute()
    except Exception as e:
        print(f"Error logging usage: {e}")

async def create_user(email: str, stripe_customer_id: Optional[str] = None) -> Optional[str]:
    """Create new user and return user_id"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("users").insert({
            "email": email,
            "stripe_customer_id": stripe_customer_id
        }).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        return None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

async def create_subscription(
    user_id: str,
    tier: str = "free",
    stripe_subscription_id: Optional[str] = None
) -> bool:
    """Create subscription for user"""
    if not supabase:
        return False
    
    # Tier limits
    limits = {
        "free": {"chunks": 10000, "rate": 100},
        "indie": {"chunks": 1000000, "rate": 1000},
        "studio": {"chunks": 10000000, "rate": 10000},
        "enterprise": {"chunks": 100000000, "rate": 100000}
    }
    
    tier_limits = limits.get(tier, limits["free"])
    
    try:
        supabase.table("subscriptions").insert({
            "user_id": user_id,
            "tier": tier,
            "stripe_subscription_id": stripe_subscription_id,
            "chunks_limit": tier_limits["chunks"],
            "rate_limit": tier_limits["rate"],
            "active": True
        }).execute()
        return True
    except Exception as e:
        print(f"Error creating subscription: {e}")
        return False

async def create_api_key(user_id: str, name: Optional[str] = None) -> Optional[str]:
    """
    Create new API key for user
    Returns the actual key (only time it's visible)
    """
    if not supabase:
        return None
    
    import secrets
    
    # Generate key: gs_<32 random chars>
    key = f"gs_{secrets.token_urlsafe(32)}"
    key_hash = hash_api_key(key)
    key_prefix = key[:11]  # gs_abcdefg...
    
    try:
        supabase.table("api_keys").insert({
            "user_id": user_id,
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "name": name or "Default API Key",
            "active": True
        }).execute()
        
        return key
    except Exception as e:
        print(f"Error creating API key: {e}")
        return None

# Initialize on import
init_supabase()
