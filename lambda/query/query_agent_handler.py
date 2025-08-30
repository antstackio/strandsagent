from strands import Agent
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from strands.models.openai import OpenAIModel
from typing import Dict, Any
from datetime import datetime, timedelta
from contextlib import contextmanager
import logging

# Configure logging for strands and this module
logging.getLogger("strands").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configure logging format
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_database_credentials():
    """Get database credentials from environment variables."""
    logger.debug("Retrieving database credentials from environment variables")
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise Exception(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    creds = {
        'host': os.environ['DB_HOST'],
        'database': os.environ['DB_NAME'],
        'user': os.environ['DB_USER'],
        'password': os.environ['DB_PASSWORD'],
        'port': os.environ.get('DB_PORT', '5432')
    }
    logger.debug(f"Database credentials loaded for host: {creds['host']}, database: {creds['database']}")
    return creds

def get_openai_api_key():
    """Get OpenAI API key from environment variables."""
    logger.debug("Retrieving OpenAI API key from environment variables")
    api_key = os.environ.get('OPENAI_KEY')
    if not api_key:
        logger.error("OpenAI API key not found in environment variables")
        raise Exception("OpenAI API key not found. Set OPENAI_API_KEY or OPENAI_KEY environment variable.")
    logger.debug("OpenAI API key successfully retrieved")
    return api_key

@contextmanager
def get_db_connection():
    """Database connection context manager."""
    conn = None
    try:
        logger.debug("Establishing database connection")
        creds = get_database_credentials()
        conn = psycopg2.connect(
            host=creds['host'],
            port=creds['port'],
            database=creds['database'],
            user=creds['user'],
            password=creds['password'],
            sslmode='require',
            connect_timeout=10,
            cursor_factory=RealDictCursor
        )
        logger.debug(f"Database connection established successfully to {creds['host']}:{creds['port']}/{creds['database']}")
        yield conn
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise Exception(f"Database connection failed: {str(e)}")
    finally:
        if conn:
            logger.debug("Closing database connection")
            conn.close()

def execute_revenue_query(start_date: str = None) -> Dict[str, Any]:
    """Execute revenue summary query."""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        logger.debug(f"Using default start_date: {start_date}")
    else:
        logger.debug(f"Using provided start_date: {start_date}")
    
    logger.debug("Executing revenue summary query")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = """
            SELECT 
                DATE(o.created_at) as order_date,
                COUNT(o.id) as order_count,
                SUM(o.total) as daily_revenue,
                AVG(o.total) as avg_order_value,
                COUNT(DISTINCT o.user_id) as unique_customers
            FROM orders o
            WHERE o.status IN ('completed', 'delivered')
              AND o.created_at >= %s
            GROUP BY DATE(o.created_at)
            ORDER BY order_date DESC
            LIMIT 30
            """
            
            cursor.execute(sql, [start_date])
            rows = cursor.fetchall()
            logger.debug(f"Revenue query returned {len(rows)} rows")
            
            total_revenue = sum(float(row['daily_revenue'] or 0) for row in rows)
            total_orders = sum(row['order_count'] or 0 for row in rows)
            logger.debug(f"Calculated total revenue: ${total_revenue:,.2f}, total orders: {total_orders}")
            
            return {
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'average_daily_revenue': total_revenue / len(rows) if rows else 0,
                'days_analyzed': len(rows),
                'daily_data': [
                    {
                        'date': row['order_date'].isoformat(),
                        'revenue': float(row['daily_revenue'] or 0),
                        'orders': row['order_count'] or 0,
                        'avg_order_value': float(row['avg_order_value'] or 0)
                    } for row in rows[:7]  # Last 7 days detail
                ]
            }

def execute_product_query(start_date: str = None, category: str = None) -> Dict[str, Any]:
    """Execute product sales query."""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        logger.debug(f"Using default start_date for products: {start_date}")
    else:
        logger.debug(f"Using provided start_date for products: {start_date}")
    
    if category:
        logger.debug(f"Filtering by category: {category}")
    
    logger.debug("Executing product sales query")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = """
            SELECT 
                p.name,
                p.category,
                SUM(oi.quantity) as total_sold,
                SUM(oi.quantity * (oi.price - COALESCE(oi.discount_amount, 0))) as total_revenue,
                AVG(oi.price) as avg_price,
                COUNT(DISTINCT o.user_id) as unique_buyers
            FROM products p
            JOIN order_items oi ON p.id = oi.product_id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status IN ('completed', 'delivered')
              AND o.created_at >= %s
            """
            
            params = [start_date]
            if category:
                sql += " AND p.category = %s"
                params.append(category)
            
            sql += """
            GROUP BY p.id, p.name, p.category
            ORDER BY total_revenue DESC
            LIMIT 15
            """
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            logger.debug(f"Product query returned {len(rows)} products")
            
            total_revenue = sum(float(row['total_revenue'] or 0) for row in rows)
            total_units = sum(row['total_sold'] or 0 for row in rows)
            logger.debug(f"Product totals - revenue: ${total_revenue:,.2f}, units sold: {total_units}")
            
            return {
                'total_products_analyzed': len(rows),
                'total_revenue': total_revenue,
                'total_units_sold': total_units,
                'top_products': [
                    {
                        'name': row['name'],
                        'category': row['category'],
                        'revenue': float(row['total_revenue'] or 0),
                        'units_sold': row['total_sold'] or 0,
                        'avg_price': float(row['avg_price'] or 0)
                    } for row in rows[:10]
                ]
            }

def execute_customer_query(start_date: str = None, min_amount: float = None) -> Dict[str, Any]:
    """Execute customer orders query."""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        logger.debug(f"Using default start_date for customers: {start_date}")
    else:
        logger.debug(f"Using provided start_date for customers: {start_date}")
    
    if min_amount:
        logger.debug(f"Filtering by minimum amount: ${min_amount}")
    
    logger.debug("Executing customer orders query")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = """
            SELECT 
                o.id,
                o.total,
                o.status,
                o.created_at,
                u.first_name || ' ' || u.last_name as customer_name,
                u.email,
                COUNT(oi.id) as item_count
            FROM orders o
            JOIN users u ON o.user_id = u.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.created_at >= %s
            """
            
            params = [start_date]
            if min_amount:
                sql += " AND o.total >= %s"
                params.append(min_amount)
            
            sql += """
            GROUP BY o.id, o.total, o.status, o.created_at, u.first_name, u.last_name, u.email
            ORDER BY o.total DESC
            LIMIT 20
            """
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            logger.debug(f"Customer query returned {len(rows)} orders")
            
            total_value = sum(float(row['total'] or 0) for row in rows)
            logger.debug(f"Customer orders total value: ${total_value:,.2f}")
            
            return {
                'total_orders_analyzed': len(rows),
                'total_value': total_value,
                'average_order_value': total_value / len(rows) if rows else 0,
                'high_value_orders': [
                    {
                        'order_id': row['id'],
                        'customer_name': row['customer_name'],
                        'total': float(row['total'] or 0),
                        'status': row['status'],
                        'date': row['created_at'].strftime('%Y-%m-%d'),
                        'items': row['item_count'] or 0
                    } for row in rows[:10]
                ]
            }

def analyze_business_request(user_prompt: str) -> Dict[str, Any]:
    """Analyze user request and execute appropriate queries."""
    
    logger.debug(f"Analyzing business request: {user_prompt}")
    
    # Determine what data to fetch based on the prompt
    prompt_lower = user_prompt.lower()
    
    results = {
        'request': user_prompt,
        'queries_executed': [],
        'data': {}
    }
    
    # Execute relevant queries based on keywords
    if any(word in prompt_lower for word in ['revenue', 'sales', 'performance', 'trends', 'summary', 'business']):
        logger.debug("Revenue-related keywords detected, executing revenue query")
        results['data']['revenue'] = execute_revenue_query()
        results['queries_executed'].append('revenue_summary')
    
    if any(word in prompt_lower for word in ['product', 'bestseller', 'category', 'inventory', 'items']):
        logger.debug("Product-related keywords detected, executing product query")
        results['data']['products'] = execute_product_query()
        results['queries_executed'].append('product_sales')
    
    if any(word in prompt_lower for word in ['customer', 'order', 'high value', 'vip', 'spending']):
        logger.debug("Customer-related keywords detected, executing customer query")
        # Look for amount mentions
        min_amount = None
        if '$' in user_prompt or 'over' in prompt_lower:
            # Try to extract amount (simple regex could be added here)
            if '200' in user_prompt:
                min_amount = 200
                logger.debug("Detected minimum amount filter: $200")
            elif '500' in user_prompt:
                min_amount = 500
                logger.debug("Detected minimum amount filter: $500")
        
        results['data']['customers'] = execute_customer_query(min_amount=min_amount)
        results['queries_executed'].append('customer_orders')
    
    # If no specific queries matched, get a general business overview
    if not results['queries_executed']:
        logger.debug("No specific query detected, running general business overview")
        results['data']['revenue'] = execute_revenue_query()
        results['data']['products'] = execute_product_query()
        results['queries_executed'] = ['revenue_summary', 'product_sales']
    
    logger.debug(f"Completed analysis with queries: {results['queries_executed']}")
    return results

def generate_business_insights(query_results: Dict[str, Any], user_prompt: str) -> str:
    """Generate business insights using the agent with real data."""
    
    try:
        logger.debug("Starting business insights generation")
        openai_api_key = get_openai_api_key()
        
        logger.debug("Initializing OpenAI model for insights generation")
        model = OpenAIModel(
            client_args={"api_key": openai_api_key},
            model_id="gpt-4o",
            params={"max_tokens": 2000, "temperature": 0.3}
        )
        logger.debug("OpenAI model initialized successfully")
        
        # Create agent for analysis (no tools needed, just analysis)
        logger.debug("Creating business analyst agent")
        analyst = Agent(
            system_prompt="""You are a senior business analyst. Analyze the provided data and give actionable insights.
            
            Focus on:
            - Key trends and patterns
            - Performance highlights and concerns  
            - Actionable recommendations
            - Executive-level summary
            
            Be specific with numbers and provide context.""",
            model=model
        )
        
        # Format the data for analysis
        data_summary = f"""
        User Request: {user_prompt}
        
        Queries Executed: {', '.join(query_results['queries_executed'])}
        
        DATA ANALYSIS:
        """
        
        if 'revenue' in query_results['data']:
            rev_data = query_results['data']['revenue']
            data_summary += f"""
        
        REVENUE PERFORMANCE:
        - Total Revenue ({rev_data['days_analyzed']} days): ${rev_data['total_revenue']:,.2f}
        - Total Orders: {rev_data['total_orders']:,}
        - Average Daily Revenue: ${rev_data['average_daily_revenue']:,.2f}
        
        Recent Daily Performance:
        """
            for day in rev_data['daily_data'][:5]:
                data_summary += f"  • {day['date']}: ${day['revenue']:,.2f} ({day['orders']} orders)\n"
        
        if 'products' in query_results['data']:
            prod_data = query_results['data']['products']
            data_summary += f"""
        
        PRODUCT PERFORMANCE:
        - Products Analyzed: {prod_data['total_products_analyzed']}
        - Total Revenue: ${prod_data['total_revenue']:,.2f}
        - Total Units Sold: {prod_data['total_units_sold']:,}
        
        Top Products:
        """
            for prod in prod_data['top_products'][:5]:
                data_summary += f"  • {prod['name']} ({prod['category']}): ${prod['revenue']:,.2f} - {prod['units_sold']} units\n"
        
        if 'customers' in query_results['data']:
            cust_data = query_results['data']['customers']
            data_summary += f"""
        
        CUSTOMER ANALYSIS:
        - Orders Analyzed: {cust_data['total_orders_analyzed']}
        - Total Value: ${cust_data['total_value']:,.2f}
        - Average Order Value: ${cust_data['average_order_value']:,.2f}
        
        High-Value Orders:
        """
            for order in cust_data['high_value_orders'][:5]:
                data_summary += f"  • Order #{order['order_id']}: {order['customer_name']} - ${order['total']:,.2f}\n"
        
        data_summary += "\n\nPlease provide comprehensive business insights and recommendations based on this data."
        
        # Get analysis from the agent
        logger.debug("Invoking analyst agent for insights generation")
        analysis = analyst(data_summary)
        logger.debug("Business insights generated successfully")
        
        return str(analysis)
        
    except Exception as e:
        logger.error(f"Error generating business insights: {str(e)}")
        return f"Data retrieved successfully, but analysis failed: {str(e)}\n\nRaw data: {json.dumps(query_results, indent=2, default=str)}"

def agentic_handler(event: Dict[str, Any], _context) -> Dict[str, Any]:
    """Lambda handler that actually executes database queries and provides insights."""
    
    try:
        user_prompt = event.get('prompt', 'Show me a business performance summary')
        
        logger.debug(f"Lambda handler invoked with prompt: {user_prompt}")
        logger.debug(f"Full event: {json.dumps(event, default=str)}")
        
        # Step 1: Execute database queries based on the request
        logger.debug("Step 1: Analyzing business request and executing queries")
        query_results = analyze_business_request(user_prompt)
        
        logger.debug(f"Queries executed: {query_results['queries_executed']}")
        logger.debug(f"Data points collected: {len(query_results.get('data', {}))}")
        
        # Step 2: Generate insights using the agent with real data
        logger.debug("Step 2: Generating business insights from query results")
        insights = generate_business_insights(query_results, user_prompt)
        
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': insights,
                'queries_executed': query_results['queries_executed'],
                'timestamp': datetime.utcnow().isoformat(),
                'data_points': len(query_results.get('data', {}))
            })
        }
        
        logger.debug(f"Lambda handler completed successfully with status code: {response['statusCode']}")
        return response
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}", exc_info=True)
        error_response = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
        logger.error(f"Lambda handler failed with status code: {error_response['statusCode']}")
        return error_response
