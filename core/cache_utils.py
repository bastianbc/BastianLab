from django.core.cache import cache
from django.contrib.auth.models import User
from projects.utils import get_user_projects
import hashlib


def get_cached_user_projects(user, timeout=300):
    """
    Cache user projects to avoid repeated database queries.
    Cache timeout: 5 minutes (300 seconds)
    """
    if not user or not user.is_authenticated:
        return []
    
    cache_key = f"user_projects_{user.id}_{user.last_login.timestamp() if user.last_login else 'never'}"
    
    # Try to get from cache first
    cached_projects = cache.get(cache_key)
    if cached_projects is not None:
        return cached_projects
    
    # If not in cache, fetch from database
    projects = get_user_projects(user)
    
    # Cache the result
    cache.set(cache_key, projects, timeout)
    
    return projects


def get_cached_block_url(timeout=3600):
    """
    Cache block URL to avoid repeated queries.
    Cache timeout: 1 hour (3600 seconds)
    """
    cache_key = "block_url"
    
    cached_url = cache.get(cache_key)
    if cached_url is not None:
        return cached_url
    
    # Import here to avoid circular imports
    from blocks.models import BlockUrl
    
    try:
        url_obj = BlockUrl.objects.order_by('id').first()
        url = url_obj.url if url_obj else None
    except:
        url = None
    
    cache.set(cache_key, url, timeout)
    return url


def invalidate_user_cache(user_id):
    """
    Invalidate cache for a specific user when their permissions change.
    """
    # This is a simple approach - in production you might want to use cache versioning
    cache.delete_many([key for key in cache._cache.keys() if f"user_projects_{user_id}_" in key])


def invalidate_block_url_cache():
    """
    Invalidate block URL cache when it changes.
    """
    cache.delete("block_url")
