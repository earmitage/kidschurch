import { useState, useEffect } from 'react'
import { getPamphlets, deletePamphlet, downloadPamphlet } from '../utils/api'
import './PamphletHistory.css'

function PamphletHistory({ onBack }) {
  const [pamphlets, setPamphlets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchChurchName, setSearchChurchName] = useState('')
  const [searchTheme, setSearchTheme] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [deletingId, setDeletingId] = useState(null)
  const [downloadingId, setDownloadingId] = useState(null)
  
  const itemsPerPage = 20

  const loadPamphlets = async (page = 1) => {
    setLoading(true)
    setError('')
    
    try {
      const filters = {
        limit: itemsPerPage,
        offset: (page - 1) * itemsPerPage,
        sort: 'created_at',
        order: 'desc'
      }
      
      if (searchChurchName.trim()) {
        filters.church_name = searchChurchName.trim()
      }
      
      if (searchTheme.trim()) {
        filters.theme = searchTheme.trim()
      }
      
      const data = await getPamphlets(filters)
      
      if (data.success) {
        setPamphlets(data.pamphlets || [])
        setTotal(data.total || 0)
      } else {
        setError('Failed to load pamphlets')
      }
    } catch (err) {
      console.error('Error loading pamphlets:', err)
      setError('Failed to load pamphlets. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPamphlets(currentPage)
  }, [currentPage])

  const handleSearch = () => {
    setCurrentPage(1)
    loadPamphlets(1)
  }

  const handleDelete = async (pamphletId) => {
    if (!confirm('Are you sure you want to delete this pamphlet?')) {
      return
    }

    setDeletingId(pamphletId)
    
    try {
      await deletePamphlet(pamphletId)
      // Reload current page
      await loadPamphlets(currentPage)
    } catch (err) {
      console.error('Error deleting pamphlet:', err)
      alert('Failed to delete pamphlet. Please try again.')
    } finally {
      setDeletingId(null)
    }
  }

  const handleDownload = async (pamphlet) => {
    setDownloadingId(pamphlet.id)
    
    try {
      const blob = await downloadPamphlet(pamphlet.id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = pamphlet.file_name || `${pamphlet.church_name}-${pamphlet.theme}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Error downloading pamphlet:', err)
      alert('Failed to download pamphlet. Please try again.')
    } finally {
      setDownloadingId(null)
    }
  }

  const totalPages = Math.ceil(total / itemsPerPage)

  return (
    <div className="pamphlet-history">
      <div className="history-header">
        <div className="history-title-section">
          <h1>📚 Pamphlet History</h1>
          <button onClick={onBack} className="back-button">
            ← Back to Generator
          </button>
        </div>
        
        <div className="search-section">
          <div className="search-inputs">
            <input
              type="text"
              placeholder="Search by church name..."
              value={searchChurchName}
              onChange={(e) => setSearchChurchName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="search-input"
            />
            <input
              type="text"
              placeholder="Search by theme..."
              value={searchTheme}
              onChange={(e) => setSearchTheme(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="search-input"
            />
            <button onClick={handleSearch} className="search-button">
              🔍 Search
            </button>
            {(searchChurchName || searchTheme) && (
              <button 
                onClick={() => {
                  setSearchChurchName('')
                  setSearchTheme('')
                  setCurrentPage(1)
                  loadPamphlets(1)
                }} 
                className="clear-button"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          <p>⏳ Loading pamphlets...</p>
        </div>
      ) : pamphlets.length === 0 ? (
        <div className="empty-state">
          <p>📭 No pamphlets found</p>
          {searchChurchName || searchTheme ? (
            <p className="empty-hint">Try adjusting your search criteria</p>
          ) : (
            <p className="empty-hint">Generate your first pamphlet to get started!</p>
          )}
        </div>
      ) : (
        <>
          <div className="pamphlets-grid">
            {pamphlets.map((pamphlet) => (
              <div key={pamphlet.id} className="pamphlet-card">
                <div className="pamphlet-card-header">
                  <h3>{pamphlet.church_name}</h3>
                  <span className="pamphlet-theme">{pamphlet.theme}</span>
                </div>
                
                <div className="pamphlet-card-info">
                  <div className="info-row">
                    <span className="info-label">Created:</span>
                    <span className="info-value">
                      {new Date(pamphlet.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">File Size:</span>
                    <span className="info-value">{pamphlet.file_size_mb} MB</span>
                  </div>
                </div>

                <div className="pamphlet-card-actions">
                  <button
                    onClick={() => handleDownload(pamphlet)}
                    disabled={downloadingId === pamphlet.id}
                    className="download-button"
                  >
                    {downloadingId === pamphlet.id ? '⏳ Downloading...' : '⬇️ Download'}
                  </button>
                  <button
                    onClick={() => handleDelete(pamphlet.id)}
                    disabled={deletingId === pamphlet.id}
                    className="delete-button"
                  >
                    {deletingId === pamphlet.id ? '⏳ Deleting...' : '🗑️ Delete'}
                  </button>
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="page-button"
              >
                ← Previous
              </button>
              <span className="page-info">
                Page {currentPage} of {totalPages} ({total} total)
              </span>
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="page-button"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default PamphletHistory


