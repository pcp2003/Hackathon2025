# Quick Reference: What to Remove vs Keep

## 🔴 REMOVE NOW (Not Used, Adding Clutter)

### Backend Endpoints (DELETE):
1. **`POST /api/user-comment`** 
   - Allows user comments + AI responses
   - Implemented but NEVER called from frontend
   - Location: `backend/api/navigation.py` lines 375-406
   - Related NLP function: `speak_user_comment_response()` (also delete)
   - **Impact:** -35 lines, cleaner code

2. **`async check_route_deviation()`** 
   - Stub function that just returns "on_route=True"
   - Should check if user deviated from route, but doesn't
   - Location: `backend/api/navigation.py` lines 408-413
   - **Impact:** -6 lines, removes misleading code

---

## 🟡 KEEP BUT IMPROVE (Unused Now, Needed Later)

### Backend:
- **`/update-location` endpoint** - Keep for Phase 2 (live tracking)
- **Language parameter** throughout - Keep, framework already in place
- **Image analysis** - Good start, will become video analysis

### Frontend:
- **Map component** - Keep for dev testing, remove for blind users
- **ImageAnalyzer** - Keep camera button, remove file upload
- **useGeolocation** - Keep, will integrate with live tracking

---

## 🟢 KEEP & SHIP (Production Ready)

✅ Voice input + transcription  
✅ Route calculation (OSRM)  
✅ Text-to-speech (ElevenLabs)  
✅ Image analysis (GPT-4o-mini)  
✅ Error handling  
✅ All 48 tests passing  

---

## 📊 By The Numbers

| Category | Count | Action |
|----------|-------|--------|
| Unused Endpoints | 2 | DELETE |
| Unused Functions | 2-3 | DELETE |
| Stub Implementations | 1 | IMPLEMENT or DELETE |
| Future Features | 6+ | KEEP, mark as TODO |
| Core Working Features | 6+ | SHIP AS-IS |

---

## Decision Matrix

```
Question: "Should we keep this feature?"

Is it called from frontend? 
├─ YES → Keep (unless broken)
└─ NO  → Is it needed for Phase 2?
         ├─ YES → Keep, add TODO comment
         └─ NO  → DELETE

Is it broken or stub-only?
├─ YES → Fix it or delete it (don't leave broken)
└─ NO  → Keep as-is
```

---

## Estimated Cleanup Time

- **DELETE unused endpoints:** 10 minutes
- **DELETE unused functions:** 5 minutes  
- **Add TODO comments:** 10 minutes
- **Update documentation:** 15 minutes
- **Re-test:** 10 minutes

**Total:** 50 minutes  
**Risk:** Very Low (nothing that's currently used)

---

## Files Affected if We Clean Up

### To Delete/Modify:
- `backend/api/navigation.py` - Remove 2 endpoints
- `backend/services/nlp.py` - Remove 2-3 functions
- `backend/schemas/navigation.py` - Remove related schemas
- Add TODO comments to 3-4 places

### To Keep As-Is:
- `backend/services/routing.py` ✅
- `backend/services/text_to_speech.py` ✅
- `backend/services/image_alert.py` ✅
- `backend/services/transcription.py` ✅
- All frontend components ✅

---

## Recommendation

### For This Demo: ✅ Keep Everything
- All features working correctly
- Code is clean enough for a hackathon
- No breaking changes needed

### For Production: Clean Up After Demo
- Remove unused endpoints (faster API)
- Add TODO comments for future features
- Update documentation
- Remove Map component for blind users
- Simplify to voice-first interface

---

## Next Steps

Option 1: **Do cleanup now** (50 min) → cleaner codebase  
Option 2: **Keep for demo, cleanup later** → focus on features  
Option 3: **Create cleanup branch** → separate work stream  

**My Recommendation:** Option 1 (cleanup is quick, makes code much cleaner)

