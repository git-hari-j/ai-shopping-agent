# 🛒 AI Shopping Agent

An intelligent shopping assistant that helps users find the best products across multiple e-commerce platforms using AI, web scraping, and voice recognition.

## ✨ Features

### 🔐 Authentication & User Management
- 🔒 **Secure Authentication**: JWT-based user registration and login system
- 👤 **User Profiles**: Personal user accounts with secure session management
- 🛡️ **Protected Routes**: Secure API endpoints with authentication middleware

### 🛍️ Advanced Shopping Features
- 🤖 **AI-Powered Recommendations**: Uses LLM (OpenAI, Groq, Ollama, etc.) for intelligent product suggestions
- 🛍️ **Multi-Platform Scraping**: Enhanced scraping across Amazon, eBay, and Walmart
- 💝 **Favorites Management**: Save and organize your favorite products
- 🚨 **Price Alerts**: Set target prices and get email notifications when prices drop
- 🔍 **Smart Search**: Real-time product search with enhanced results
- 📊 **Price Comparison**: Dynamic price comparison across multiple platforms

### 🎨 Modern User Experience
- 🎨 **Beautiful UI**: Modern React 18 frontend with glass morphism design
- 📱 **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- ⚡ **Real-time Updates**: Live product data and instant search results
- 🎭 **Interactive Components**: Smooth animations and user-friendly interface

### 🔧 Technical Features
- ⚡ **FastAPI Backend**: High-performance, async-ready Python backend
- 🏗️ **Modular Architecture**: Clean separation of concerns with Pydantic models
- 🗣️ **Voice Commands**: Voice-enabled product search using speech recognition
- 💱 **Currency Conversion**: Real-time currency conversion for international shopping
- 🔍 **NLP Processing**: Natural language processing for better search queries
- 📧 **Email Notifications**: Automated email alerts for price drops
- 💾 **Data Persistence**: Async SQLAlchemy with support for SQLite and PostgreSQL

## 🏗️ Project Structure

```
ai-shopping-agent/
├── ai-agent-frontend/          # React 18 frontend application
│   ├── src/
│   │   ├── App.js             # Main application component
│   │   ├── Login.js           # Authentication component
│   │   ├── App.css            # Modern styling with glass morphism
│   │   └── images/            # Application assets
│   ├── public/
│   ├── package.json
│   └── README.md
├── ai-agent-backend/           # FastAPI backend API
│   ├── app.py                 # Main application server
│   ├── models.py              # Database models
│   ├── auth.py                # JWT authentication manager
│   ├── config.py              # Application configuration
│   ├── database.py            # Database connection logic
│   ├── core/                  # Core modules
│   │   └── llm.py             # LLM Factory and providers
│   ├── enhanced_scraper.py    # Multi-platform web scraper
│   ├── price_alerts.py        # Price monitoring system
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment variables template
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.12 or higher)
- **uv** (recommended for Python dependency management)
- **Git**

### 🔧 Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd ai-agent-backend
   ```

2. Install Python dependencies:
   ```bash
   # Using uv (recommended)
   uv pip install -r requirements.txt

   # Or using standard pip
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env file and add your configuration:
   # - LLM Provider (groq, openai, ollama, etc.)
   # - API keys
   # - Database URL (sqlite:///./shopping_agent.db or postgresql://...)
   ```

4. Start the FastAPI server:
   ```bash
   # Using uvicorn directly
   uvicorn app:app --host 127.0.0.1 --port 5000 --reload
   ```
   The backend will run on `http://127.0.0.1:5000`.

### 🌐 Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ai-agent-frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```
   The frontend will run on `http://localhost:3000`

## 🎯 How to Use

### 1. Getting Started
1. **Register/Login**: Create an account or sign in to access features
2. **Search Products**: Use the search bar to find products across multiple platforms
3. **Browse Results**: View products from Amazon, eBay, and Walmart with prices and images

### 2. Managing Favorites
1. **Add to Favorites**: Click the heart icon on any product to save it
2. **View Favorites**: Navigate to the "My Favorites" section
3. **Remove Favorites**: Click the remove button to delete saved products

### 3. Setting Price Alerts
1. **Create Alert**: Click "Set Price Alert" on any product
2. **Set Target Price**: Enter your desired price point
3. **Get Notifications**: Receive email alerts when prices drop below your target

### 4. Advanced Features
1. **AI Recommendations**: Get intelligent product suggestions based on budget and preferences
2. **Real-time Updates**: See live price data and instant search results

## 📡 API Endpoints & Testing

See [CURL_COMMANDS.md](ai-agent-backend/CURL_COMMANDS.md) for a comprehensive list of curl commands to test the API.

### Key Endpoints:

- `GET /api/health` - Health check
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/recommend` - Get AI product recommendations

## 🛠️ Technologies Used

### Backend
- **FastAPI** - High-performance web framework
- **Async SQLAlchemy** - Database ORM with async support
- **SQLite / PostgreSQL** - Database options
- **JWT** - Secure JSON Web Tokens
- **Pydantic** - Data validation and settings management
- **LangChain** - LLM integration

### Frontend
- **React 18** - Modern UI framework
- **Axios** - HTTP client
- **CSS3** - Glass morphism styling

### Web Scraping & AI
- **Selenium** - Advanced web automation
- **Chrome WebDriver** - Headless browser automation
- **LLM Factory** - Multi-provider AI support (OpenAI, Groq, etc.)
- **BeautifulSoup** - HTML parsing

## 🔒 Security Notes

- Never commit API keys to version control
- Consider using environment variables for sensitive data

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
