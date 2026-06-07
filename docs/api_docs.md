# FraudShield Bot & Operations API Documentation

Base URL: `https://your-domain.com`

All endpoints return JSON. Authentication is via Firebase ID Token (Bearer token in Authorization header) where specified.

---

## Alerts (`/alerts`)

### GET /alerts/advisories

Returns the last 10 advisories from the fraud intelligence database.

**Auth:** No

**Response:**
```json
[
  {
    "_id": "665a1b2c3d4e5f6a7b8c9d0e",
    "source": "RBI",
    "raw_title": "Fraud Alert: Fake KYC Messages",
    "summary_en": [
      "RBI warns against fake KYC messages",
      "Never click on links in SMS",
      "Always verify through official channels"
    ],
    "summary_hi": [
      "RBI ने नकली KYC संदेशों के खिलाफ चेतावनी दी",
      "SMS में लिंक पर कभी क्लिक न करें",
      "हमेशा आधिकारिक माध्यमों से सत्यापित करें"
    ],
    "severity": "HIGH",
    "published_at": "2025-05-20T10:30:00Z",
    "ingested_at": "2025-05-20T10:35:00Z",
    "pushed_to_users": true
  }
]
```

**Error codes:** `500` — Failed to fetch advisories

---

### POST /alerts/advisory

Creates a new advisory. If severity is `HIGH`, it triggers an immediate push notification to all users with instant alert preference.

**Auth:** No

**Request body:**
```json
{
  "source": "NPCI",
  "raw_title": "New UPI Scam Pattern Detected",
  "summary_en": [
    "Fraudsters using fake collect requests",
    "Verify sender before approving any request",
    "Report suspicious UPI IDs to FraudShield"
  ],
  "summary_hi": [
    "धोखेबाज नकली कलेक्ट रिक्वेस्ट का उपयोग कर रहे हैं",
    "कोई भी अनुरोध स्वीकृत करने से पहले प्रेषक की पुष्टि करें",
    "संदिग्ध UPI ID की सूचना FraudShield को दें"
  ],
  "severity": "HIGH"
}
```

**Response:**
```json
{
  "advisory_id": "665a1b2c3d4e5f6a7b8c9d0e",
  "pushed_count": 142
}
```

**Error codes:** `500` — Failed to save advisory

---

### GET /alerts/critical-reports

Returns the last 20 critical fraud reports. User data is masked.

**Auth:** No

**Response:**
```json
[
  {
    "_id": "665a1b2c3d4e5f6a7b8c9d0e",
    "case_id": "FS-20250520-4821",
    "upi_ids": ["scammer@paytm"],
    "phone_numbers": ["9876543210"],
    "scam_type": "KYC Scam",
    "critical_reason": "High confidence fraud with estimated financial loss of ₹15,000",
    "confidence_score": 95,
    "estimated_loss_inr": 15000,
    "npci_email_sent": true,
    "cert_in_email_sent": true,
    "reported_at": "2025-05-20T12:00:00Z"
  }
]
```

**Error codes:** `500` — Failed to fetch critical reports

---

### POST /alerts/test-critical

Sends a test critical alert to a specified user. Only available in `development` environment.

**Auth:** No

**Request body:**
```json
{
  "user_id": "123456789",
  "scam_type": "Test Scam"
}
```

**Response:**
```json
{
  "case_id": "FS-20250520-9034",
  "emails_sent": true,
  "message": "Test critical alert sent successfully"
}
```

**Error codes:**
- `403` — Only available in development mode
- `500` — Test critical alert failed

---

## Community (`/community`)

### GET /community/reports

Returns anonymised recent community fraud reports.

**Auth:** No

**Query params:**
| Param | Type | Default | Max |
|-------|------|---------|-----|
| limit | int | 20 | 50 |

**Response:**
```json
{
  "reports": [
    {
      "city": "Mumbai",
      "scam_type": "Fake Refund",
      "status": "pending",
      "time": "2025-05-20T12:00:00"
    }
  ],
  "total": 1
}
```

**Error codes:** `500` — Failed to fetch community reports

---

### GET /community/leaderboard

Returns top Guardian Points holders in the community.

**Auth:** No

**Query params:**
| Param | Type | Default |
|-------|------|---------|
| limit | int | 10 |

**Response:**
```json
{
  "leaderboard": [
    {
      "telegram_id": "123456789",
      "name": "Rahul",
      "city": "Delhi",
      "guardian_points": 250,
      "badges": ["Fraud Reporter", "Community Guardian"]
    }
  ]
}
```

**Error codes:** `500` — Failed to fetch leaderboard

---

### GET /community/stats

Returns aggregated community statistics. Response is cached in Redis for 10 minutes.

**Auth:** No

**Response:**
```json
{
  "total_upi_ids_reported": 1523,
  "total_phone_numbers_reported": 876,
  "total_community_reports": 3450,
  "verified_reports": 2100,
  "top_scam_type": "KYC Scam",
  "top_city": "Mumbai"
}
```

**Error codes:** `500` — Failed to fetch community stats

---

### GET /community/patterns

Returns all active scam patterns.

**Auth:** No

