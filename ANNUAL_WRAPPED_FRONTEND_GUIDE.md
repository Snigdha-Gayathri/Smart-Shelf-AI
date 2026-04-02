# Annual Wrapped - Frontend Integration Guide

## Overview

The Annual Wrapped feature provides three comprehensive analytical metrics about a user's reading patterns and preferences. All data is calculated and returned from a single API endpoint.

---

## API Endpoint

```
GET /users/{user_id}/annual-wrapped
```

### Query Parameters

None (all parameters are path parameters)

### Response Format

```json
{
  "status": "success" | "insufficient_data",
  "user_id": 100,
  "generated_at": "2026-04-02T15:30:45.123456",
  "predictionAlignment": {
    "score": 0.75,
    "label": "High Alignment",
    "context": [
      "How well recommendations matched your actual preferences",
      "Based on 3/4 recommended books liked"
    ]
  },
  "preferenceStability": {
    "score": 0.62,
    "label": "Moderately Evolving",
    "context": [
      "Consistency of your reading patterns over time",
      "Analyzed across 3 months of reading"
    ]
  },
  "explorationProfile": {
    "score": 0.48,
    "label": "Balanced Reader",
    "context": [
      "Your tendency to explore vs stick to familiar genres",
      "48.0% of your books were new genres to you"
    ]
  },
  "extras": {
    "topGenres": ["dark romance", "paranormal fantasy", "contemporary romance"],
    "favoritesTropes": ["possessive-mmc", "dark-romance", "enemies-to-lovers"],
    "readingStats": {
      "total_books": 24,
      "avg_rating": 4.2,
      "dnf_count": 2,
      "dnf_rate": 0.08,
      "avg_completion": 97.3
    }
  }
}
```

---

## Metric Definitions

### 1. Prediction vs Reality Alignment

**What it measures:** How well the recommendation system understood your preferences based on your actual ratings.

**Score:** 0.0 - 1.0
- **0.0** = Recommendations were completely misaligned
- **0.5** = About half the recommendations matched your taste
- **1.0** = All recommendations were perfectly matched

**Classification:**
- **Low Alignment** (< 0.4): Recommendations aren't matching your preferences
- **Moderate Alignment** (0.4 - 0.7): Recommendations are decent but could improve
- **High Alignment** (≥ 0.7): Recommendations are well-targeted

**Calculation:** 
```
alignment = (books_you_liked_that_were_recommended) / (total_books_recommended)
```

**Frontend Notes:**
- Only calculated if user has rated books
- If insufficient data, returns 0.0 with label "Insufficient Data"
- Helps users understand system accuracy

---

### 2. Preference Stability Index

**What it measures:** Whether your reading preferences are consistent over time or evolving.

**Score:** 0.0 - 1.0
- **0.0** = Your preferences are completely changing (highly dynamic)
- **0.5** = Your preferences are moderately evolving
- **1.0** = Your preferences are very consistent

**Classification:**
- **Highly Stable** (> 0.7): Very consistent reading patterns
- **Moderately Evolving** (0.4 - 0.7): Some pattern changes over time
- **Highly Dynamic** (≤ 0.4): Preferences change frequently

**Calculation:**
```
- Divide reading history into monthly periods
- Extract top 5 genres/tags for each month
- Calculate Jaccard similarity between consecutive months
- Average all similarities to get stability score
```

**Frontend Notes:**
- Analyzed monthly, can span multiple months
- Needs at least 8 weeks of reading data for meaningful results
- Shows book diversity trends

---

### 3. Exploration vs Exploitation Score

**What it measures:** Your tendency to read new genres vs. revisiting familiar ones.

**Score:** 0.0 - 1.0
- **0.0** = You only read familiar genres (100% exploitation)
- **0.5** = Equal mix of new and familiar genres
- **1.0** = You read only new genres (100% exploration)

**Classification:**
- **Explorer** (> 0.6): Adventurous reader who loves trying new genres
- **Balanced Reader** (0.3 - 0.6): Mix of familiar and new
- **Preference-Focused** (< 0.3): Tends to stick with favorite genres

**Calculation:**
```
- Go through books chronologically
- Mark each genre as "seen" or "new" on first encounter
- exploration_ratio = (new_genres) / (total_books)
```

**Frontend Notes:**
- Chronological ordering important for accuracy
- Based on genre diversity, not just variety
- Helps users understand their reading habits

---

## Frontend Component Examples

### React Hook for Data Fetching

```javascript
import { useState, useEffect } from 'react';

export function useAnnualWrapped(userId) {
  const [wrapped, setWrapped] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userId) return;

    fetch(`/users/${userId}/annual-wrapped`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        setWrapped(data);
        setError(null);
      })
      .catch(err => {
        setError(err.message);
        setWrapped(null);
      })
      .finally(() => setLoading(false));
  }, [userId]);

  return { wrapped, loading, error };
}
```

