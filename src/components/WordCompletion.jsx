import './WordCompletion.css'

function WordCompletion({ phrase }) {
  // Split the phrase into words with some blanks
  const words = phrase.split(' ')
  const blanksCount = Math.min(2, Math.floor(words.length / 3))
  
  // Create word completion with some blanks
  const displayWords = words.map((word, index) => {
    // Make every 3rd word a blank (up to blanksCount blanks)
    if (index > 0 && index % 3 === 0 && (index / 3) <= blanksCount) {
      return '_'.repeat(word.length)
    }
    return word
  })

  return (
    <div className="word-completion-container">
      <div className="word-completion-phrase">
        {displayWords.map((word, index) => (
          <span key={index} className={`word-item ${word.startsWith('_') ? 'blank-word' : ''}`}>
            {word}
          </span>
        ))}
      </div>
      <div className="word-completion-hint">
        Fill in the blanks!
      </div>
    </div>
  )
}

export default WordCompletion

