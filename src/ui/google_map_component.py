import re
import json
from typing import List, Optional, Dict, Any
from src.models import Lead

def render_google_map_html(
    api_key: str,
    center_lat: float,
    center_lon: float,
    zoom: int = 13,
    leads: Optional[List[Lead]] = None,
    marked_lat: Optional[float] = None,
    marked_lon: Optional[float] = None,
    radius_km: float = 3.0
) -> str:
    """
    Generates a full-featured Google Maps JavaScript interface with:
    - Google Places Search Box / Autocomplete
    - Click-to-pin with reverse geocoding
    - Custom colored markers for leads (Red = No Website, Green = Live Website, Orange = Social Only)
    - Rich interactive InfoWindows with one-click WhatsApp outreach buttons
    """
    leads = leads or []
    lead_markers = []

    for l in leads:
        if l.lat is not None and l.lon is not None:
            is_high = l.lead_score == "HIGH"
            has_web = bool(l.website)
            is_social = any(s in (l.website or "").lower() for s in ["facebook.com", "instagram.com", "wa.me", "fb.me"])
            
            # Marker Pin Color (Google Maps marker icons)
            if is_high or not has_web:
                pin_color = "https://maps.google.com/mapfiles/ms/icons/red-dot.png"
            elif is_social:
                pin_color = "https://maps.google.com/mapfiles/ms/icons/orange-dot.png"
            elif l.website and l.website.startswith("http://"):
                pin_color = "https://maps.google.com/mapfiles/ms/icons/blue-dot.png"
            else:
                pin_color = "https://maps.google.com/mapfiles/ms/icons/green-dot.png"

            # Phone formatting for WhatsApp
            digits = re.sub(r"\D", "", l.phone or "")
            if digits.startswith("01") and len(digits) == 11:
                digits = "880" + digits[1:]
            elif digits.startswith("880"):
                pass
            elif len(digits) == 10 and digits.startswith(("9", "8", "7", "6")):
                digits = "91" + digits

            wa_url = f"https://api.whatsapp.com/send?phone={digits}" if digits else ""

            lead_markers.append({
                "name": l.business_name,
                "lat": float(l.lat),
                "lon": float(l.lon),
                "score": l.lead_score,
                "category": l.category,
                "opportunity": l.opportunity_type,
                "phone": l.phone,
                "website": l.website,
                "pitch": l.pitch_angle[:120] if l.pitch_angle else "",
                "wa_url": wa_url,
                "icon": pin_color
            })

    markers_json = json.dumps(lead_markers)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            html, body {{
                height: 100%;
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            #map {{
                height: 100%;
                width: 100%;
                border-radius: 10px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.1);
            }}
            .pac-card {{
                background-color: #fff;
                padding: 0;
                margin-right: 46px;
                border-radius: 4px;
                box-sizing: border-box;
                min-width: 280px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
            }}
            #pac-container {{
                padding-bottom: 12px;
                margin-right: 12px;
            }}
            .pac-controls {{
                display: inline-block;
                padding: 5px 11px;
            }}
            #pac-input {{
                background-color: #fff;
                font-family: inherit;
                font-size: 14px;
                font-weight: 400;
                margin-left: 12px;
                padding: 10px 14px;
                text-overflow: ellipsis;
                width: calc(100% - 24px);
                max-width: 340px;
                box-sizing: border-box;
                border-radius: 8px;
                border: 1px solid #CBD5E1;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                margin-top: 14px;
                outline: none;
            }}
            #pac-input:focus {{
                border-color: #3B82F6;
            }}
            .info-card {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                min-width: 220px;
                max-width: 280px;
                padding: 4px;
                color: #0F172A;
            }}
            .info-title {{
                font-size: 14px;
                font-weight: 700;
                color: #0F172A;
                margin-bottom: 4px;
            }}
            .info-badge {{
                display: inline-block;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
                margin-bottom: 6px;
            }}
            .badge-high {{ background: #FEE2E2; color: #DC2626; }}
            .badge-med {{ background: #FEF3C7; color: #D97706; }}
            .badge-low {{ background: #D1FAE5; color: #059669; }}
            .info-item {{
                font-size: 12px;
                color: #475569;
                margin-bottom: 4px;
            }}
            .pitch-quote {{
                font-size: 11px;
                font-style: italic;
                color: #334155;
                background: #F8FAFC;
                border-left: 3px solid #3B82F6;
                padding: 4px 6px;
                margin: 6px 0;
                border-radius: 2px;
            }}
            .wa-btn {{
                display: block;
                text-align: center;
                background: #25D366;
                color: white !important;
                padding: 6px 10px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                text-decoration: none;
                margin-top: 6px;
            }}
            .wa-btn:hover {{
                background: #1EBE5D;
            }}
            #click-helper {{
                position: absolute;
                bottom: 24px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(15, 23, 42, 0.85);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                pointer-events: none;
                z-index: 1000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            }}
        </style>
    </head>
    <body>
        <input id="pac-input" class="controls" type="text" placeholder="🔍 Search any city, area, or business on Google Maps..." />
        <div id="map"></div>
        <div id="click-helper">📍 Click anywhere on the map to drop a target scan pin</div>

        <script>
            let map;
            let targetMarker = null;
            let targetCircle = null;
            let infoWindow;
            const markersData = {markers_json};
            const defaultCenter = {{ lat: {center_lat}, lng: {center_lon} }};
            const hasMarked = {"true" if marked_lat is not None and marked_lon is not None else "false"};
            const markedLat = {marked_lat if marked_lat is not None else 0.0};
            const markedLon = {marked_lon if marked_lon is not None else 0.0};
            const radiusMeters = {int(radius_km * 1000)};

            function initMap() {{
                map = new google.maps.Map(document.getElementById("map"), {{
                    center: defaultCenter,
                    zoom: {zoom},
                    mapTypeControl: false,
                    streetViewControl: true,
                    fullscreenControl: true,
                    gestureHandling: 'cooperative',
                    styles: [
                        {{ "featureType": "poi.business", "stylers": [{{ "visibility": "on" }}] }}
                    ]
                }});

                infoWindow = new google.maps.InfoWindow();

                // Places Autocomplete Search Box
                const input = document.getElementById("pac-input");
                const searchBox = new google.maps.places.SearchBox(input);
                map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

                map.addListener("bounds_changed", () => {{
                    searchBox.setBounds(map.getBounds());
                }});

                searchBox.addListener("places_changed", () => {{
                    const places = searchBox.getPlaces();
                    if (!places || places.length === 0) return;

                    const place = places[0];
                    if (!place.geometry || !place.geometry.location) return;

                    map.setCenter(place.geometry.location);
                    map.setZoom(15);
                    setTargetPin(place.geometry.location.lat(), place.geometry.location.lng(), place.name);
                }});

                // Map Click Listener
                map.addListener("click", (e) => {{
                    const lat = e.latLng.lat();
                    const lng = e.latLng.lng();
                    setTargetPin(lat, lng, "Marked Location");
                }});

                // Set initial marked pin if present
                if (hasMarked) {{
                    setTargetPin(markedLat, markedLon, "Active Search Target");
                }}

                // Render discovered business leads
                markersData.forEach((lead) => {{
                    const marker = new google.maps.Marker({{
                        position: {{ lat: lead.lat, lng: lead.lon }},
                        map: map,
                        title: lead.name,
                        icon: lead.icon
                    }});

                    const badgeClass = lead.score === "HIGH" ? "badge-high" : (lead.score === "MEDIUM" ? "badge-med" : "badge-low");
                    const webDisplay = lead.website ? `<a href="${{lead.website}}" target="_blank">${{lead.website.substring(0, 26)}}...</a>` : '<span style="color:#DC2626;font-weight:bold;">❌ No Website</span>';
                    const waBtn = lead.wa_url ? `<a href="${{lead.wa_url}}" target="_blank" class="wa-btn">🟢 Chat on WhatsApp</a>` : '';

                    const content = `
                        <div class="info-card">
                            <div class="info-title">🏢 ${{lead.name}}</div>
                            <span class="info-badge ${{badgeClass}}">${{lead.score}} Priority • ${{lead.category}}</span>
                            <div class="info-item"><strong>Audit:</strong> ${{lead.opportunity}}</div>
                            <div class="info-item"><strong>Phone:</strong> ${{lead.phone || 'None listed'}}</div>
                            <div class="info-item"><strong>Web:</strong> ${{webDisplay}}</div>
                            <div class="pitch-quote">"${{lead.pitch}}"</div>
                            ${{waBtn}}
                        </div>
                    `;

                    marker.addListener("click", () => {{
                        infoWindow.setContent(content);
                        infoWindow.open(map, marker);
                    }});
                }});
            }}

            function setTargetPin(lat, lng, label) {{
                const pos = {{ lat: lat, lng: lng }};

                if (targetMarker) {{
                    targetMarker.setPosition(pos);
                }} else {{
                    targetMarker = new google.maps.Marker({{
                        position: pos,
                        map: map,
                        title: label,
                        icon: "https://maps.google.com/mapfiles/ms/icons/red-pushpin.png",
                        zIndex: 9999
                    }});
                }}

                if (targetCircle) {{
                    targetCircle.setCenter(pos);
                }} else {{
                    targetCircle = new google.maps.Circle({{
                        strokeColor: "#EF4444",
                        strokeOpacity: 0.8,
                        strokeWeight: 2,
                        fillColor: "#EF4444",
                        fillOpacity: 0.15,
                        map: map,
                        center: pos,
                        radius: radiusMeters
                    }});
                }}

                // Geocode coordinates to notify user
                const geocoder = new google.maps.Geocoder();
                geocoder.geocode({{ location: pos }}, (results, status) => {{
                    let addr = `${{lat.toFixed(4)}}, ${{lng.toFixed(4)}}`;
                    if (status === "OK" && results[0]) {{
                        addr = results[0].formatted_address;
                    }}
                    infoWindow.setContent(`
                        <div style="padding: 6px; font-family: inherit;">
                            <strong>🎯 Search Target Pin</strong><br/>
                            <span style="font-size: 12px; color: #475569;">${{addr}}</span><br/>
                            <span style="font-size: 11px; color: #EF4444; font-weight: 600;">Radius: ${{radiusMeters / 1000}} km</span>
                        </div>
                    `);
                    infoWindow.open(map, targetMarker);
                }});
            }}
        </script>
        <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=places&callback=initMap" async defer></script>
    </body>
    </html>
    """
    return html
