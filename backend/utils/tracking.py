"""
LLM API Call Tracking Decorator
Tracks LLM calls with token usage, costs, and performance metrics
"""

from functools import wraps
import time
import uuid
import asyncio
import threading
from typing import Callable, Optional

# Store reference to the main event loop for thread-safe logging
_main_event_loop: Optional[asyncio.AbstractEventLoop] = None
_main_event_loop_lock = threading.Lock()


def set_main_event_loop(loop: asyncio.AbstractEventLoop):
    """Set the main event loop for thread-safe async logging"""
    global _main_event_loop
    with _main_event_loop_lock:
        _main_event_loop = loop


def _schedule_logging_task(coro):
    """
    Schedule an async logging task, handling both async and sync contexts.
    
    Uses the best method available:
    - If in async context: asyncio.create_task()
    - If in thread without loop: asyncio.run_coroutine_threadsafe() on main loop
    - If no main loop: runs in background thread with new event loop
    """
    try:
        # Try to get the current running event loop
        loop = asyncio.get_running_loop()
        # We're in an async context, use create_task
        asyncio.create_task(coro)
    except RuntimeError:
        # No running event loop - we're likely in a thread
        with _main_event_loop_lock:
            main_loop = _main_event_loop
        
        if main_loop and main_loop.is_running():
            # Use thread-safe scheduling on the main event loop
            asyncio.run_coroutine_threadsafe(coro, main_loop)
        else:
            # No main loop available - run in background thread with new event loop
            def run_in_thread():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(coro)
                    loop.close()
                except Exception:
                    # Silently ignore errors in background logging
                    pass
            
            thread = threading.Thread(target=run_in_thread, daemon=True)
            thread.start()


def track_llm_call(endpoint_name: str):
    """
    Decorator to track LLM API calls
    
    Supports both sync and async functions.
    Logging is done asynchronously (fire-and-forget) to not block requests.
    
    Args:
        endpoint_name: Name of the endpoint/method being tracked
    """
    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):
            # Async function
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                request_id = str(uuid.uuid4())
                
                # Import here to avoid circular imports
                # Import instances from app module (created in app.py)
                from app import database_service, ai_service
                from utils.cost_calculator import calculate_cost
                
                provider_name = ai_service.provider_name.lower()
                model_name = getattr(ai_service._service, 'model', 'unknown')
                
                try:
                    result = await func(*args, **kwargs)
                    response_time = int((time.time() - start_time) * 1000)
                    
                    # Extract token usage from result
                    # Result may be a dict with 'usage' key or separate token fields
                    input_tokens = 0
                    output_tokens = 0
                    total_tokens = 0
                    
                    if isinstance(result, dict):
                        if 'usage' in result:
                            usage = result['usage']
                            input_tokens = usage.get('prompt_tokens', 0) or usage.get('input_tokens', 0)
                            output_tokens = usage.get('completion_tokens', 0) or usage.get('output_tokens', 0)
                            total_tokens = usage.get('total_tokens', 0) or (input_tokens + output_tokens)
                        else:
                            input_tokens = result.get('input_tokens', 0)
                            output_tokens = result.get('output_tokens', 0)
                            total_tokens = result.get('total_tokens', 0) or (input_tokens + output_tokens)
                    
                    # Calculate cost
                    estimated_cost = calculate_cost(provider_name, model_name, input_tokens, output_tokens)
                    
                    # Extract theme if available
                    theme = kwargs.get('theme') or (args[0] if args else None)
                    
                    # Log to database (fire-and-forget)
                    asyncio.create_task(database_service.log_llm_call({
                        'provider': provider_name,
                        'model': model_name,
                        'endpoint': endpoint_name,
                        'theme': theme,
                        'input_tokens': input_tokens,
                        'output_tokens': output_tokens,
                        'total_tokens': total_tokens,
                        'estimated_cost': estimated_cost,
                        'response_time_ms': response_time,
                        'success': True,
                        'request_id': request_id
                    }))
                    
                    return result
                except Exception as e:
                    response_time = int((time.time() - start_time) * 1000)
                    
                    # Log error (fire-and-forget)
                    asyncio.create_task(database_service.log_llm_call({
                        'provider': provider_name,
                        'model': model_name,
                        'endpoint': endpoint_name,
                        'theme': kwargs.get('theme') or (args[0] if args else None),
                        'input_tokens': 0,
                        'output_tokens': 0,
                        'total_tokens': 0,
                        'estimated_cost': 0.0,
                        'response_time_ms': response_time,
                        'success': False,
                        'error_message': str(e),
                        'request_id': request_id
                    }))
                    raise
            return async_wrapper
        else:
            # Sync function
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                request_id = str(uuid.uuid4())
                
                # Import here to avoid circular imports
                # Import instances from app module (created in app.py)
                from app import database_service, ai_service
                from utils.cost_calculator import calculate_cost
                
                provider_name = ai_service.provider_name.lower()
                model_name = getattr(ai_service._service, 'model', 'unknown')
                
                try:
                    result = func(*args, **kwargs)
                    response_time = int((time.time() - start_time) * 1000)
                    
                    # Extract token usage (same logic as async)
                    input_tokens = 0
                    output_tokens = 0
                    total_tokens = 0
                    
                    if isinstance(result, dict):
                        if 'usage' in result:
                            usage = result['usage']
                            input_tokens = usage.get('prompt_tokens', 0) or usage.get('input_tokens', 0)
                            output_tokens = usage.get('completion_tokens', 0) or usage.get('output_tokens', 0)
                            total_tokens = usage.get('total_tokens', 0) or (input_tokens + output_tokens)
                        else:
                            input_tokens = result.get('input_tokens', 0)
                            output_tokens = result.get('output_tokens', 0)
                            total_tokens = result.get('total_tokens', 0) or (input_tokens + output_tokens)
                    
                    # Calculate cost
                    estimated_cost = calculate_cost(provider_name, model_name, input_tokens, output_tokens)
                    
                    # Extract theme
                    theme = kwargs.get('theme') or (args[0] if args else None)
                    
                    # Log to database (fire-and-forget, async)
                    # Use thread-safe scheduling that works from any context
                    _schedule_logging_task(database_service.log_llm_call({
                        'provider': provider_name,
                        'model': model_name,
                        'endpoint': endpoint_name,
                        'theme': theme,
                        'input_tokens': input_tokens,
                        'output_tokens': output_tokens,
                        'total_tokens': total_tokens,
                        'estimated_cost': estimated_cost,
                        'response_time_ms': response_time,
                        'success': True,
                        'request_id': request_id
                    }))
                    
                    return result
                except Exception as e:
                    response_time = int((time.time() - start_time) * 1000)
                    
                    # Log error (fire-and-forget)
                    # Use thread-safe scheduling that works from any context
                    _schedule_logging_task(database_service.log_llm_call({
                        'provider': provider_name,
                        'model': model_name,
                        'endpoint': endpoint_name,
                        'theme': kwargs.get('theme') or (args[0] if args else None),
                        'input_tokens': 0,
                        'output_tokens': 0,
                        'total_tokens': 0,
                        'estimated_cost': 0.0,
                        'response_time_ms': response_time,
                        'success': False,
                        'error_message': str(e),
                        'request_id': request_id
                    }))
                    raise
            return sync_wrapper
    return decorator

