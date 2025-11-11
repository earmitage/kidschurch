import { useState, useEffect } from 'react'
import './ColoringText.css'

function ColoringText({ imageUrl, text, theme }) {
  const [imageLoaded, setImageLoaded] = useState(false)
  const [imageError, setImageError] = useState(false)

  useEffect(() => {
    if (imageUrl) {
      setImageLoaded(false)
      setImageError(false)
      // Check if image is already loaded (cached)
      const img = new Image()
      img.onload = () => {
        setImageLoaded(true)
      }
      img.onerror = () => {
        setImageError(true)
        setImageLoaded(false)
      }
      img.src = imageUrl
    } else {
      setImageLoaded(false)
      setImageError(false)
    }
  }, [imageUrl])

  const handleImageLoad = () => {
    setImageLoaded(true)
  }

  const handleImageError = () => {
    setImageError(true)
    setImageLoaded(false)
  }

  if (!imageUrl) {
    return (
      <div className="coloring-text-container">
        <div className="coloring-loading">No coloring text available</div>
      </div>
    )
  }

  if (!imageLoaded && !imageError) {
    return (
      <div className="coloring-text-container">
        <div className="coloring-loading">Loading decorative text...</div>
        <img
          src={imageUrl}
          alt={`Coloring text: ${text}`}
          className="coloring-text-image"
          onLoad={handleImageLoad}
          onError={handleImageError}
          style={{ width: '1px', height: '1px', opacity: 0, position: 'absolute' }}
        />
      </div>
    )
  }

  if (imageError) {
    return (
      <div className="coloring-text-container">
        <div className="coloring-text-fallback">
          <div className="coloring-text-placeholder">{text || 'TEXT'}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="coloring-text-container">
      <img
        src={imageUrl}
        alt={`Coloring text: ${text}`}
        className="coloring-text-image"
        onLoad={handleImageLoad}
        onError={handleImageError}
      />
    </div>
  )
}

export default ColoringText

