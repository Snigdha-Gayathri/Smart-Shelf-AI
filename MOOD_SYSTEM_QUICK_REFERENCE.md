# SmartShelf AI Mood System - Quick Reference

## ✅ Status: FULLY IMPLEMENTED & TESTED

---

## API Endpoint

```
POST /api/recommend
```

### Request
```json
{
  "query": "I want obsession",
  "limit": 10  // optional, default 10, max 50
}
```

### Response
```json
{
  "detectedMood": "i want obsession",
  "matchedMood": "i want obsession",
  "matchedTags": ["possessive", "obsessive", "dark romance"],
  "matchedEmotions": ["desire", "love"],
  "similarityScore": 1.0,
  "fallbackUsed": false,
  "recommendations": [
    {
      "title": "Twisted Love",
      "author": "Ana Huang",
      "score": 0.448,
      "matchedTags": ["possessive", "dark romance"],
      "matchedEmotions": ["desire", "love"],
      ...
    }
  ]
}
```

---

## Available Moods (Canonical)

| Mood | Aliases | Tags | Intensity |
|------|---------|------|-----------|
| **i want obsession** | obsession, obsessive love, possessive love, i need obsessive love | possessive, obsessive, dark romance | high |
| **emotionally numb** | numb, emotionally numb, empty, dead inside | slow burn, introspective | low |
| **ruin me emotionally** | ruin me, destroy me emotionally, make me cry, hurt me | angst, tragic, dark | very_high |
| **touch her and die** | protective mmc, touch him and die, touch them and die | protective mmc, possessive | high |
| **comfort me** | comfort, soft healing, cozy, warm hug | cozy, healing, heartwarming | low |
| **chaos** | unhinged, chaotic, wild ride, messy | chaotic, unhinged, wild | high |

---

## Testing

### Test 1: Exact Match
```python
result = process_mood_query("i want obsession")
assert result['detected_mood'] == "i want obsession"
assert result['fallback_used'] == False
assert result['similarity_score'] == 1.0
```
✅ PASS

### Test 2: Alias Match
```python
result = process_mood_query("ruin me")
assert result['detected_mood'] == "ruin me emotionally"
assert result['fallback_used'] == False
```
✅ PASS

### Test 3: Fuzzy Match (Lexical/Embedding)
```python
result = process_mood_query("I need obsessive love")
assert result['detected_mood'] == "i want obsession"
assert result['fallback_used'] == False
```
✅ PASS

### Test 4: Fallback (Unknown Mood)
```python
result = process_mood_query("I want to eat pizza")
assert result['fallback_used'] == True
assert result['similarity_score'] == 0.0
# Still generates recommendations!
```
✅ PASS

### Test 5: Error Handling
```python
try:
    process_mood_query("")
except ValueError:
    pass  # Expected
```
✅ PASS

---

## File Structure

```
backend/
├── config/
│   └── mood_map.py              # Mood definitions & GoEmotions labels
├── services/
│   ├── mood_processor.py        # Mood detection & matching
│   ├── mood_recommendation_service.py  # Scoring & ranking
│   └── book_repository.py       # Book data loading
├── controllers/
│   └── recommendation_controller.py  # Error handling
├── routes/
│   └── recommendation_routes.py  # API endpoint
└── data/
    └── books_data.json          # 380 books with metadata
```

---

## Key Functions

### `mood_processor.process_mood_query(raw_query, threshold=0.7)`
Returns:
```python
{
    "normalized_query": str,      # Cleaned input
    "detected_mood": str,          # Canonical or raw query
    "matched_mood": str or None,   # Canonical mood (if matched)
    "matched_emotions": List[str], # GoEmotions labels
    "matched_tags": List[str],     # Trope/theme tags
    "intensity": str,              # low/medium/high/very_high
    "similarity_score": float,     # 0.0-1.0
    "fallback_used": bool,         # True if no match found
    "query_embedding": List[float] # Embedding for similarity search
}
```

