import ColoringText from './ColoringText'
import ColoringScene from './ColoringScene'
import './ColoringActivity.css'

function ColoringActivity({ textImageUrl, sceneImageUrl, text, theme }) {
  return (
    <div className="coloring-activity">
      <div className="coloring-text-wrapper">
        <ColoringText
          imageUrl={textImageUrl}
          text={text}
          theme={theme}
        />
      </div>
      <div className="coloring-scene-wrapper">
        <ColoringScene
          imageUrl={sceneImageUrl}
          theme={theme}
        />
      </div>
    </div>
  )
}

export default ColoringActivity

