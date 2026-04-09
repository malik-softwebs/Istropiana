import jellyfish # Advanced phonetics
import httpx
import re

# --- 1000+ ITEMS PHONETIC ENGINE ---
TOP_1000_BRANDS = ["Apple", "Google", "Microsoft", "Amazon", "Samsung", "Toyota"] # Extend this list to 1000

def check_global_conflicts(name):
    conflicts = []
    for brand in TOP_1000_BRANDS:
        # Jaro-Winkler gives a score from 0.0 to 1.0
        similarity = jellyfish.jaro_winkler_similarity(name.lower(), brand.lower())
        if similarity > 0.85: # 85% similarity threshold
            conflicts.append(f"{brand} ({int(similarity*100)}%)")
    return conflicts

# --- GOVT & IPO DEEP SCAN (The DuckDuckGo Proxy) ---
async def check_govt_records(name):
    """Uses search engine dorks to find government filings without an API."""
    search_query = f'site:ipo.gov.pk "{name}"'
    url = f"https://duckduckgo.com/html/?q={search_query}"
    
    async with httpx.AsyncClient() as client:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            response = await client.get(url, headers=headers)
            # If the search results contain the name, it's likely a registered trademark
            if name.lower() in response.text.lower():
                return "❌ Potential IPO Record Found"
            return "✅ No IPO Records Found"
        except:
            return "⚠️ Scan Interrupted"

# --- OPEN CORPORATES SCAN ---
async def check_corporates(name):
    """Checks if the name is a registered company name globally."""
    url = f"https://opencorporates.com/companies?q={name}"
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, follow_redirects=True)
            if "No companies found" in res.text:
                return "✅ Name is Unique"
            return "❌ Existing Company Found"
        except:
            return "⚠️ Database Busy"
