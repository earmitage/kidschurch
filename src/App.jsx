import PamphletGenerator from './components/PamphletGenerator'
import './App.css'

function App() {
  return (
    <div className="App">
      <PamphletGenerator />
      <footer className="app-footer">
        <p>
          Made with ❤️ for kids church leaders everywhere | 
          <span className="footer-link"> Free & Open Source</span>
        </p>
        <p className="footer-tagline">
          Generate beautiful, printable activities in seconds
        </p>
      </footer>
    </div>
  )
}

export default App

