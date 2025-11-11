import { useEffect, useRef } from 'react'
import './TicTacToe.css'

function TicTacToe() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const size = 120 // Reduced size to fit better
    canvas.width = size
    canvas.height = size

    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, size, size)

    ctx.strokeStyle = '#2c3e50'
    ctx.lineWidth = 2

    // Draw grid
    const cellSize = size / 3
    
    // Vertical lines
    for (let i = 1; i < 3; i++) {
      ctx.beginPath()
      ctx.moveTo(i * cellSize, 0)
      ctx.lineTo(i * cellSize, size)
      ctx.stroke()
    }
    
    // Horizontal lines
    for (let i = 1; i < 3; i++) {
      ctx.beginPath()
      ctx.moveTo(0, i * cellSize)
      ctx.lineTo(size, i * cellSize)
      ctx.stroke()
    }

    // Add label at bottom
    ctx.font = '12px Arial'
    ctx.fillStyle = '#666'
    ctx.textAlign = 'center'
    ctx.fillText('Tic Tac Toe!', size / 2, size - 5)
  }, [])

  return (
    <div className="tictactoe-container">
      <canvas ref={canvasRef} className="tictactoe-canvas"></canvas>
    </div>
  )
}

export default TicTacToe

