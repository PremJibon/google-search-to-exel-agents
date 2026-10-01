# Recovery Skill (`skills/recover_skill.md`)

## 1. Purpose
The **Recovery Skill** automatically handles failures during location geocoding, external API queries, network timeouts, rate limiting, and zero-match responses without crashing the application or returning cryptic 500 error messages.

---

## 2. Failure Modes & Automatic Recovery Strategies

### Scenario 1: Nominatim Location Geocoding Fails (`NOT_FOUND`)
- **Root Cause**: Specific neighborhood or spelling is not recognized by Nominatim as a single administrative polygon (e.g., "Kushtia Sadar", misspelled locality).
- **Recovery Strategy**:
  1. Strip the specific neighborhood and geocode the broader `City, Country` first to obtain a base coordinate center.
  2. If resolved, construct a radial bounding box (~3 km to 5 km around the center coordinate) to proceed with Overpass POI retrieval.
  3. Inform user with an informational badge: *"Exact neighborhood boundary not found; expanded search to a 5 km radius around [City]."*

### Scenario 2: Overpass API Endpoint Timeout or HTTP 429 / 504
- **Root Cause**: Overpass public servers occasionally become congested or enforce rate limiting during high traffic.
- **Recovery Strategy**:
  1. Implement automatic server failover across 3 tier-1 public Overpass instances:
     - Primary: `https://overpass-api.de/api/interpreter`
     - Secondary: `https://lz4.overpass-api.de/api/interpreter`
     - Tertiary: `https://overpass.kumi.systems/api/interpreter`
  2. Exponential backoff retry (1.5s ➔ 3.0s).
  3. If all instances fail, notify the user cleanly: *"Overpass public servers are temporarily busy. Please wait 10 seconds and try again."*

### Scenario 3: Category Query Returns Zero Results
- **Root Cause**: Strict tag mismatch (e.g. querying `amenity=gym` instead of `leisure=fitness_centre` or `shop=pet` instead of `amenity=pet_shop`).
- **Recovery Strategy**:
  1. Utilize a Category Synonym Dictionary:
     - "gym" ➔ `leisure=fitness_centre`, `leisure=sports_centre`, `amenity=gym`
     - "restaurant" ➔ `amenity=restaurant`, `amenity=fast_food`, `amenity=cafe`
     - "dentist" / "dental clinic" ➔ `amenity=dentist`, `healthcare=dentist`, `amenity=clinic`
     - "hotel" ➔ `tourism=hotel`, `tourism=motel`, `tourism=guest_house`
  2. If the primary tag query yields 0 results, automatically query the secondary synonym tags before concluding.

### Scenario 4: "Require Phone" Filter Eliminates All Results
- **Root Cause**: In regions where OpenStreetMap contributors haven't added phone numbers, all POIs get filtered out.
- **Recovery Strategy**:
  1. Detect when `raw_count > 0` but `filtered_count == 0` due to `require_phone=True`.
  2. Prompt user in UI: *"Found [N] businesses in this area, but none have public phone numbers listed in OpenStreetMap. Would you like to view them with websites/addresses only?"*
