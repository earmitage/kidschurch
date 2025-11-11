import { useEffect, useRef, useState } from 'react'
import './Maze.css'

function Maze() {
  const canvasRef = useRef(null)
  const [mazeKey, setMazeKey] = useState(0)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const size = 450
    const cellSize = 18
    const cols = Math.floor(size / cellSize)
    const rows = Math.floor(size / cellSize)

    canvas.width = size
    canvas.height = size

    // Generate a simple maze using recursive backtracking
    const grid = generateMaze(cols, rows)
    drawMaze(ctx, grid, cellSize, cols, rows, size)
  }, [mazeKey])

  // Regenerate maze on click
  const handleCanvasClick = () => {
    setMazeKey(prev => prev + 1)
  }

  function generateMaze(cols, rows) {
    // Initialize grid - all walls
    const grid = []
    for (let y = 0; y < rows; y++) {
      grid[y] = []
      for (let x = 0; x < cols; x++) {
        grid[y][x] = { top: true, right: true, bottom: true, left: true, visited: false }
      }
    }

    // Recursive backtracking
    const stack = []
    const current = { x: 0, y: 0 }
    grid[current.y][current.x].visited = true
    stack.push({ ...current })

    while (stack.length > 0) {
      const neighbors = []
      
      // Check neighbors (top, right, bottom, left)
      if (current.y > 0 && !grid[current.y - 1][current.x].visited) {
        neighbors.push({ x: current.x, y: current.y - 1, wall: 'top' })
      }
      if (current.x < cols - 1 && !grid[current.y][current.x + 1].visited) {
        neighbors.push({ x: current.x + 1, y: current.y, wall: 'right' })
      }
      if (current.y < rows - 1 && !grid[current.y + 1][current.x].visited) {
        neighbors.push({ x: current.x, y: current.y + 1, wall: 'bottom' })
      }
      if (current.x > 0 && !grid[current.y][current.x - 1].visited) {
        neighbors.push({ x: current.x - 1, y: current.y, wall: 'left' })
      }

      if (neighbors.length > 0) {
        const next = neighbors[Math.floor(Math.random() * neighbors.length)]
        
        // Remove wall between current and next
        if (next.wall === 'top') {
          grid[current.y][current.x].top = false
          grid[next.y][next.x].bottom = false
        } else if (next.wall === 'right') {
          grid[current.y][current.x].right = false
          grid[next.y][next.x].left = false
        } else if (next.wall === 'bottom') {
          grid[current.y][current.x].bottom = false
          grid[next.y][next.x].top = false
        } else if (next.wall === 'left') {
          grid[current.y][current.x].left = false
          grid[next.y][next.x].right = false
        }

        grid[next.y][next.x].visited = true
        stack.push({ ...current })
        current.x = next.x
        current.y = next.y
      } else {
        const prev = stack.pop()
        current.x = prev.x
        current.y = prev.y
      }
    }

    // Open entrance at top-left
    grid[0][0].top = false
    
    // Open exit at bottom-right  
    grid[rows - 1][cols - 1].bottom = false

    return grid
  }

  function drawMaze(ctx, grid, cellSize, cols, rows, size) {
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, size, size)

    ctx.strokeStyle = '#2c3e50'
    ctx.lineWidth = 2

    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const cell = grid[y][x]
        const xPos = x * cellSize
        const yPos = y * cellSize

        if (cell.top) {
          ctx.beginPath()
          ctx.moveTo(xPos, yPos)
          ctx.lineTo(xPos + cellSize, yPos)
          ctx.stroke()
        }
        if (cell.right) {
          ctx.beginPath()
          ctx.moveTo(xPos + cellSize, yPos)
          ctx.lineTo(xPos + cellSize, yPos + cellSize)
          ctx.stroke()
        }
        if (cell.bottom) {
          ctx.beginPath()
          ctx.moveTo(xPos + cellSize, yPos + cellSize)
          ctx.lineTo(xPos, yPos + cellSize)
          ctx.stroke()
        }
        if (cell.left) {
          ctx.beginPath()
          ctx.moveTo(xPos, yPos + cellSize)
          ctx.lineTo(xPos, yPos)
          ctx.stroke()
        }
      }
    }

    // Draw start marker
    ctx.fillStyle = '#27ae60'
    ctx.fillRect(cellSize / 4, cellSize / 4, cellSize / 2, cellSize / 2)

    // Draw end marker (treasure)
    ctx.fillStyle = '#f39c12'
    ctx.beginPath()
    ctx.arc(
      (cols - 1) * cellSize + cellSize / 2,
      (rows - 1) * cellSize + cellSize / 2,
      cellSize / 3,
      0,
      2 * Math.PI
    )
    ctx.fill()
  }

  return (
    <div className="maze-container">
      <canvas 
        ref={canvasRef} 
        className="maze-canvas"
        onClick={handleCanvasClick}
        title="Click to generate a new maze!"
        style={{ cursor: 'pointer' }}
      ></canvas>
      <p className="maze-hint">Click the maze to generate a new one!</p>
    </div>
  )
}

export default Maze