**Response:**
```json
[
  {
    "name": "Fake KYC",
    "description_en": "Fraudsters send fake KYC expiry messages with phishing links.",
    "description_hi": "धोखेबाज फिशिंग लिंक के साथ नकली KYC एक्सपायरी संदेश भेजते हैं।",
    "reported_cities": ["Mumbai", "Delhi", "Bangalore"]
  }
]
```

**Error codes:** `500` — Failed to fetch scam patterns

---

## Reports (`/reports`)

### POST /reports/submit

Submit a fraud report via the web dashboard. Requires Firebase authentication.

**Auth:** Yes (Bearer token)

**Request body:**
```json
{
  "upi_id": "scammer@paytm",
  "phone": null,
  "scam_type": "Fake Refund",
  "description": "Someone sent me a collect request"
}
```

Either `upi_id` or `phone` must be provided (not both).

**Response:**
```json
{
  "success": true,
  "points_awarded": 10,
  "new_total": 85,
  "badge_earned": null,
  "message": "✅ Report submit ho gayi!\n\n+10 Guardian Points credited 🌟\nTotal Points: 85\n\nShukriya community ko safe rakhne ke liye! 🛡️"
}
```

**Error codes:**
- `400` — Invalid input or duplicate report
- `401` — Missing or invalid Authorization header

---

### GET /reports/lookup/{identifier}

Lookup a UPI ID or phone number in the fraud database. Results are cached in Redis for 1 hour.

**Auth:** No

**Path param:** `identifier` — UPI ID (e.g., `scammer@paytm`) or 10-digit phone number

**Response (found):**
```json
{
  "found": true,
  "risk_level": "HIGH",
  "report_count": 12,
  "scam_type": "KYC Scam",
  "risk_score": 90,
  "verified": true,
  "first_seen": "2025-01-15T10:30:00"
}
```

**Response (not found):**
```json
{
  "found": false,
  "risk_level": null,
  "report_count": 0,
  "scam_type": null,
  "risk_score": null,
  "verified": false,
  "first_seen": null
}
```

**Error codes:** `500` — Lookup failed

---

### GET /reports/my-reports

Returns all fraud reports submitted by the authenticated user.

**Auth:** Yes (Bearer token)

**Response:**
```json
{
  "reports": [
    {
      "_id": "665a1b2c3d4e5f6a7b8c9d0e",
      "upi_id": "scammer@paytm",
      "scam_type": "Fake Refund",
      "description": "Collect request from unknown person",
      "status": "pending",
      "submitted_at": "2025-05-20T12:00:00"
    }
  ]
}
```

**Error codes:**
- `401` — Missing or invalid Authorization header
- `500` — Failed to fetch reports

---

## History (`/history`)

### GET /history/

Returns the authenticated user's analysis history, ordered by most recent first.

**Auth:** Yes (Bearer token)

**Query params:**
| Param | Type | Default | Max |
|-------|------|---------|-----|
| limit | int | 20 | 100 |
| offset | int | 0 | — |

**Response:**
```json
{
  "history": [
    {
      "_id": "665a1b2c3d4e5f6a7b8c9d0e",
      "user_id": "123456789",
      "risk_level": "HIGH",
      "confidence_score": 95,
      "scam_type": "KYC Scam",
      "verdict_en": "This is a confirmed scam attempt.",
      "verdict_hi": "यह एक पुष्ट scam प्रयास है।",
      "action_en": "Do not send any money. Report immediately.",
      "action_hi": "कोई पैसे न भेजें। तुरंत रिपोर्ट करें।",
      "upi_ids_found": ["scammer@paytm"],
      "phone_numbers_found": [],
      "is_critical": true,
      "analysed_at": "2025-05-20T12:00:00"
    }
  ],
  "total": 1,
  "has_more": false
}
```

**Error codes:**
- `401` — Missing or invalid Authorization header
- `500` — Failed to fetch history

---

### GET /history/{history_id}

Returns a single history record. The record must belong to the authenticated user.

**Auth:** Yes (Bearer token)

**Path param:** `history_id` — MongoDB ObjectId as string

**Response:** Single history record (same schema as items in list above)

**Error codes:**
- `401` — Missing or invalid Authorization header
- `404` — History item not found
- `500` — Failed to fetch history item

---

### DELETE /history/{history_id}

Soft-deletes a history record (sets `deleted: true`). The record must belong to the authenticated user.

**Auth:** Yes (Bearer token)

**Path param:** `history_id` — MongoDB ObjectId as string

**Response:**
```json
{
  "success": true,
  "message": "History item deleted"
}
```

**Error codes:**
- `401` — Missing or invalid Authorization header
- `404` — History item not found or unauthorized
- `500` — Failed to delete history item

---

### GET /history/stats/summary

Returns the authenticated user's personal analysis statistics.

**Auth:** Yes (Bearer token)

**Response:**
```json
{
  "total_checks": 47,
  "high_risk_caught": 12,
  "medium_risk_caught": 8,
  "safe_checks": 27,
  "critical_cases": 3,
  "scams_prevented_estimate": 15
}
```

`scams_prevented_estimate` = `high_risk_caught` + `critical_cases`

**Error codes:**
- `401` — Missing or invalid Authorization header
- `500` — Failed to fetch stats
