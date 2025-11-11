/**
 * Backend API client for Church Games
 */

// Determine API base URL based on environment variables
// Set via .env.production (for production) or .env.development (for dev)
// Vite automatically loads .env files based on --mode flag
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001'

/**
 * Generate a coloring image using AI
 * @param {string} prompt - Image description
 * @param {string} theme - Biblical theme
 * @returns {Promise<string>} Image URL
 */
export async function generateColoringImage(prompt, theme) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/generate-coloring-image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        theme
      })
    })

    if (!response.ok) {
      throw new Error('Failed to generate image')
    }

    const data = await response.json()
    return data.image_url
  } catch (error) {
    console.error('Error generating coloring image:', error)
    // Return null to fallback to canvas rendering
    return null
  }
}

/**
 * Upload a PDF pamphlet to local storage
 * @param {Blob} pdfBlob - PDF file blob
 * @param {Object} metadata - Metadata (church_name, theme, llm_call_id, etc.)
 * @returns {Promise<Object>} Upload result with pamphlet_id and download_url
 */
export async function uploadPdf(pdfBlob, metadata = {}) {
  try {
    const formData = new FormData()
    formData.append('pdf', pdfBlob, 'pamphlet.pdf')
    formData.append('metadata', JSON.stringify(metadata))

    const response = await fetch(`${API_BASE_URL}/api/upload-pdf`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.error || 'Failed to upload PDF')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error uploading PDF:', error)
    throw error
  }
}

/**
 * Get list of pamphlets with filters
 * @param {Object} filters - Filter options (church_name, theme, limit, offset, sort, order)
 * @returns {Promise<Object>} List of pamphlets with pagination info
 */
export async function getPamphlets(filters = {}) {
  try {
    const params = new URLSearchParams()
    
    if (filters.church_name) params.append('church_name', filters.church_name)
    if (filters.theme) params.append('theme', filters.theme)
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.offset) params.append('offset', filters.offset.toString())
    if (filters.sort) params.append('sort', filters.sort)
    if (filters.order) params.append('order', filters.order)

    const response = await fetch(`${API_BASE_URL}/api/pamphlets?${params.toString()}`)
    
    if (!response.ok) {
      throw new Error('Failed to fetch pamphlets')
    }

    return await response.json()
  } catch (error) {
    console.error('Error fetching pamphlets:', error)
    throw error
  }
}

/**
 * Get a single pamphlet by ID
 * @param {number} pamphletId - Pamphlet ID
 * @returns {Promise<Object>} Pamphlet data
 */
export async function getPamphlet(pamphletId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/pamphlets/${pamphletId}`)
    
    if (!response.ok) {
      throw new Error('Failed to fetch pamphlet')
    }

    const data = await response.json()
    return data.pamphlet
  } catch (error) {
    console.error('Error fetching pamphlet:', error)
    throw error
  }
}

/**
 * Download a PDF pamphlet
 * @param {number} pamphletId - Pamphlet ID
 * @returns {Promise<Blob>} PDF blob
 */
export async function downloadPamphlet(pamphletId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/pamphlets/${pamphletId}/download`)
    
    if (!response.ok) {
      throw new Error('Failed to download pamphlet')
    }

    return await response.blob()
  } catch (error) {
    console.error('Error downloading pamphlet:', error)
    throw error
  }
}

/**
 * Delete a pamphlet (soft delete)
 * @param {number} pamphletId - Pamphlet ID
 * @returns {Promise<Object>} Delete result
 */
export async function deletePamphlet(pamphletId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/pamphlets/${pamphletId}`, {
      method: 'DELETE'
    })
    
    if (!response.ok) {
      throw new Error('Failed to delete pamphlet')
    }

    return await response.json()
  } catch (error) {
    console.error('Error deleting pamphlet:', error)
    throw error
  }
}

/**
 * Get usage statistics
 * @param {Object} options - Options (start_date, end_date, provider)
 * @returns {Promise<Object>} Usage statistics
 */
export async function getUsageStats(options = {}) {
  try {
    const params = new URLSearchParams()
    
    if (options.start_date) params.append('start_date', options.start_date)
    if (options.end_date) params.append('end_date', options.end_date)
    if (options.provider) params.append('provider', options.provider)

    const response = await fetch(`${API_BASE_URL}/api/usage/stats?${params.toString()}`)
    
    if (!response.ok) {
      throw new Error('Failed to fetch usage stats')
    }

    return await response.json()
  } catch (error) {
    console.error('Error fetching usage stats:', error)
    throw error
  }
}

/**
 * Check backend health
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    return await response.json()
  } catch (error) {
    console.error('Backend health check failed:', error)
    return null
  }
}

/**
 * Get backend configuration
 * @returns {Promise<Object>} Configuration
 */
export async function getConfig() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/config`)
    return await response.json()
  } catch (error) {
    console.error('Failed to get config:', error)
    return null
  }
}

/**
 * Generate all pamphlet content in one LLM call
 * @param {string} theme - Biblical theme
 * @returns {Promise<Object>} All pamphlet content
 */
export async function generatePamphletContentFromAI(theme) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/generate-pamphlet-content`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        theme
      })
    })

    if (!response.ok) {
      throw new Error('Failed to generate pamphlet content')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error generating pamphlet content:', error)
    throw error
  }
}