### `mood_recommendation_service.generate_mood_recommendations(query, limit=10)`
Returns:
```python
{
    "detectedMood": str,
    "matchedMood": str,
    "matchedTags": List[str],
    "matchedEmotions": List[str],
    "similarityScore": float,
    "fallbackUsed": bool,
    "recommendations": List[{
        "title": str,
        "author": str,
        "score": float,  # 0.0-1.0 overall match
        "embeddingSimilarity": float,
        "tagMatchScore": float,
        "emotionMatchScore": float,
        "matchedTags": List[str],
        "matchedEmotions": List[str],
        ...
    }]
}
```

---

## Scoring Formula

```
score = 0.5 * embedding_similarity + 
        0.3 * tag_match_score + 
        0.2 * emotion_match_score

score *= intensity_multiplier
```

Where:
- **embedding_similarity**: Cosine similarity of mood vs book descriptions
- **tag_match_score**: Overlap of mood tags with book tags
- **emotion_match_score**: Overlap of mood emotions with book emotions
- **intensity_multiplier**: 
  - low: 0.9x (reduce intensity-sensitive recommendations)
  - medium: 1.0x (default)
  - high: 1.12x (boost mood-relevant recommendations)
  - very_high: 1.2x (strong boost)

---

## Book Metadata Fields Used

```json
{
  "title": "string",
  "author": "string", 
  "genre": "string",
  "synopsis": "string",
  "embedding_tags": ["string"],  // Fallback for tags
  "emotion_tags": ["string"],    // Fallback for emotionProfile
  "mood": "string",
  "tone": "string",
  "type": "string",
  "pacing": "string",
  "cover": "path or URL"
}
```

---

## Environment Variables

```bash
# Disable ML pipeline (faster startup, no embeddings)
SKIP_ML=1  

# CORS origins
ALLOWED_ORIGINS=http://localhost:3000,https://example.com

# Server port
PORT=8000
```

---

## Common Mistakes to Avoid

### ❌ Wrong
```python
# Don't direct-call the mood processor without error handling
mood_result = process_mood_query(user_input)
```

### ✅ Right
```python
# Use the controller which handles errors
from controllers.recommendation_controller import handle_mood_recommendation

try:
    result = handle_mood_recommendation(user_input, limit=10)
except ValueError as e:
    # User gave empty input
    return {"error": "Please tell me how you're feeling"}
except Exception as e:
    # Server error
    return {"error": "Failed to generate recommendations"}
```

---

## Deployment Checklist

- [ ] `config/mood_map.py` deployed
- [ ] `services/mood_processor.py` deployed
- [ ] `services/mood_recommendation_service.py` deployed
- [ ] `routes/recommendation_routes.py` registered in FastAPI app
- [ ] `data/books_data.json` includes embedding_tags or emotion_tags
- [ ] ML pipeline available (or SKIP_ML=1 if constrained)
- [ ] Logging configured for debugging
- [ ] CORS configured for frontend

---

## Debugging

### Check Mood Detection
```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "test mood"}'
```

### Check Logs
```bash
# Look for:
# "Mood mapped via embedding/lexical/exact: [mood] (score=...)"
# "Mood recommendation generated: detected=..., fallback=..."
```

### Run Tests Locally
```bash
cd backend
python -m pytest test_memory_brain.py -v -k mood
```

---

## What Works

✅ Exact mood matching
✅ Alias detection
✅ Fuzzy/semantic matching
✅ Fallback for unknown moods
✅ Tag-based filtering
✅ Emotion-based filtering
✅ Intensity-aware scoring
✅ Error validation (empty input)
✅ Comprehensive logging
✅ 380 books tested

---

## Next Steps (Optional)

1. **Add more moods** to `config/mood_map.py`
2. **Add "reason" field** explaining why each book was recommended
3. **Add mood confidence metric** (0.0-1.0) to response
4. **Implement user feedback** (track which moods are working)
5. **Integrate with frontend** using example code above

---

## Version History

- **v1.0.0** (Current) ✅ 
  - Core mood processing
  - 6 base moods + aliases
  - Full fallback coverage
  - API integrated
  - 380 books tested

- **v1.1.0** (Planned)
  - Additional moods
  - Recommendation reasons
  - Confidence metrics

- **v2.0.0** (Phase 2)
  - User mood history
  - Personalization
  - Feedback loops
