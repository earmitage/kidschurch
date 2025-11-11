import { useState, useEffect } from 'react'
import { generatePamphletContentFromAI, getPamphlets, downloadPamphlet } from '../utils/api'
import PamphletPreview from './PamphletPreview'
import './PamphletGenerator.css'

function PamphletGenerator() {
  const [churchName, setChurchName] = useState('')
  const [theme, setTheme] = useState('')
  const [pamphletContent, setPamphletContent] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  // History state
  const [pamphlets, setPamphlets] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState('')
  const [searchChurchName, setSearchChurchName] = useState('')
  const [searchTheme, setSearchTheme] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [downloadingId, setDownloadingId] = useState(null)
  const [pdfGenerated, setPdfGenerated] = useState(false)
  
  const itemsPerPage = 20

  const handleGenerate = async () => {
    setError('')
    setPdfGenerated(false) // Reset success message when generating new pamphlet
    
    if (!churchName.trim()) {
      setError('Church name is required')
      return
    }
    if (!theme.trim()) {
      setError('Theme is required')
      return
    }
    
    setIsLoading(true)
    try {
      // Generate all pamphlet content in one LLM call
      const aiContent = await generatePamphletContentFromAI(theme)
      
      if (aiContent && aiContent.success) {
        // Add theme to content
        aiContent.theme = theme
        
        // Debug: Log image URLs to verify they're present
        console.log('Generated content keys:', Object.keys(aiContent))
        console.log('Text Image URL present:', !!aiContent.coloringTextImageUrl, 
          aiContent.coloringTextImageUrl ? `${aiContent.coloringTextImageUrl.substring(0, 50)}...` : 'null')
        console.log('Scene Image URL present:', !!aiContent.coloringSceneImageUrl,
          aiContent.coloringSceneImageUrl ? `${aiContent.coloringSceneImageUrl.substring(0, 50)}...` : 'null')
        
        setPamphletContent(aiContent)
      } else {
        setError('Failed to generate pamphlet content. Please try again.')
      }
    } catch (err) {
      console.error('AI generation failed:', err)
      setError('Failed to generate content. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const loadPamphlets = async (page = 1) => {
    setHistoryLoading(true)
    setHistoryError('')
    
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
      
      console.log('📚 Loaded pamphlets:', data)
      
      if (data.success) {
        setPamphlets(data.pamphlets || [])
        setTotal(data.total || 0)
      } else {
        console.error('❌ Failed to load pamphlets - response:', data)
        setHistoryError('Failed to load pamphlets')
      }
    } catch (err) {
      console.error('Error loading pamphlets:', err)
      setHistoryError('Failed to load pamphlets. Please try again.')
    } finally {
      setHistoryLoading(false)
    }
  }

  useEffect(() => {
    loadPamphlets(currentPage)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage])

  const handleSearch = () => {
    setCurrentPage(1)
    loadPamphlets(1)
  }

  const handleViewPamphlet = (pamphlet) => {
    // Open PDF in new tab using the download URL
    const downloadUrl = `${import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001'}${pamphlet.download_url}`
    window.open(downloadUrl, '_blank')
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
    <div className="pamphlet-generator">
      <div className="hero-section">
        <h1>🎨 Kids Church Pamphlet Generator</h1>
        <p className="hero-description">
          Create amazing, printable activity pamphlets for your kids church in seconds! 
          Generate fun mazes, word searches, coloring pages, and quizzes customized to any theme. 
          Perfect for lessons on God's love, Bible stories, prayer, and more. 
          Each pamphlet is professionally formatted to fit exactly 2 A4 pages, ready to print and share!
        </p>
      </div>

      <div className="generator-header">
        <div className="input-section">
          <div className="input-group">
            <label htmlFor="church-name-input">Church Name</label>
            <input
              id="church-name-input"
              type="text"
              placeholder="e.g., 'Rhema Kids Church'"
              value={churchName}
              onChange={(e) => setChurchName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
              className="church-input"
            />
          </div>
          <div className="input-group">
            <label htmlFor="theme-input">Theme</label>
            <input
              id="theme-input"
              type="text"
              placeholder="e.g., 'God's Love', 'The Good Shepherd', 'Prayer Power'"
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
              className="theme-input"
            />
          </div>
          <button onClick={handleGenerate} className="generate-btn" disabled={isLoading}>
            {isLoading ? '⏳ Generating...' : '✨ Generate Pamphlet'}
          </button>
        </div>
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        <div className="theme-suggestions">
          <span className="suggestions-label">✨ Try these themes:</span>
          <span className="suggestion-tag" onClick={() => setTheme("God's Love")}>God's Love</span>
          <span className="suggestion-tag" onClick={() => setTheme('Prayer Power')}>Prayer Power</span>
          <span className="suggestion-tag" onClick={() => setTheme('The Good Shepherd')}>Good Shepherd</span>
          <span className="suggestion-tag" onClick={() => setTheme('Creation')}>Creation</span>
          <span className="suggestion-tag" onClick={() => setTheme('Noah and the Ark')}>Noah's Ark</span>
        </div>
        
        {pamphletContent && (
          <>
            <PamphletPreview 
              content={pamphletContent} 
              theme={theme} 
              churchName={churchName}
              onPdfGenerated={(generated) => {
                setPdfGenerated(generated)
              }}
              onPdfUploaded={() => {
                // Reload pamphlets after successful PDF upload
                loadPamphlets(currentPage)
              }}
            />
            
            {pdfGenerated && (
              <div className="pdf-success-message" style={{
                margin: '20px 0',
                padding: '15px',
                backgroundColor: '#d4edda',
                border: '1px solid #c3e6cb',
                borderRadius: '8px',
                color: '#155724',
                fontSize: '16px',
                textAlign: 'center',
                fontWeight: '500'
              }}>
                ✅ PDF generated and saved! Check your downloads folder.
              </div>
            )}
          </>
        )}
        
        <div className="history-section">
          <h2 className="history-title">📚 Previously Generated Pamphlets</h2>
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

          {historyError && (
            <div className="error-message">
              {historyError}
            </div>
          )}

          {historyLoading ? (
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
                    
                    <div 
                      className="pamphlet-preview" 
                      onClick={() => handleViewPamphlet(pamphlet)}
                      title="Click to view full pamphlet"
                    >
                      {pamphlet.preview_image_url ? (
                        <img 
                          src={`${import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001'}${pamphlet.preview_image_url}`}
                          alt={`${pamphlet.church_name} - ${pamphlet.theme}`}
                          className="preview-image"
                          onError={(e) => {
                            // Fallback to placeholder if image fails to load
                            e.target.style.display = 'none'
                            e.target.nextElementSibling.style.display = 'flex'
                          }}
                        />
                      ) : null}
                      <div className="pamphlet-preview-placeholder" style={{ display: pamphlet.preview_image_url ? 'none' : 'flex' }}>
                        <div className="preview-icon">📄</div>
                        <div className="preview-text">Click to view PDF</div>
                      </div>
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
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDownload(pamphlet)
                        }}
                        disabled={downloadingId === pamphlet.id}
                        className="download-button"
                      >
                        {downloadingId === pamphlet.id ? '⏳ Downloading...' : '⬇️ Download'}
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
      </div>
    </div>
  )
}

export default PamphletGenerator

