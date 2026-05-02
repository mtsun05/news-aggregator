import httpx
from fastapi.responses import JSONResponse
from dotenv import get_key

REDIS_API_URL="https://aws-us-east-1.langcache.redis.io"
CACHE_ID = get_key(".env", "CACHE_ID")
LANGCACHE_API_KEY = get_key(".env", "LANGCACHE_API_KEY")

async def search_key(key: str):
	# validate key
	if len(key) > 1024:
		return JSONResponse(content="Error: Key must be less than 1024 chars", status_code=400)
	
	# make request
	try:
		async with httpx.AsyncClient() as async_client:
			response = await async_client.get(f"{REDIS_API_URL}/v1/caches/{CACHE_ID}/entries/search", headers={
				"accept": "application/json",
				"Authorization": f"Bearer {LANGCACHE_API_KEY}"
			}, data={
				"prompt": key,
				"similarityThreshold": 0.9,
				"searchStrategies": ["exact", "semantic"]
			})
			# returns [] on miss
			return JSONResponse(content=response.data, status_code=200)
	# catch errors
	except Exception as e:
		return JSONResponse(content=f"Error occurred: {e}", status_code=500)

async def insert_pair(key: str, value: str):
	# validate key
	if len(key) > 1024:
		return JSONResponse(content="Error: Key must be less than 1024 chars", status_code=400)
	
	# make request
	try:
		async with httpx.AsyncClient() as async_client:
			response = await async_client.post(f"{REDIS_API_URL}/v1/caches/{CACHE_ID}/entries", headers={
				"accept": "application/json",
				"Authorization": f"Bearer {LANGCACHE_API_KEY}"
			}, data={
				"prompt": key,
				"response": value,
			})
			return JSONResponse(content=response.entryId, status_code=200)
	# catch errors
	except Exception as e:
		return JSONResponse(content=f"Error occurred: {e}", status_code=500)

async def delete_pair(id: str):
	# make request
	try:
		async with httpx.AsyncClient() as async_client:
			response = await async_client.get(f"{REDIS_API_URL}/v1/caches/{CACHE_ID}/entries/{id}", headers={
				"accept": "application/json",
				"Authorization": f"Bearer {LANGCACHE_API_KEY}"
			})
			return JSONResponse(content="Delete succeeded", status_code=200)
	# catch errors
	except Exception as e:
		return JSONResponse(content=f"Error occurred: {e}", status_code=500)