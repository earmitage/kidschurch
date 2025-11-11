"""
Database Initialization Script
Creates the database schema for Church Games backend
"""

import sys
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the database if it doesn't exist"""
    try:
        host = os.getenv('MYSQL_HOST', 'localhost')
        port = int(os.getenv('MYSQL_PORT', 3306))
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        database = os.getenv('MYSQL_DATABASE', 'kidschurch')
        
        if not user or not password:
            print("❌ MySQL credentials not configured in .env file")
            print("Please set MYSQL_USER and MYSQL_PASSWORD")
            return False
        
        # Connect without database first
        print(f"🔌 Connecting to MySQL at {host}:{port}...")
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        
        cursor = conn.cursor()
        
        # Create database
        print(f"📦 Creating database '{database}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{database}' created or already exists")
        
        # Use database
        cursor.execute(f"USE {database}")
        
        # Create tables
        print("📋 Creating tables...")
        
        # Table: llm_api_calls
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_api_calls (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                provider VARCHAR(50) NOT NULL,
                model VARCHAR(100) NOT NULL,
                endpoint VARCHAR(100) NOT NULL,
                theme VARCHAR(255),
                input_tokens INT DEFAULT 0,
                output_tokens INT DEFAULT 0,
                total_tokens INT DEFAULT 0,
                estimated_cost DECIMAL(10, 6) DEFAULT 0.0,
                response_time_ms INT DEFAULT 0,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                request_id VARCHAR(100),
                INDEX idx_timestamp (timestamp),
                INDEX idx_provider (provider),
                INDEX idx_request_id (request_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 'llm_api_calls' created")
        
        # Table: pamphlets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pamphlets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                church_name VARCHAR(255) NOT NULL,
                theme VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_size_bytes INT DEFAULT 0,
                llm_call_id INT,
                metadata JSON,
                preview_image_path VARCHAR(500) NULL,
                deleted_at DATETIME NULL,
                FOREIGN KEY (llm_call_id) REFERENCES llm_api_calls(id) ON DELETE SET NULL,
                INDEX idx_created_at (created_at),
                INDEX idx_church_name (church_name),
                INDEX idx_theme (theme),
                INDEX idx_deleted_at (deleted_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 'pamphlets' created")
        
        # Add preview_image_path column if it doesn't exist (for existing databases)
        try:
            # Check if column exists first
            cursor.execute("""
                SELECT COUNT(*) as col_count
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'pamphlets' 
                AND COLUMN_NAME = 'preview_image_path'
            """, (database,))
            col_exists = cursor.fetchone()[0] > 0
            
            if not col_exists:
                cursor.execute("""
                    ALTER TABLE pamphlets 
                    ADD COLUMN preview_image_path VARCHAR(500) NULL 
                    AFTER metadata
                """)
                print("✅ Column 'preview_image_path' added")
            else:
                print("✅ Column 'preview_image_path' already exists")
        except Exception as e:
            print(f"⚠️  Could not add preview_image_path column: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ Database initialization completed successfully!")
        print(f"📊 Database: {database}")
        print(f"📁 Tables: llm_api_calls, pamphlets")
        return True
        
    except Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    print("🚀 Church Games Database Initialization")
    print("=" * 50)
    
    success = create_database()
    
    if success:
        print("\n✅ Setup complete! You can now start the backend server.")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check your MySQL configuration.")
        sys.exit(1)

