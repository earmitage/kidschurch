import { useRef, useState, useEffect } from 'react'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import WordSearch from './WordSearch'
import Maze from './Maze'
import Quiz from './Quiz'
import TicTacToe from './TicTacToe'
import WordCompletion from './WordCompletion'
import Crossword from './Crossword'
import ColoringActivity from './ColoringActivity'
import { uploadPdf } from '../utils/api'
import './PamphletPreview.css'

function PamphletPreview({ content, theme, churchName, onPdfUploaded, onPdfGenerated }) {
  const pamphletRef = useRef(null)
  const displayChurchName = churchName.toUpperCase()
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState('')
  const [pdfGenerated, setPdfGenerated] = useState(false)

  const exportToPDF = async () => {
    if (pdfGenerated) return // Prevent double generation
    
    try {
      setError('')
      setIsExporting(true)
      const element = pamphletRef.current
      
      // Hide interactive elements before capturing
      const hintElements = element.querySelectorAll('.maze-hint')
      const originalDisplay = []
      hintElements.forEach((el, index) => {
        originalDisplay[index] = el.style.display
        el.style.display = 'none'
      })
      
      const pages = element.querySelectorAll('.page')
      const pdf = new jsPDF('p', 'mm', 'a4')
      const pdfWidth = pdf.internal.pageSize.getWidth()
      const pdfHeight = pdf.internal.pageSize.getHeight()

      for (let i = 0; i < pages.length; i++) {
        if (i > 0) {
          pdf.addPage()
        }
        
        const pageElement = pages[i]
        const canvas = await html2canvas(pageElement, {
          scale: 2,
          useCORS: true,
          logging: false,
          backgroundColor: '#ffffff',
        })

        const imgData = canvas.toDataURL('image/png')
        const imgWidth = canvas.width
        const imgHeight = canvas.height
        const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight)
        const imgScaledWidth = imgWidth * ratio
        const imgScaledHeight = imgHeight * ratio

        // Center the image on the page
        const xOffset = (pdfWidth - imgScaledWidth) / 2
        const yOffset = (pdfHeight - imgScaledHeight) / 2

        pdf.addImage(imgData, 'PNG', xOffset, yOffset, imgScaledWidth, imgScaledHeight, undefined, 'FAST')
      }
      
      // Restore hidden elements
      hintElements.forEach((el, index) => {
        el.style.display = originalDisplay[index] || ''
      })
      
      // Generate PDF blob
      const pdfBlob = pdf.output('blob')
      
      // Save locally
      pdf.save(`${churchName.replace(/\s+/g, '-')}-${theme.replace(/\s+/g, '-')}-Pamphlet.pdf`)
      
      // Upload to backend for storage and tracking
      try {
        const uploadResult = await uploadPdf(pdfBlob, {
          church_name: churchName,
          theme: theme,
          preview_image_url: content.coloringSceneImageUrl || content.coloringTextImageUrl || null
        })
        
        console.log('📤 Upload result:', uploadResult)
        
        if (uploadResult && uploadResult.pamphlet_id) {
          console.log('✅ PDF saved successfully:', uploadResult.pamphlet_id)
          setPdfGenerated(true)
          // Notify parent component that PDF was generated
          if (onPdfGenerated) {
            onPdfGenerated(true)
          }
          // Notify parent component to reload pamphlet list
          if (onPdfUploaded) {
            console.log('🔄 Calling onPdfUploaded callback')
            onPdfUploaded()
          }
        } else {
          console.warn('⚠️ Upload succeeded but no pamphlet_id returned:', uploadResult)
          setPdfGenerated(true)
          // Notify parent component that PDF was generated
          if (onPdfGenerated) {
            onPdfGenerated(true)
          }
          // Still reload the list in case there are other pamphlets
          if (onPdfUploaded) {
            onPdfUploaded()
          }
        }
      } catch (uploadError) {
        // Upload is optional, but log the error for debugging
        console.error('❌ PDF upload failed:', uploadError)
        console.error('❌ Upload error details:', {
          message: uploadError.message,
          stack: uploadError.stack
        })
        setPdfGenerated(true)
        // Notify parent component that PDF was generated (even if upload failed)
        if (onPdfGenerated) {
          onPdfGenerated(true)
        }
        // Still reload the list in case there are other pamphlets
        if (onPdfUploaded) {
          onPdfUploaded()
        }
      }
    } catch (error) {
      setError('Failed to generate PDF. Please try again.')
      setPdfGenerated(true)
    } finally {
      setIsExporting(false)
    }
  }

  // Auto-generate PDF when content is ready
  useEffect(() => {
    if (content && !pdfGenerated && !isExporting && pamphletRef.current) {
      // Small delay to ensure DOM is fully rendered
      const timer = setTimeout(() => {
        exportToPDF()
      }, 500)
      return () => clearTimeout(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [content, pdfGenerated, isExporting])

  return (
    <div className="preview-container">
      <div className="preview-controls">
        {!pdfGenerated && (
          <button 
            onClick={exportToPDF} 
            className="export-btn" 
            disabled={isExporting}
          >
            {isExporting ? '⏳ Generating PDF...' : '📥 Download PDF'}
          </button>
        )}
        {error && (
          <div className="pdf-error-message">
            {error}
          </div>
        )}
      </div>
      
      <div ref={pamphletRef} className="pamphlet">
        {/* Page 1 */}
        <div className="page page-1">
          <div className="page-header">
            <h2 className="church-name">{displayChurchName}</h2>
            <h3 className="theme-title">{content.theme.toUpperCase()}</h3>
          </div>
          
          <div className="page-content">
            <div className="maze-section-full">
              <h4>🧩 Maze Challenge</h4>
              <p className="maze-instruction">{content.mazeGoal}</p>
              <Maze />
            </div>
            
            <div className="page-1-bottom">
              <div className="crossword-section-full">
                <h4>📝 Crossword</h4>
                <Crossword theme={content.theme} words={content.wordList} />
              </div>
            </div>
          </div>
        </div>

        {/* Page 2 */}
        <div className="page page-2">
          <div className="page-header">
            <h2 className="church-name">{displayChurchName}</h2>
            <h3 className="theme-title">{content.theme.toUpperCase()}</h3>
          </div>
          
          <div className="page-content">
            <div className="word-search-section-full">
              <h4>🔍 Word Search</h4>
              <p className="word-search-instruction">
                Find these words: {content.wordList.join(', ')}
              </p>
              <WordSearch words={content.wordList} />
            </div>
            
            <div className="page-2-bottom">
              <div className="left-col">
                <div className="quiz-section">
                  <h4>❓ Quiz</h4>
                  <Quiz questions={content.quizQuestions.slice(0, 5)} />
                </div>
              </div>
              
              <div className="right-col">
                <div className="word-completion-wrapper">
                  <h4>✏️ Complete the Phrase!</h4>
                  <WordCompletion phrase={content.wordCompletionPhrase} />
                </div>
                <div className="tictactoe-section">
                  <h4>⭕ Tic Tac Toe</h4>
                  <TicTacToe />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Page 3 */}
        <div className="page page-3">
          <div className="page-header">
            <h2 className="church-name">{displayChurchName}</h2>
            <h3 className="theme-title">{content.theme.toUpperCase()}</h3>
          </div>
          
          <div className="page-content">
            <div className="coloring-activity-section">
              <h4>🎨 Color Me!</h4>
              {content.coloringImageError && (
                <div className="coloring-error-message">
                  ⚠️ {content.coloringImageError}
                </div>
              )}
              <ColoringActivity
                textImageUrl={content.coloringTextImageUrl}
                sceneImageUrl={content.coloringSceneImageUrl}
                text={content.coloringText}
                theme={content.theme}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PamphletPreview

