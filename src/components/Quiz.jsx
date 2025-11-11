import './Quiz.css'

function Quiz({ questions }) {
  if (!questions || questions.length === 0) {
    return <div className="quiz-empty">No questions available</div>
  }

  return (
    <div className="quiz-container">
      {questions.map((item, index) => (
        <div key={index} className="quiz-item">
          <div className="quiz-question">
            <span className="question-number">{index + 1}.</span>
            <span className="question-text">{item.q}</span>
          </div>
          <div className="quiz-answer-line">
            <span className="answer-label">Answer:</span>
            <div className="answer-dashes">
              {Array(item.a.length).fill('_').map((_, i) => (
                <span key={i} className="dash">_</span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default Quiz


