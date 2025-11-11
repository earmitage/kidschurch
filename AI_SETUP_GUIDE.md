# AI Setup Guide

This guide walks you through configuring AI providers for the Church Games application.

## Supported Providers

| Provider | Model | Cost | Speed | Setup Difficulty |
|----------|-------|------|-------|------------------|
| **OpenAI** | GPT-3.5-turbo | ~$0.01-0.02 per 10 questions | Fast (1-2s) | ⭐ Easy |
| **Anthropic** | Claude 3 Haiku | ~$0.008 per 10 questions | Good (2-3s) | ⭐⭐ Medium |
| **Google Gemini** | Gemini 1.5 Flash | **FREE** up to 15/min | Good (1-2s) | ⭐⭐ Medium |
| **Mock** | Development | $0 | Instant | ⭐⭐⭐ N/A |

---

## Quick Setup Guides

### Option 1: OpenAI GPT-3.5 Turbo (Recommended for Production)

**Best for**: Production environments with budget  
**Cost**: ~$0.01-0.02 per 10 quiz questions  
**Speed**: 1-2 seconds

#### Steps:

1. **Get OpenAI API Key**
   - Visit https://platform.openai.com/api-keys
   - Sign up or log in
   - Create a new secret key

2. **Create `.env` file**
   ```bash
   cd backend
   cp .env.example .env
   ```

3. **Configure `.env`**
   ```bash
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-your-actual-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   PORT=5001
   FLASK_ENV=development
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start backend**
   ```bash
   python3 app.py
   ```

---

### Option 2: Anthropic Claude 3 Haiku (Cheapest Premium)

**Best for**: Cost-conscious production with excellent quality  
**Cost**: ~$0.008 per 10 quiz questions  
**Speed**: 2-3 seconds

#### Steps:

1. **Get Anthropic API Key**
   - Visit https://console.anthropic.com/
   - Sign up or log in
   - Go to API Keys section
   - Create a new key

2. **Configure `.env`**
   ```bash
   AI_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ANTHROPIC_MODEL=claude-3-haiku-20240307
   PORT=5001
   FLASK_ENV=development
   ```

3. **Install dependencies**
   ```bash
   pip install anthropic
   ```

4. **Start backend**
   ```bash
   python3 app.py
   ```

---

### Option 3: Google Gemini Flash (Free Tier Available)

**Best for**: Development and testing, or low-volume production  
**Cost**: FREE for 15 requests/minute  
**Speed**: 1-2 seconds

#### Steps:

1. **Get Google API Key**
   - Visit https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Create a new API key

2. **Configure `.env`**
   ```bash
   AI_PROVIDER=gemini
   GOOGLE_API_KEY=your-google-api-key-here
   GEMINI_MODEL=gemini-1.5-flash
   PORT=5001
   FLASK_ENV=development
   ```

3. **Install dependencies**
   ```bash
   pip install google-generativeai
   ```

4. **Start backend**
   ```bash
   python3 app.py
   ```

---

### Option 4: Mock (Development Only)

**Best for**: Local development without API costs  
**Cost**: $0  
**Speed**: Instant

#### Steps:

1. **Configure `.env`**
   ```bash
   AI_PROVIDER=mock
   PORT=5001
   FLASK_ENV=development
   ```

2. **Start backend**
   ```bash
   python3 app.py
   ```

---

## Testing Your Configuration

### 1. Health Check
```bash
curl http://localhost:5001/health
```
**Expected**: `{"status": "healthy"}`

### 2. Test Quiz Generation
```bash
curl -X POST http://localhost:5001/api/generate-quiz \
  -H "Content-Type: application/json" \
  -d '{"theme":"Noah","num_questions":5}'
```

**Expected Response**:
```json
{
  "success": true,
  "questions": [
    {"q": "Who built the big boat?", "a": "NOAH"},
    {"q": "What came after the rain?", "a": "RAINBOW"},
    ...
  ]
}
```

---

## Model Configuration

Each provider supports custom models via environment variables:

### OpenAI Models
- `gpt-3.5-turbo` (default) - Best balance of cost and speed
- `gpt-4` - Higher quality but more expensive
- `gpt-4-turbo` - Latest GPT-4 with better performance

**Usage**:
```bash
OPENAI_MODEL=gpt-3.5-turbo
```

### Anthropic Models
- `claude-3-haiku-20240307` (default) - Fast and cheap
- `claude-3-sonnet-20240229` - Higher quality
- `claude-3-opus-20240229` - Best quality, most expensive

**Usage**:
```bash
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