### Card Component for Metrics

```javascript
function MetricCard({ metric, label, subtitle, icon }) {
  const score = metric.score;
  const percentage = Math.round(score * 100);

  return (
    <div className="metric-card">
      <div className="metric-header">
        <span className="metric-icon">{icon}</span>
        <h3>{label}</h3>
      </div>

      <div className="metric-body">
        <div className="score-display">
          <svg className="score-circle" viewBox="0 0 100 100">
            <circle
              className="background"
              cx="50"
              cy="50"
              r="45"
            />
            <circle
              className="progress"
              cx="50"
              cy="50"
              r="45"
              style={{
                strokeDashoffset: `${282.7 * (1 - score)}`
              }}
            />
          </svg>
          <div className="score-text">
            <span className="percentage">{percentage}%</span>
            <span className="score-number">{score.toFixed(2)}</span>
          </div>
        </div>

        <div className="metric-info">
          <p className="classification">{metric.label}</p>
          <p className="description">{metric.context[0]}</p>
          <p className="details">{metric.context[1]}</p>
        </div>
      </div>
    </div>
  );
}
```

### Full Wrapped Dashboard

```javascript
function AnnualWrappedDashboard({ userId }) {
  const { wrapped, loading, error } = useAnnualWrapped(userId);

  if (loading) {
    return <div className="loading">Generating your wrapped report...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!wrapped) {
    return <div className="no-data">No wrapped data available</div>;
  }

  if (wrapped.status === 'insufficient_data') {
    return (
      <div className="container">
        <h1>Annual Wrapped Coming Soon</h1>
        <p>{wrapped.message}</p>
        <p>Keep reading to unlock your personalized wrapped report!</p>
      </div>
    );
  }

  const { predictionAlignment, preferenceStability, explorationProfile, extras } = wrapped;

  return (
    <div className="wrapped-container">
      <h1>Your 2026 Reading Journey</h1>
      <p className="subtitle">Insights powered by 24 books and counting</p>

      <div className="metrics-grid">
        <MetricCard
          metric={predictionAlignment}
          label="Prediction Alignment"
          icon="🎯"
        />
        <MetricCard
          metric={preferenceStability}
          label="Preference Stability"
          icon="📈"
        />
        <MetricCard
          metric={explorationProfile}
          label="Exploration Profile"
          icon="🗺️"
        />
      </div>

      <div className="extras-section">
        <div className="reading-stats">
          <h3>Reading Statistics</h3>
          <ul>
            <li>Total Books: {extras.readingStats.total_books}</li>
            <li>Average Rating: {extras.readingStats.avg_rating}/5</li>
            <li>Completion Rate: {extras.readingStats.avg_completion}%</li>
            <li>DNF Rate: {(extras.readingStats.dnf_rate * 100).toFixed(1)}%</li>
          </ul>
        </div>

        <div className="top-genres">
          <h3>Your Top Genres</h3>
          <div className="genre-cloud">
            {extras.topGenres.map(genre => (
              <span key={genre} className="genre-tag">
                {genre}
              </span>
            ))}
          </div>
        </div>

        <div className="favorite-tropes">
          <h3>Favorite Tropes</h3>
          <div className="trope-list">
            {extras.favoritesTropes.map(trope => (
              <span key={trope} className="trope-badge">
                {trope}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## Error Handling

### Insufficient Data Response

```json
{
  "status": "insufficient_data",
  "user_id": 100,
  "message": "Not enough reading data available for an annual wrapped report",
  "predictionAlignment": {
    "score": 0.0,
    "label": "Insufficient Data",
    "context": ["Start interacting with books to unlock this metric", ""]
  },
  "preferenceStability": {
    "score": 0.0,
    "label": "Insufficient Data",
    "context": ["Need at least 8 weeks of reading activity", ""]
  },
  "explorationProfile": {
    "score": 0.0,
    "label": "Insufficient Data",
    "context": ["Need more books to analyze exploration patterns", ""]
  },
  "extras": {
    "topGenres": [],
    "favoritesTropes": [],
    "readingStats": {
      "total_books": 0,
      "avg_rating": 0.0,
      "dnf_count": 0,
      "dnf_rate": 0.0,
      "avg_completion": 0.0
    }
  }
}
```

**Minimum Requirements:**
- At least 5 books read for basic metrics
- At least 8 weeks (2 months) for stability analysis
- Variety of genres for meaningful exploration score

---

## CSS Styling Tips

### Metric Card Styling

```css
.metric-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px;
  color: white;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}

