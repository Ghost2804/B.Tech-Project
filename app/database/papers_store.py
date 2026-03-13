"""
Papers Database Module
Stores paper metadata locally with easy migration to PostgreSQL
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "papers.db"
DB_PATH.parent.mkdir(exist_ok=True)

def init_papers_db():
    """Initialize papers database with schema"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Create papers table (PostgreSQL-compatible schema)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS papers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doi TEXT UNIQUE,
        title TEXT NOT NULL,
        abstract TEXT,
        authors TEXT,
        year INTEGER,
        venue TEXT,
        source TEXT,
        url TEXT,
        fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
        access_count INTEGER DEFAULT 0
    )
    """)
    
    # Create indices for fast lookup
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_doi ON papers(doi)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_year ON papers(year)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON papers(source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON papers(title)")
    
    conn.commit()
    conn.close()
    print(f"[OK] Papers database initialized at {DB_PATH}")

def store_paper(paper_data):
    """
    Store a single paper in the database
    
    Args:
        paper_data: dict with keys: title, abstract, authors, year, venue, url, doi, source
    
    Returns:
        paper_id if new, None if duplicate
    """
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Check if paper already exists by DOI
    doi = paper_data.get('doi', '')
    if doi:
        cursor.execute("SELECT id FROM papers WHERE doi = ?", (doi,))
        existing = cursor.fetchone()
        if existing:
            # Update access count
            cursor.execute("UPDATE papers SET access_count = access_count + 1 WHERE id = ?", (existing[0],))
            conn.commit()
            conn.close()
            return None  # Already exists
    
    # Store authors as JSON string
    authors = paper_data.get('authors', [])
    if isinstance(authors, list):
        authors_json = json.dumps(authors)
    else:
        authors_json = authors
    
    # Insert new paper
    try:
        cursor.execute("""
        INSERT INTO papers (doi, title, abstract, authors, year, venue, source, url, fetched_at, access_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_data.get('doi', ''),
            paper_data.get('title', ''),
            paper_data.get('abstract', ''),
            authors_json,
            paper_data.get('year'),
            paper_data.get('venue', ''),
            paper_data.get('source', ''),
            paper_data.get('url', ''),
            datetime.now().isoformat(),
            1  # First access
        ))
        
        paper_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return paper_id
        
    except sqlite3.IntegrityError:
        conn.close()
        return None

def store_papers_batch(papers_list):
    """
    Store multiple papers efficiently
    
    Returns:
        (new_count, duplicate_count)
    """
    new_count = 0
    duplicate_count = 0
    
    for paper in papers_list:
        paper_id = store_paper(paper)
        if paper_id:
            new_count += 1
        else:
            duplicate_count += 1
    
    return new_count, duplicate_count

def get_paper_by_doi(doi):
    """Retrieve paper by DOI"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM papers WHERE doi = ?", (doi,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return _row_to_dict(row)
    return None

def get_papers_by_year(year):
    """Get all papers from a specific year"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM papers WHERE year = ? ORDER BY access_count DESC", (year,))
    rows = cursor.fetchall()
    conn.close()
    
    return [_row_to_dict(row) for row in rows]

def get_all_papers(limit=100):
    """Get recent papers (most accessed first)"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT * FROM papers 
    ORDER BY access_count DESC, fetched_at DESC 
    LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [_row_to_dict(row) for row in rows]

def search_papers_by_title(query, limit=20):
    """Search papers by title (for local retrieval)"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT * FROM papers 
    WHERE title LIKE ? OR abstract LIKE ?
    ORDER BY access_count DESC
    LIMIT ?
    """, (f'%{query}%', f'%{query}%', limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [_row_to_dict(row) for row in rows]

def get_stats():
    """Get database statistics"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM papers")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT source) FROM papers")
    sources = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(access_count) FROM papers")
    total_accesses = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_papers': total,
        'unique_sources': sources,
        'total_accesses': total_accesses
    }

def _row_to_dict(row):
    """Convert SQLite row to dictionary"""
    return {
        'id': row[0],
        'doi': row[1],
        'title': row[2],
        'abstract': row[3],
        'authors': json.loads(row[4]) if row[4] else [],
        'year': row[5],
        'venue': row[6],
        'source': row[7],
        'url': row[8],
        'fetched_at': row[9],
        'access_count': row[10]
    }

# Initialize on import
init_papers_db()