### Gemini Models
- `gemini-2.0-flash-exp` (default) - Latest experimental model
- `gemini-pro` - Stable production model
- `gemini-2.5-pro` - Premium model (if available)
- `gemini-2.5-flash` - Latest flash model (if available)

**Note**: Gemini model names change frequently. If you get a 404 error:
1. Check https://ai.google.dev/gemini-api/docs/models for current models
2. Try `gemini-pro` as a fallback
3. The code will automatically try fallback if configured

**Usage**:
```bash
GEMINI_MODEL=gemini-2.0-flash-exp
```

---

## Cost Estimates

### Per 10 Quiz Questions

| Provider | Cost | Monthly (100 pamphlets) |
|----------|------|-------------------------|
| OpenAI GPT-3.5 | $0.01-0.02 | ~$1-2 |
| Anthropic Haiku | $0.008 | ~$0.80 |
| Gemini Flash | $0 (FREE tier) | $0 |
| Mock | $0 | $0 |

### Monthly Cost (100 pamphlets, 10 questions each)

- **Most Expensive**: OpenAI @ ~$2/month
- **Cheapest Premium**: Anthropic @ ~$0.80/month
- **Free Option**: Gemini @ $0/month
- **Dev Only**: Mock @ $0/month

---

## Troubleshooting

### "Module not found" errors

**Solution**: Install the provider's package
```bash
# For OpenAI
pip install openai

# For Anthropic
pip install anthropic

# For Gemini
pip install google-generativeai

# Or install all at once
pip install -r requirements.txt
```

### "Service is not properly configured"

**Possible causes**:
1. Missing API key in `.env`
2. Invalid API key format
3. No credits/quota remaining

**Solution**:
1. Verify `.env` file has correct key
2. Check key starts with correct prefix:
   - OpenAI: `sk-`
   - Anthropic: `sk-ant-`
   - Gemini: Any string
3. Verify account has credits/quota

### "Invalid AI provider"

**Solution**: Check `AI_PROVIDER` in `.env` is one of:
- `openai`
- `anthropic`
- `gemini`
- `mock`

### Backend won't start on port 5001

**Solution**: Use different port
```bash
PORT=5002 python3 app.py
```
Then update frontend `.env`:
```
VITE_BACKEND_URL=http://localhost:5002
```

---

## Production Deployment

### Environment Variables in Production

**DO NOT** commit `.env` files to Git. Instead, set environment variables in your hosting platform:

#### Heroku
```bash
heroku config:set AI_PROVIDER=openai
heroku config:set OPENAI_API_KEY=sk-your-key
```

#### AWS Elastic Beanstalk
```bash
eb setenv AI_PROVIDER=openai OPENAI_API_KEY=sk-your-key
```

#### Docker
```dockerfile
ENV AI_PROVIDER=openai
ENV OPENAI_API_KEY=sk-your-key
```

#### Vercel/Netlify
Set in platform's Environment Variables UI

### Security Best Practices

1. ✅ Never commit `.env` files
2. ✅ Rotate API keys periodically
3. ✅ Set billing alerts in provider dashboard
4. ✅ Use read-only keys when possible
5. ✅ Monitor usage regularly

---

## Next Steps

Once configured, your application will:
- ✅ Generate unique, age-appropriate quiz questions
- ✅ Adapt to any biblical theme automatically
- ✅ Provide engaging content for 5-year-olds
- ✅ Scale with your needs

For questions or issues, refer to the main README or project documentation.

---

## Provider Comparison Summary

| Feature | OpenAI | Anthropic | Gemini | Mock |
|---------|--------|-----------|--------|------|
| Ease of Setup | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Cost | $$ | $ | FREE | $0 |
| Speed | Fast | Good | Fast | Instant |
| Quality | Excellent | Excellent | Good | Poor |
| Reliability | High | High | High | N/A |
| Best For | Production | Cost-conscious | Testing/Low-volume | Development |
