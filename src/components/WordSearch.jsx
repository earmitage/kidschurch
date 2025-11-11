import { useEffect, useRef, useState } from 'react'
import './WordSearch.css'

function WordSearch({ words }) {
  const canvasRef = useRef(null)
  const [gridSize] = useState(20)

  useEffect(() => {
    generateWordSearch()
  }, [words])

  function generateWordSearch() {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const cellSize = 18
    const size = gridSize * cellSize
    
    canvas.width = size
    canvas.height = size

    // Initialize grid with random letters
    const grid = []
    for (let y = 0; y < gridSize; y++) {
      grid[y] = []
      for (let x = 0; x < gridSize; x++) {
        grid[y][x] = String.fromCharCode(65 + Math.floor(Math.random() * 26))
      }
    }

    // Place words in grid
    const placedWords = []
    for (const word of words) {
      const wordUpper = word.toUpperCase().replace(/\s/g, '')
      if (wordUpper.length > gridSize) continue

      let placed = false
      let attempts = 0
      while (!placed && attempts < 50) {
        attempts++
        const direction = Math.floor(Math.random() * 4) // 0: horizontal, 1: vertical, 2: diagonal down-right, 3: diagonal down-left
        const x = Math.floor(Math.random() * (gridSize - (direction === 0 || direction === 2 ? wordUpper.length : 0)))
        const y = Math.floor(Math.random() * (gridSize - (direction === 1 || direction === 2 || direction === 3 ? wordUpper.length : 0)))

        let canPlace = true
        for (let i = 0; i < wordUpper.length; i++) {
          let checkX = x
          let checkY = y

          if (direction === 0) checkX = x + i
          else if (direction === 1) checkY = y + i
          else if (direction === 2) {
            checkX = x + i
            checkY = y + i
          } else if (direction === 3) {
            checkX = x - i
            checkY = y + i
          }

          // Check if cell is already used by another word with a different letter
          const conflict = placedWords.some(placedWord => {
            return placedWord.path.some(point => point.x === checkX && point.y === checkY)
          })
          
          if (conflict) {
            // Check if existing letter matches
            const existingLetter = grid[checkY][checkX]
            if (existingLetter !== wordUpper[i]) {
              canPlace = false
              break
            }
          }
        }

        if (canPlace) {
          const path = []
          for (let i = 0; i < wordUpper.length; i++) {
            let placeX = x
            let placeY = y

            if (direction === 0) placeX = x + i
            else if (direction === 1) placeY = y + i
            else if (direction === 2) {
              placeX = x + i
              placeY = y + i
            } else if (direction === 3) {
              placeX = x - i
              placeY = y + i
            }

            grid[placeY][placeX] = wordUpper[i]
            path.push({ x: placeX, y: placeY })
          }
          placedWords.push({ word: wordUpper, path })
          placed = true
        }
      }
    }

    // Draw grid
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, size, size)

    ctx.font = `${cellSize * 0.6}px Arial`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillStyle = '#000000'

    for (let y = 0; y < gridSize; y++) {
      for (let x = 0; x < gridSize; x++) {
        const xPos = x * cellSize + cellSize / 2
        const yPos = y * cellSize + cellSize / 2
        ctx.fillText(grid[y][x], xPos, yPos)
      }
    }

    // Draw grid lines
    ctx.strokeStyle = '#cccccc'
    ctx.lineWidth = 0.5
    for (let i = 0; i <= gridSize; i++) {
      ctx.beginPath()
      ctx.moveTo(i * cellSize, 0)
      ctx.lineTo(i * cellSize, size)
      ctx.stroke()
      
      ctx.beginPath()
      ctx.moveTo(0, i * cellSize)
      ctx.lineTo(size, i * cellSize)
      ctx.stroke()
    }
  }

  return (
    <div className="word-search-container">
      <canvas ref={canvasRef} className="word-search-canvas"></canvas>
    </div>
  )
}

export default WordSearch

