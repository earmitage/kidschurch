import { useState, useEffect } from 'react'
import './ColoringScene.css'

function ColoringScene({ imageUrl, theme }) {
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
      <div className="coloring-scene-container">
        <div className="coloring-loading">No coloring scene available</div>
      </div>
    )
  }

  if (!imageLoaded && !imageError) {
    return (
      <div className="coloring-scene-container">
        <div className="coloring-loading">Loading coloring scene...</div>
        <img
          src={imageUrl}
          alt={`Coloring scene: ${theme}`}
          className="coloring-scene-image"
          onLoad={handleImageLoad}
          onError={handleImageError}
          style={{ width: '1px', height: '1px', opacity: 0, position: 'absolute' }}
        />
      </div>
    )
  }

  if (imageError) {
    return (
      <div className="coloring-scene-container">
        <div className="coloring-scene-fallback">
          <div className="coloring-scene-placeholder">
            {theme} Scene
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="coloring-scene-container">
      <img
        src={imageUrl}
        alt={`Coloring scene: ${theme}`}
        className="coloring-scene-image"
        onLoad={handleImageLoad}
        onError={handleImageError}
      />
    </div>
  )
}

export default ColoringScene