.score-circle {
  width: 120px;
  height: 120px;
  transform: rotate(-90deg);
}

.score-circle .background {
  fill: none;
  stroke: rgba(255, 255, 255, 0.2);
  stroke-width: 4;
}

.score-circle .progress {
  fill: none;
  stroke: white;
  stroke-width: 4;
  stroke-linecap: round;
  stroke-dasharray: 282.7;
  transition: stroke-dashoffset 0.6s ease;
}

.classification {
  font-weight: 600;
  font-size: 18px;
  margin-top: 12px;
}

.description {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 4px;
}

.details {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 8px;
  font-style: italic;
}
```

---

## Testing

### Test Cases

```javascript
describe('Annual Wrapped', () => {
  it('should fetch wrapped data for user', async () => {
    const data = await fetch('/users/100/annual-wrapped');
    expect(data.status).toBe('success');
  });

  it('should handle insufficient data gracefully', async () => {
    const data = await fetch('/users/999/annual-wrapped');
    expect(data.status).toBe('insufficient_data');
    expect(data.predictionAlignment.score).toBe(0.0);
  });

  it('should calculate scores between 0 and 1', async () => {
    const data = await fetch('/users/100/annual-wrapped');
    [
      data.predictionAlignment.score,
      data.preferenceStability.score,
      data.explorationProfile.score
    ].forEach(score => {
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(1);
    });
  });

  it('should provide valid classifications', async () => {
    const data = await fetch('/users/100/annual-wrapped');
    const validLabels = [
      'High Alignment',
      'Moderate Alignment',
      'Low Alignment',
      'Highly Stable',
      'Moderately Evolving',
      'Highly Dynamic',
      'Explorer',
      'Balanced Reader',
      'Preference-Focused Reader',
      'Insufficient Data'
    ];
    expect(validLabels).toContain(data.predictionAlignment.label);
  });
});
```

---

## Accessibility Considerations

### Screen Reader Support

```html
<div class="metric-card" aria-label="Prediction Alignment metric">
  <h3>Prediction Alignment</h3>
  <div aria-live="polite" role="img" aria-label="Score: 0.75 or 75 percent">
    <!-- Score visualization -->
  </div>
  <p role="description">
    {metric.label}: {metric.context[0]}
  </p>
</div>
```

### Color Contrast

Ensure sufficient contrast ratios:
- Text on background cards: minimum WCAG AA (4.5:1)
- Progress circles: Use primary + secondary colors with distinct brightness
- Labels: High contrast for readability

### Keyboard Navigation

```javascript
<div className="metrics-grid" role="region" aria-label="Reading metrics">
  <MetricCard tabIndex={0} {...props} />
  <MetricCard tabIndex={0} {...props} />
  <MetricCard tabIndex={0} {...props} />
</div>
```

---

## Performance Optimization

### Caching Strategy

```javascript
// Cache wrapped data for 24 hours
const CACHE_DURATION = 24 * 60 * 60 * 1000;

export function useAnnualWrapped(userId) {
  const cacheKey = `wrapped_${userId}`;
  const [wrapped, setWrapped] = useState(() => {
    const cached = localStorage.getItem(cacheKey);
    return cached ? JSON.parse(cached) : null;
  });

  // Fetch only if cache is stale
  useEffect(() => {
    const cached = localStorage.getItem(cacheKey);
    const lastFetch = localStorage.getItem(`${cacheKey}_time`);
    const isCacheStale = !lastFetch || Date.now() - JSON.parse(lastFetch) > CACHE_DURATION;

    if (!cached || isCacheStale) {
      fetch(`/users/${userId}/annual-wrapped`)
        .then(res => res.json())
        .then(data => {
          localStorage.setItem(cacheKey, JSON.stringify(data));
          localStorage.setItem(`${cacheKey}_time`, JSON.stringify(Date.now()));
          setWrapped(data);
        });
    }
  }, [userId]);

  return { wrapped };
}
```

---

## Mobile Responsiveness

```css
@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .metric-card {
    padding: 16px;
  }

  .score-circle {
    width: 80px;
    height: 80px;
  }

  .classification {
    font-size: 16px;
  }
}
```

---

## Integration Timeline

1. **Week 1:** Add metric cards to existing dashboard
2. **Week 2:** Implement caching and performance optimization
3. **Week 3:** Add analytics tracking for user interactions
4. **Week 4:** Mobile responsiveness and accessibility testing

---

## Questions & Support

- For backend questions: See [IMPLEMENTATION_VERDICT.md](../IMPLEMENTATION_VERDICT.md)
- For data structure questions: See response examples above
- For performance issues: Check caching section

