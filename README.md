# Kids Church Pamphlet Generator

> Generate beautiful, printable activity pamphlets for kids church in seconds using AI

A full-stack web application that helps kids church leaders create engaging, age-appropriate activity pamphlets with mazes, word searches, coloring pages, quizzes, and more - all powered by AI.

![Made with ❤️ for kids church leaders everywhere | Free & Open Source](https://img.shields.io/badge/Made%20with-❤️-red) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🎨 Activity Types
- **Mazes** - Navigate through biblical-themed mazes
- **Word Searches** - Find hidden words related to the theme
- **Coloring Pages** - AI-generated coloring images and text
- **Quizzes** - Age-appropriate quiz questions (designed for 5-year-olds)
- **Crossword Puzzles** - Interactive crossword games
- **Tic Tac Toe** - Simple game with biblical themes
- **Word Completion** - Fill-in-the-blank activities

### 🤖 AI-Powered Content Generation
- **Multiple AI Providers** - Choose from OpenAI, Anthropic Claude, or Google Gemini
- **Theme-Based Generation** - Automatically adapts content to any biblical theme
- **Age-Appropriate** - Content specifically designed for young children
- **Cost-Effective** - Support for free tier (Gemini) and low-cost options

### 📄 PDF Generation & Management
- **Instant PDF Export** - Download printable pamphlets immediately
- **Storage & History** - Save and manage previously generated pamphlets
- **Preview Images** - Visual previews of generated content
- **Search & Filter** - Find pamphlets by church name or theme

### 🔒 Production-Ready Features
- **Rate Limiting** - Protect against abuse
- **Input Validation** - Comprehensive security measures
- **CORS Support** - Secure cross-origin requests
- **Error Handling** - Graceful error messages
- **Database Integration** - MySQL support for persistent storage

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **MySQL** 8.0+ (optional, for persistent storage)
- **AI API Key** (OpenAI, Anthropic, or Google Gemini)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/earmitage/kidschurch.git
   cd church-games
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp env.example .env
   # Edit .env with your configuration (see Configuration section)
   ```

3. **Set up the frontend**
   ```bash
   cd ..
   npm install
   cp .env.example .env  # If you have a frontend .env.example
   # Edit .env with your backend URL
   ```

4. **Initialize the database** (optional)
   ```bash
   cd backend
   python3 init_database.py
   ```

5. **Start the backend**
   ```bash
   cd backend
   ./start.sh
   # Or: python3 app.py (development mode)
   ```

6. **Start the frontend** (in a new terminal)
   ```bash
   npm run dev
   ```

7. **Open your browser**
   ```
   http://localhost:5173
   ```

## ⚙️ Configuration

### Backend Configuration

Create a `.env` file in the `backend/` directory:

```env
# Server Configuration
PORT=5001
HOST=0.0.0.0
FLASK_ENV=development
WORKERS=2

# AI Provider (choose one)
AI_PROVIDER=gemini  # Options: openai, anthropic, gemini, mock

# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Google Gemini Configuration (FREE tier available)
GOOGLE_API_KEY=your-google-api-key
GEMINI_MODEL=gemini-2.0-flash-exp

# Database Configuration (optional)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=kidschurch

# PDF Storage
PDF_STORAGE_DIR=pdfs

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

### Frontend Configuration

Create a `.env` file in the root directory:

```env
VITE_BACKEND_URL=http://localhost:5001
```

### AI Provider Setup

See [AI_SETUP_GUIDE.md](./AI_SETUP_GUIDE.md) for detailed instructions on setting up each AI provider.

**Quick Recommendations:**
- **Free Option**: Google Gemini (15 requests/minute free tier)
- **Production**: OpenAI GPT-3.5-turbo (~$0.01-0.02 per pamphlet)
- **Cost-Conscious**: Anthropic Claude 3 Haiku (~$0.008 per pamphlet)

## 📁 Project Structure

```
church-games/
├── backend/                 # FastAPI backend
│   ├── app.py              # Main FastAPI application
│   ├── services/           # Business logic services
│   │   ├── ai_service.py   # AI provider abstraction
│   │   ├── database_service.py
│   │   └── pdf_storage_service.py
│   ├── utils/              # Utilities (security, validation, etc.)
│   ├── requirements.txt    # Python dependencies
│   ├── start.sh           # Production startup script
│   └── gunicorn.conf.py   # Gunicorn configuration
├── src/                    # React frontend
│   ├── components/         # React components
│   │   ├── PamphletGenerator.jsx
│   │   ├── PamphletPreview.jsx
│   │   ├── Quiz.jsx
│   │   ├── Maze.jsx
│   │   └── ... (other activity components)
│   └── utils/             # Frontend utilities
│       └── api.js         # API client
├── package.json           # Frontend dependencies
└── README.md             # This file
```

## 🛠️ Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python3 app.py  # Development server
```

### Frontend Development

```bash
npm run dev  # Starts Vite dev server with hot reload
```

### Building for Production

**Frontend:**
```bash
npm run build
# Output: dist/
```

**Backend:**
```bash
cd backend
./start.sh  # Uses Gunicorn with Uvicorn workers
```

## 🚢 Production Deployment

### Backend Deployment

1. **Set environment variables** (see Configuration section)
2. **Use Gunicorn** (included in `start.sh`):
   ```bash
   cd backend
   ./start.sh
   ```

3. **Or use a process manager** (systemd, supervisor, etc.)

4. **Configure reverse proxy** (Nginx recommended):
   - See `backend/nginx.example.conf` for Nginx configuration
   - **Important**: Set `client_max_body_size 15M` for PDF uploads

### Frontend Deployment

1. **Build the frontend:**
   ```bash
   npm run build
   ```

2. **Deploy `dist/` folder** to your web server (Nginx, Apache, CDN, etc.)

3. **Configure environment variables** for production backend URL

### Troubleshooting

#### 413 Content Too Large Error

If you get `413 (Content Too Large)` errors when uploading PDFs:

1. **Nginx Configuration**: Add to your Nginx config:
   ```nginx
   client_max_body_size 15M;
   ```

2. See `backend/STARTUP_GUIDE.md` for detailed troubleshooting steps.

## 📚 Documentation

- **[AI Setup Guide](./AI_SETUP_GUIDE.md)** - Detailed AI provider configuration
- **[Backend Startup Guide](./backend/STARTUP_GUIDE.md)** - Backend setup and deployment
- **[Nginx Configuration Example](./backend/nginx.example.conf)** - Production reverse proxy setup

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- Made with ❤️ for kids church leaders everywhere
- Built with [React](https://react.dev/), [FastAPI](https://fastapi.tiangolo.com/), and AI
- Inspired by the need for quick, engaging content for children's ministry

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Made with ❤️ for kids church leaders everywhere | Free & Open Source**

