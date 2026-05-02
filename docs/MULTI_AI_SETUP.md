# 🚀 Multi-Provider AI Setup Guide

Your resume generator now supports **ANY AI provider**! 🎉

## ✅ What's New

- ✨ **Multi-Provider Support**: OpenAI, Anthropic Claude, Google Gemini, Ollama
- 🔧 **Easy Switching**: Just change environment variables
- 🛡️ **Fallback System**: Mock responses when AI is unavailable
- 📊 **Token Tracking**: Works with all providers

## 🔧 Quick Setup

### 1. Copy Environment File
```bash
cp .env.multi-ai-example .env
```

### 2. Choose Your AI Provider

#### Option A: OpenAI (GPT-4, ChatGPT)
```env
AI_PROVIDER=openai
AI_API_KEY=sk-your-openai-key-here
```

#### Option B: Anthropic Claude
```env
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-your-anthropic-key-here
```

#### Option C: Google Gemini
```env
AI_PROVIDER=google
AI_API_KEY=your-google-gemini-key-here
```

#### Option D: Ollama (Local AI - Free!)
```env
AI_PROVIDER=ollama
AI_BASE_URL=http://localhost:11434
# No API key needed for Ollama
```

### 3. Start Your Services
```bash
docker-compose up -d
```

## 🧪 Test Your Setup

### Quick API Test
```bash
python test_multi_ai.py
```

### Check Backend API
```bash
python test_api_backend.py
```

## 🎯 Provider Comparison

| Provider | Pros | Cons | Best For |
|----------|------|------|----------|
| **OpenAI** | Most reliable, best quality | Costs money, rate limits | Production use |
| **Anthropic** | Very good quality, longer context | Costs money | Complex resumes |
| **Google** | Fast, good quality | Newer, less tested | Quick generation |
| **Ollama** | 100% Free, runs locally | Requires local setup | Development/testing |

## 🔄 Switching Providers

Just update your `.env` file:

```bash
# Switch to Claude
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-your-claude-key

# Restart backend
docker-compose restart backend
```

## 🛠️ Advanced Configuration

### Custom Models
```env
# OpenAI
AI_MODEL_RESUME=gpt-4o-mini
AI_MODEL_INTERVIEW=gpt-3.5-turbo

# Anthropic
AI_MODEL_RESUME=claude-3-5-sonnet-20241022
AI_MODEL_INTERVIEW=claude-3-haiku-20240307

# Google
AI_MODEL_RESUME=gemini-1.5-pro
AI_MODEL_INTERVIEW=gemini-1.5-flash
```

### Ollama Setup (Free Local AI)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download a model
ollama pull llama3.1
ollama pull mistral

# Set environment
AI_PROVIDER=ollama
AI_MODEL_RESUME=llama3.1
```

## 🚨 Troubleshooting

### Issue: "API key not found"
- ✅ Check your `.env` file has `AI_API_KEY=your-key`
- ✅ Restart backend: `docker-compose restart backend`

### Issue: "Quota exceeded" 
- ✅ Switch to different provider or add billing
- ✅ Use Ollama for free local AI

### Issue: "Provider not supported"
- ✅ Check `AI_PROVIDER` is one of: `openai`, `anthropic`, `google`, `ollama`

## 🎉 Success!

Your app now works with **any AI provider**! Switch between them anytime by updating your `.env` file.

### Next Steps:
1. Test with your preferred AI provider
2. Set up billing if using paid providers
3. Try Ollama for free local AI
4. Customize models for your needs

## 📞 Need Help?

If you see errors:
1. Check your `.env` file
2. Verify API keys are valid
3. Ensure provider is supported
4. Try switching to a different provider

**Your resume generator is now future-proof and can use any AI model! 🚀**