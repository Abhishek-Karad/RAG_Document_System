# LLM Integration Guide

## Overview

This system now includes a **Generative AI (LLM) layer** powered by **Google Gemini** to generate formulated, comprehensive answers based on FAISS-retrieved document chunks.

## Architecture

```
1. User Question
    ↓
2. FAISS Search (retrieve relevant chunks)
    ↓
3. Gemini LLM (formulate answer from chunks)
    ↓
4. Formatted Response (answer + supporting chunks)
```

## Setup

### 1. Get a Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your API key

### 2. Configure Environment

**Option A: Using .env file**
```bash
cp .env.example .env
# Edit .env and add your API key
GEMINI_API_KEY=your_key_here
```

**Option B: Set environment variable**
```bash
export GEMINI_API_KEY=your_key_here
python main.py
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### API Endpoints

#### Original: Chunk Retrieval Only
```bash
POST /ask
{
  "question": "What is X?",
  "top_k": 3,
  "similarity_threshold": 0.50
}

Response:
{
  "question": "What is X?",
  "results": [
    {
      "chunk_id": "...",
      "text": "...",
      "similarity_score": 0.87,
      ...
    }
  ],
  "total_results": 3
}
```

#### New: LLM-Formatted Answer
```bash
POST /ask-llm
{
  "question": "What is X?",
  "top_k": 3,
  "similarity_threshold": 0.50,
  "model": "gemini-pro"
}

Response:
{
  "question": "What is X?",
  "answer": "Based on the documents, X is... [comprehensive answer]",
  "supporting_chunks": [
    {
      "chunk_id": "...",
      "text": "...",
      "similarity_score": 0.87
    }
  ],
  "chunk_count": 3,
  "model": "gemini-pro"
}
```

## Available Gemini Models

- `gemini-pro` - Best for text generation (default)
- `gemini-pro-vision` - For text + image inputs (requires additional setup)

## How It Works

### Step 1: Retrieve Chunks
- Query is converted to 384-dimensional embedding
- FAISS searches for similar chunks
- Top-k relevant chunks are selected
- Chunks filtered by similarity threshold

### Step 2: Format Context
Each chunk is formatted with:
- Document source name
- Chunk index
- Relevance score
- Content text

### Step 3: LLM Generation
- Context + chunks sent to Gemini
- LLM generates comprehensive answer
- Answer references document sources
- Response includes quality and completeness

### Step 4: Return Result
- Answer text
- Supporting chunks with scores
- Model information

## Example Usage

### Python
```python
import requests

response = requests.post(
    "http://localhost:7999/ask-llm",
    json={
        "question": "What are the main benefits?",
        "top_k": 3,
        "similarity_threshold": 0.50,
        "model": "gemini-pro"
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Source chunks: {result['chunk_count']}")
```

### cURL
```bash
curl -X POST "http://localhost:7999/ask-llm" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main topics?",
    "top_k": 3,
    "similarity_threshold": 0.50,
    "model": "gemini-pro"
  }'
```

## Troubleshooting

### "Gemini API key not configured"
**Issue**: GEMINI_API_KEY environment variable not set

**Solution**:
```bash
export GEMINI_API_KEY=your_key
python main.py
```

### "Could not import module"
**Issue**: google-generativeai not installed

**Solution**:
```bash
pip install google-generativeai
```

### "API Error: 429"
**Issue**: Rate limit exceeded

**Solution**: Wait a moment and try again. Gemini API has rate limits on free tier.

### "No relevant information found"
**Issue**: LLM found chunks but answer is empty

**Solution**: Try lowering similarity_threshold or increasing top_k

## API Rate Limits

**Free Tier**:
- 60 requests per minute
- 1.5 x 10^6 tokens per day

**For production**, consider:
- Upgrading to paid plan
- Implementing caching layer
- Batching requests

## Cost

- **Free Tier**: Limited requests, fully functional
- **Paid**: $0.00125 per 1K input tokens, $0.000375 per 1K output tokens

See pricing: https://ai.google.dev/pricing

## Best Practices

1. **Set appropriate threshold**: 0.5-0.6 for balanced results
2. **Use reasonable top_k**: 3-5 chunks usually sufficient
3. **Keep questions clear**: Better questions = better answers
4. **Monitor latency**: First query slower (model loading)
5. **Handle errors gracefully**: LLM may occasionally fail

## Advanced Configuration

### Custom Instructions
Edit the prompt in `faiss_manager.py` `generate_answer()` method:

```python
prompt = f"""Your custom instructions:
- Be concise
- Quote sources
- Indicate uncertainty
...
"""
```

### Different Gemini Models
```python
# In your code
response = requests.post(
    "http://localhost:7999/ask-llm",
    json={
        "question": "What is X?",
        "model": "gemini-pro-vision"  # Different model
    }
)
```

## Limitations

- **Token Limit**: Max ~30k tokens per request
- **Hallucination**: LLM may generate plausible-sounding but false information
- **Latency**: First request slower (model warming up)
- **Cost**: Each request incurs API charges (if paid tier)

## Monitoring

Check system status:
```bash
curl http://localhost:7999/health

# Response includes:
# - Gemini configuration status
# - Number of documents
# - Total chunks indexed
```

## Production Checklist

- [ ] Set GEMINI_API_KEY in production environment
- [ ] Monitor API usage and costs
- [ ] Implement caching for common questions
- [ ] Set up error logging and alerts
- [ ] Load test with expected query volume
- [ ] Configure rate limiting if needed
- [ ] Test with real documents
- [ ] Document your custom prompt modifications

## Support

- **Gemini Issues**: https://ai.google.dev/support
- **FAISS Issues**: https://github.com/facebookresearch/faiss/issues
- **This Project**: Check main documentation

---

**Happy Questioning!** 🚀

With Gemini LLM integration, your document QA system can now provide intelligent, contextually-aware answers!
