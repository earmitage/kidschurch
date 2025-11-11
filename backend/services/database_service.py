"""
Database Service for async MySQL operations
Handles all database interactions with connection pooling
"""

import os
import json
import aiomysql
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import asyncio


class DatabaseService:
    """
    Async MySQL database service for Church Games backend
    
    Environment variables:
    - MYSQL_HOST (default: localhost)
    - MYSQL_PORT (default: 3306)
    - MYSQL_USER
    - MYSQL_PASSWORD
    - MYSQL_DATABASE
    """
    
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self.user = os.getenv('MYSQL_USER')
        self.password = os.getenv('MYSQL_PASSWORD')
        self.database = os.getenv('MYSQL_DATABASE', 'kidschurch')
        self._pool = None
        
    async def initialize(self):
        """Initialize database connection pool"""
        if not all([self.user, self.password, self.database]):
            print("⚠️  MySQL credentials not configured. Database features will be disabled.")
            return False
        
        try:
            self._pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database,
                minsize=1,
                maxsize=10,
                autocommit=True,
                charset='utf8mb4',
                connect_timeout=10
            )
            print(f"✅ Database connection pool initialized: {self.database}")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
            return False
    
    async def close(self):
        """Close database connection pool"""
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            print("✅ Database connection pool closed")
    
    def is_enabled(self) -> bool:
        """Check if database is properly configured"""
        return self._pool is not None
    
    async def _execute_query(self, query: str, params: Tuple = None) -> List:
        """Execute a SELECT query and return results"""
        if not self.is_enabled():
            raise Exception("Database service is not initialized")
        
        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    return await cursor.fetchall()
        except (aiomysql.Error, ConnectionError, OSError) as e:
            print(f"⚠️  Database query error: {e}")
            print(f"   Query: {query[:200]}...")
            raise
    
    async def _execute_insert(self, query: str, params: Tuple = None) -> int:
        """Execute an INSERT query and return last insert ID"""
        if not self.is_enabled():
            raise Exception("Database service is not initialized")
        
        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    return cursor.lastrowid
        except (aiomysql.Error, ConnectionError, OSError) as e:
            print(f"⚠️  Database insert error: {e}")
            raise
    
    async def _execute_update(self, query: str, params: Tuple = None) -> int:
        """Execute an UPDATE/DELETE query and return affected rows"""
        if not self.is_enabled():
            raise Exception("Database service is not initialized")
        
        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    return cursor.rowcount
        except (aiomysql.Error, ConnectionError, OSError) as e:
            print(f"⚠️  Database update error: {e}")
            raise
    
    async def log_llm_call(self, call_data: Dict) -> Optional[int]:
        """
        Log an LLM API call to the database
        
        Args:
            call_data: Dictionary with provider, model, endpoint, tokens, etc.
            
        Returns:
            ID of inserted record, or None if failed
        """
        if not self.is_enabled():
            return None
        
        try:
            query = """
                INSERT INTO llm_api_calls 
                (provider, model, endpoint, theme, input_tokens, output_tokens, 
                 total_tokens, estimated_cost, response_time_ms, success, error_message, request_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                call_data.get('provider'),
                call_data.get('model'),
                call_data.get('endpoint'),
                call_data.get('theme'),
                call_data.get('input_tokens', 0),
                call_data.get('output_tokens', 0),
                call_data.get('total_tokens', 0),
                call_data.get('estimated_cost', 0.0),
                call_data.get('response_time_ms', 0),
                call_data.get('success', True),
                call_data.get('error_message'),
                call_data.get('request_id')
            )
            
            call_id = await self._execute_insert(query, params)
            return call_id
        except Exception as e:
            print(f"⚠️  Failed to log LLM call: {e}")
            return None
    
    async def create_pamphlet_record(self, pamphlet_data: Dict) -> Optional[int]:
        """
        Create a pamphlet record in the database
        
        Args:
            pamphlet_data: Dictionary with church_name, theme, file_path, etc.
            
        Returns:
            ID of inserted record, or None if failed
        """
        if not self.is_enabled():
            return None
        
        try:
            query = """
                INSERT INTO pamphlets 
                (church_name, theme, file_path, file_name, file_size_bytes, llm_call_id, metadata, preview_image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            metadata_json = json.dumps(pamphlet_data.get('metadata', {})) if isinstance(pamphlet_data.get('metadata'), dict) else pamphlet_data.get('metadata')
            
            params = (
                pamphlet_data.get('church_name'),
                pamphlet_data.get('theme'),
                pamphlet_data.get('file_path'),
                pamphlet_data.get('file_name'),
                pamphlet_data.get('file_size_bytes', 0),
                pamphlet_data.get('llm_call_id'),
                metadata_json,
                pamphlet_data.get('preview_image_path')  # Store separately, not in JSON
            )
            
            pamphlet_id = await self._execute_insert(query, params)
            return pamphlet_id
        except Exception as e:
            print(f"⚠️  Failed to create pamphlet record: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def get_pamphlets(self, filters: Optional[Dict] = None) -> Tuple[List[Dict], int]:
        """
        Get list of pamphlets with filters and pagination
        
        Args:
            filters: Dictionary with church_name, theme, limit, offset, sort, order
            
        Returns:
            Tuple of (pamphlets list, total count)
        """
        if not self.is_enabled():
            return [], 0
        
        filters = filters or {}
        church_name = filters.get('church_name')
        theme = filters.get('theme')
        limit = filters.get('limit', 20)
        offset = filters.get('offset', 0)
        sort = filters.get('sort', 'created_at')
        order = filters.get('order', 'desc').upper()
        
        # Build WHERE clause
        where_clauses = ["deleted_at IS NULL"]
        params = []
        
        # SQL injection prevention: Use parameterized queries
        if church_name:
            where_clauses.append("church_name LIKE %s")
            params.append(f"%{church_name}%")
        
        if theme:
            where_clauses.append("theme LIKE %s")
            params.append(f"%{theme}%")
        
        where_sql = " AND ".join(where_clauses)
        
        # Build ORDER BY
        valid_sort_fields = ['created_at', 'church_name', 'theme', 'file_size_bytes']
        sort_field = sort if sort in valid_sort_fields else 'created_at'
        order_clause = "ASC" if order == "ASC" else "DESC"
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM pamphlets WHERE {where_sql}"
        count_result = await self._execute_query(count_query, tuple(params))
        total = count_result[0]['total'] if count_result else 0
        
        # Get paginated results
        # Simplified query - avoid complex subqueries that might cause connection issues
        # We don't select metadata JSON to avoid loading large JSON columns in memory
        query = f"""
            SELECT id, created_at, church_name, theme, file_path, file_name, 
                   file_size_bytes, llm_call_id, preview_image_path
            FROM pamphlets
            WHERE {where_sql}
            ORDER BY {sort_field} {order_clause}
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        results = await self._execute_query(query, tuple(params))
        
        # Format results
        pamphlets = []
        for row in results:
            pamphlet = {
                'id': row['id'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'church_name': row['church_name'],
                'theme': row['theme'],
                'file_name': row['file_name'],
                'file_size_bytes': row['file_size_bytes'],
                'file_size_mb': round(row['file_size_bytes'] / 1024 / 1024, 2),
                'download_url': f'/api/pamphlets/{row["id"]}/download'
            }
            # Set preview_image_url from preview_image_path column (if available)
            if row.get('preview_image_path'):
                pamphlet['preview_image_url'] = f'/api/pamphlets/{row["id"]}/preview'
            pamphlets.append(pamphlet)
        
        return pamphlets, total
    
    async def get_pamphlet_by_id(self, pamphlet_id: int) -> Optional[Dict]:
        """Get a single pamphlet by ID"""
        if not self.is_enabled():
            return None
        
        try:
            query = """
                SELECT id, created_at, church_name, theme, file_path, file_name,
                       file_size_bytes, llm_call_id, metadata, preview_image_path
                FROM pamphlets
                WHERE id = %s AND deleted_at IS NULL
            """
            results = await self._execute_query(query, (pamphlet_id,))
            
            if not results:
                return None
            
            row = results[0]
            pamphlet = {
                'id': row['id'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'church_name': row['church_name'],
                'theme': row['theme'],
                'file_path': row['file_path'],
                'file_name': row['file_name'],
                'file_size_bytes': row['file_size_bytes'],
                'file_size_mb': round(row['file_size_bytes'] / 1024 / 1024, 2),
                'download_url': f'/api/pamphlets/{row["id"]}/download',
                'preview_image_path': row.get('preview_image_path')  # Include directly
            }
            # Set preview_image_url from preview_image_path column (if available)
            if row.get('preview_image_path'):
                pamphlet['preview_image_url'] = f'/api/pamphlets/{row["id"]}/preview'
            
            if row.get('metadata'):
                try:
                    pamphlet['metadata'] = json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
                except:
                    pamphlet['metadata'] = {}
            
            return pamphlet
        except Exception as e:
            print(f"⚠️  Failed to get pamphlet: {e}")
            return None
    
    async def delete_pamphlet(self, pamphlet_id: int) -> bool:
        """Soft delete a pamphlet by setting deleted_at timestamp"""
        if not self.is_enabled():
            return False
        
        try:
            query = """
                UPDATE pamphlets
                SET deleted_at = %s
                WHERE id = %s AND deleted_at IS NULL
            """
            affected = await self._execute_update(query, (datetime.now(), pamphlet_id))
            return affected > 0
        except Exception as e:
            print(f"⚠️  Failed to delete pamphlet: {e}")
            return False
    
    async def get_usage_stats(self, start_date: Optional[datetime] = None, 
                              end_date: Optional[datetime] = None,
                              provider: Optional[str] = None) -> Dict:
        """
        Get usage statistics for LLM API calls
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            provider: Filter by provider name
            
        Returns:
            Dictionary with usage statistics
        """
        if not self.is_enabled():
            return {}
        
        try:
            # Build WHERE clause
            where_clauses = []
            params = []
            
            if start_date:
                where_clauses.append("timestamp >= %s")
                params.append(start_date)
            
            if end_date:
                where_clauses.append("timestamp <= %s")
                params.append(end_date)
            
            if provider:
                where_clauses.append("provider = %s")
                params.append(provider)
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # Get overall stats
            overall_query = f"""
                SELECT 
                    COUNT(*) as total_calls,
                    SUM(total_tokens) as total_tokens,
                    SUM(estimated_cost) as total_cost
                FROM llm_api_calls
                WHERE {where_sql}
            """
            overall_result = await self._execute_query(overall_query, tuple(params))
            overall = overall_result[0] if overall_result else {}
            
            # Get stats by provider
            provider_query = f"""
                SELECT 
                    provider,
                    COUNT(*) as calls,
                    SUM(total_tokens) as tokens,
                    SUM(estimated_cost) as cost
                FROM llm_api_calls
                WHERE {where_sql}
                GROUP BY provider
            """
            provider_results = await self._execute_query(provider_query, tuple(params))
            by_provider = {row['provider']: {
                'calls': row['calls'],
                'tokens': row['tokens'] or 0,
                'cost': float(row['cost'] or 0)
            } for row in provider_results}
            
            # Get stats by endpoint
            endpoint_query = f"""
                SELECT 
                    endpoint,
                    COUNT(*) as calls,
                    AVG(total_tokens) as avg_tokens,
                    AVG(estimated_cost) as avg_cost
                FROM llm_api_calls
                WHERE {where_sql}
                GROUP BY endpoint
            """
            endpoint_results = await self._execute_query(endpoint_query, tuple(params))
            by_endpoint = {row['endpoint']: {
                'calls': row['calls'],
                'avg_tokens': round(float(row['avg_tokens'] or 0)),
                'avg_cost': round(float(row['avg_cost'] or 0), 6)
            } for row in endpoint_results}
            
            return {
                'total_calls': overall.get('total_calls', 0) or 0,
                'total_tokens': overall.get('total_tokens', 0) or 0,
                'total_cost_usd': round(float(overall.get('total_cost', 0) or 0), 6),
                'by_provider': by_provider,
                'by_endpoint': by_endpoint
            }
        except Exception as e:
            print(f"⚠️  Failed to get usage stats: {e}")
            return {}

