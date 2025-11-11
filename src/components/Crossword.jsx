import { useEffect, useState } from 'react'
import './Crossword.css'

function Crossword({ theme, words = [] }) {
  const [crossword, setCrossword] = useState(null)

  useEffect(() => {
    if (words.length > 0) {
      const generated = generateCrossword(words)
      setCrossword(generated)
    }
  }, [words])

  if (!crossword) {
    return <div className="crossword-loading">Generating crossword...</div>
  }

  return (
    <div className="crossword-container">
      <div className="crossword-grid">
        {crossword.grid.map((row, rowIdx) => (
          <div key={rowIdx} className="crossword-row">
            {row.map((cell, colIdx) => (
              <div
                key={`${rowIdx}-${colIdx}`}
                className={`crossword-cell ${cell.isBlack ? 'black' : ''} ${cell.hasNumber ? 'numbered' : ''}`}
              >
                {cell.hasNumber && <span className="cell-number">{cell.number}</span>}
              </div>
            ))}
          </div>
        ))}
      </div>
      
      <div className="crossword-clues">
        <div className="clues-section">
          <h5>Across</h5>
          {crossword.across.map((clue, idx) => (
            <div key={idx} className="clue-item">
              <span className="clue-number">{clue.number}.</span>
              <span className="clue-text">{clue.clue}</span>
            </div>
          ))}
        </div>
        
        <div className="clues-section">
          <h5>Down</h5>
          {crossword.down.map((clue, idx) => (
            <div key={idx} className="clue-item">
              <span className="clue-number">{clue.number}.</span>
              <span className="clue-text">{clue.clue}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Simple crossword generator
function generateCrossword(words) {
  const gridSize = 15
  const grid = Array(gridSize).fill(null).map(() => Array(gridSize).fill(null).map(() => '_'))
  const placedWords = []
  
  // Place first word in the center
  if (!words || words.length === 0) {
    return { grid: [], across: [], down: [] }
  }
  
  const firstWord = words[0]
  const startRow = Math.floor(gridSize / 2)
  const startCol = Math.floor((gridSize - firstWord.length) / 2)
  
  for (let i = 0; i < firstWord.length; i++) {
    grid[startRow][startCol + i] = firstWord[i]
  }
  
  placedWords.push({
    text: firstWord,
    row: startRow,
    col: startCol,
    vertical: false
  })
  
  // Try to place remaining words
  for (let wordIdx = 1; wordIdx < Math.min(words.length, 8); wordIdx++) {
    const word = words[wordIdx]
    let placed = false
    
    // Try to find an intersection
    for (let i = 0; i < word.length && !placed; i++) {
      const letter = word[i]
      
      // Look for this letter in placed words
      for (const placedWord of placedWords) {
        for (let j = 0; j < placedWord.text.length; j++) {
          if (placedWord.text[j] === letter) {
            let newRow, newCol
            
            if (placedWord.vertical) {
              newRow = placedWord.row + j
              newCol = placedWord.col - i
            } else {
              newRow = placedWord.row - i
              newCol = placedWord.col + j
            }
            
            if (canPlaceWord(grid, word, newRow, newCol, !placedWord.vertical)) {
              placeWord(grid, word, newRow, newCol, !placedWord.vertical)
              placedWords.push({
                text: word,
                row: newRow,
                col: newCol,
                vertical: !placedWord.vertical
              })
              placed = true
              break
            }
          }
        }
        if (placed) break
      }
    }
  }
  
  // Convert to display format
  const displayGrid = grid.map(row => 
    row.map(cell => ({
      letter: cell === '_' ? '' : cell,
      isBlack: cell === '_',
      hasNumber: false,
      number: null
    }))
  )
  
  // Add numbers and build clues
  let clueNum = 1
  const across = []
  const down = []
  
  for (const word of placedWords) {
    const gridRow = word.row
    const gridCol = word.col
    
    displayGrid[gridRow][gridCol].hasNumber = true
    displayGrid[gridRow][gridCol].number = clueNum
    
    const clue = getClue(word.text)
    if (word.vertical) {
      down.push({ number: clueNum, clue })
    } else {
      across.push({ number: clueNum, clue })
    }
    clueNum++
  }
  
  return { grid: displayGrid, across, down }
}

function canPlaceWord(grid, word, row, col, vertical) {
  const gridSize = grid.length
  
  if (vertical) {
    if (row < 0 || row + word.length > gridSize) return false
    for (let i = 0; i < word.length; i++) {
      const cell = grid[row + i][col]
      if (cell !== '_' && cell !== word[i]) return false
      if (cell !== '_') continue
      
      // Check adjacent cells
      if (col > 0 && grid[row + i][col - 1] !== '_') return false
      if (col < gridSize - 1 && grid[row + i][col + 1] !== '_') return false
      if (i === 0 && row > 0 && grid[row - 1][col] !== '_') return false
      if (i === word.length - 1 && row + word.length < gridSize && grid[row + word.length][col] !== '_') return false
    }
  } else {
    if (col < 0 || col + word.length > gridSize) return false
    for (let i = 0; i < word.length; i++) {
      const cell = grid[row][col + i]
      if (cell !== '_' && cell !== word[i]) return false
      if (cell !== '_') continue
      
      // Check adjacent cells
      if (row > 0 && grid[row - 1][col + i] !== '_') return false
      if (row < gridSize - 1 && grid[row + 1][col + i] !== '_') return false
      if (i === 0 && col > 0 && grid[row][col - 1] !== '_') return false
      if (i === word.length - 1 && col + word.length < gridSize && grid[row][col + word.length] !== '_') return false
    }
  }
  
  return true
}

function placeWord(grid, word, row, col, vertical) {
  if (vertical) {
    for (let i = 0; i < word.length; i++) {
      grid[row + i][col] = word[i]
    }
  } else {
    for (let i = 0; i < word.length; i++) {
      grid[row][col + i] = word[i]
    }
  }
}

function getClue(word) {
  const clues = {
    'NOAH': 'Built the big boat',
    'ARK': 'Big floating boat',
    'RAINBOW': 'Colors in the sky',
    'ANIMALS': 'In the big boat',
    'WATER': 'Falls from sky',
    'DOVE': 'White bird',
    'PROMISE': 'God said yes',
    'FLOOD': 'Lots of rain',
    'RAIN': 'Falls from clouds',
    'BOAT': 'Floats on water',
    'SAVE': 'Help others',
    'PAIR': 'Two together',
    'GOD': 'Made everything',
    'LOVE': 'Big hug feeling',
    'JESUS': 'God\'s son',
    'PRAY': 'Talk to God',
    'BIBLE': 'God\'s book',
    'FAITH': 'Believe in God'
  }
  
  return clues[word] || `${word} (starts with ${word.charAt(0)})`
}

export default Crossword
