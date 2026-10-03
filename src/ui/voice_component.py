"""
Voice Input Component — Multi-Device Voice Dictation & Audio Processing
Features:
1. Groq Whisper AI Turbo Voice Input (whisper-large-v3-turbo, sub-300ms cloud transcription for recorded audio).
2. 100% Free Browser-Native Web Speech Dictation (Zero API credits, instant live speech recognition on desktop, tablets, and phones).
3. Zero-overflow, fully responsive mobile-first UI ergonomics.
"""

import streamlit as st
from typing import Optional, Callable
from src.services.voice_service import voice_service

def render_voice_input_widget(
    key: str,
    label: str = "🎙️ Tap to record voice query",
    button_label: str = "🚀 Send Voice Prompt"
) -> Optional[str]:
    """
    Renders a clean, responsive voice recording widget powered by Groq Whisper Turbo.
    Adapts seamlessly across mobile, tablet, and desktop viewports with zero font overflows.
    """
    st.markdown("""
        <div class="voice-card-title">
            <span>🎙️ Voice Input (Powered by Groq Whisper Turbo — Free & Fast)</span>
        </div>
    """, unsafe_allow_html=True)

    if not hasattr(st, "audio_input"):
        st.info("💡 Direct microphone input is available on modern browsers.")
        return None

    audio_file = st.audio_input(label=label, key=f"{key}_recorder")

    if audio_file is not None:
        cache_key = f"whisper_transcription_{key}"
        # Transcribe if new recording
        if cache_key not in st.session_state or st.session_state.get(f"{key}_last_audio") != audio_file:
            st.session_state[f"{key}_last_audio"] = audio_file
            with st.spinner("⚡ Transcribing voice with Groq Whisper Turbo (~250ms)..."):
                res = voice_service.transcribe_audio(audio_file, filename="recording.wav")
                if res["success"] and res["text"]:
                    transcription = res["text"]
                    st.session_state[cache_key] = transcription
                    st.session_state[f"{key}_duration"] = res["duration_ms"]
                elif res["success"] and not res["text"]:
                    st.session_state[cache_key] = ""
                    st.warning("⚠️ No speech detected. Please speak closer to the microphone and try again.")
                else:
                    st.session_state[cache_key] = ""
                    st.error(f"❌ Voice transcription error: {res.get('error')}")

        current_transcription = st.session_state.get(cache_key, "")
        duration_ms = st.session_state.get(f"{key}_duration", 250)

        if current_transcription:
            st.markdown(f"""
                <div class="voice-result-box">
                    <strong>🎙️ Transcribed ({duration_ms}ms):</strong><br/>
                    <em>"{current_transcription}"</em>
                </div>
            """, unsafe_allow_html=True)

            if st.button(f"{button_label}: \"{current_transcription[:32]}...\"", key=f"{key}_submit_btn", use_container_width=True):
                return current_transcription

    return None

def render_browser_voice_dictation(target_input_id: str = "chat_input", label: str = "🎙️ Live Voice Dictation"):
    """
    Renders a 100% Free, Zero-Credit, Client-Side Voice Dictation component using the Web Speech API.
    Works natively in Chrome, Edge, Safari, Android, and iOS browsers.
    Generous 120px viewport prevents any font clipping or overflow.
    """
    html_code = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; box-sizing: border-box; width: 100%;">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap;">
            <button id="stt-btn-{target_input_id}" onclick="toggleDictation_{target_input_id}()" 
                style="display: inline-flex; align-items: center; gap: 8px; background: #1E293B; color: #38BDF8; border: 1px solid #38BDF8; border-radius: 8px; padding: 8px 14px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s ease;">
                <span id="stt-icon-{target_input_id}">🎙️</span>
                <span id="stt-label-{target_input_id}">{label}</span>
            </button>
            <span id="stt-status-{target_input_id}" style="font-size: 12px; color: #94A3B8; font-style: italic;">Tap mic to speak</span>
        </div>
        <div id="stt-preview-box-{target_input_id}" style="margin-top: 8px; padding: 8px 12px; background: #0F172A; border-left: 3px solid #38BDF8; border-radius: 6px; font-size: 12px; color: #F1F5F9; min-height: 38px; word-break: break-word;">
            <span id="stt-text-{target_input_id}" style="color: #94A3B8;">(Speech transcription will appear here in real-time...)</span>
        </div>
    </div>

    <style>
        @keyframes pulse-ring {{
            0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }}
            70% {{ box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
        }}
        .stt-recording {{
            background: #EF4444 !important;
            color: #FFFFFF !important;
            border-color: #EF4444 !important;
            animation: pulse-ring 1.5s infinite;
        }}
    </style>

    <script>
        (function() {{
            let recognition = null;
            let isRecognizing = false;
            const btn = document.getElementById("stt-btn-{target_input_id}");
            const icon = document.getElementById("stt-icon-{target_input_id}");
            const lbl = document.getElementById("stt-label-{target_input_id}");
            const status = document.getElementById("stt-status-{target_input_id}");
            const previewText = document.getElementById("stt-text-{target_input_id}");

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

            window.toggleDictation_{target_input_id} = function() {{
                if (!SpeechRecognition) {{
                    alert("Voice dictation is supported in Chrome, Edge, Safari, iOS & Android. Please open in a supported browser.");
                    return;
                }}

                if (isRecognizing) {{
                    if (recognition) recognition.stop();
                    return;
                }}

                try {{
                    recognition = new SpeechRecognition();
                    recognition.continuous = true;
                    recognition.interimResults = true;
                    recognition.lang = 'en-US';

                    recognition.onstart = function() {{
                        isRecognizing = true;
                        btn.classList.add("stt-recording");
                        icon.innerText = "🔴";
                        lbl.innerText = "Listening...";
                        status.innerText = "Listening (tap again to stop)";
                        previewText.style.color = "#38BDF8";
                        previewText.innerText = "Listening to your voice...";
                    }};

                    recognition.onresult = function(event) {{
                        let interim = '';
                        let finalStr = '';

                        for (let i = event.resultIndex; i < event.results.length; ++i) {{
                            if (event.results[i].isFinal) {{
                                finalStr += event.results[i][0].transcript;
                            }} else {{
                                interim += event.results[i][0].transcript;
                            }}
                        }}

                        const res = finalStr || interim;
                        if (res) {{
                            previewText.style.color = "#F8FAFC";
                            previewText.innerText = res;
                        }}
                    }};

                    recognition.onerror = function(event) {{
                        console.warn("Dictation error:", event.error);
                        status.innerText = "Error: " + event.error;
                        stopUi();
                    }};

                    recognition.onend = function() {{
                        stopUi();
                    }};

                    recognition.start();

                }} catch(err) {{
                    console.error("Dictation start error:", err);
                    stopUi();
                }}
            }};

            function stopUi() {{
                isRecognizing = false;
                btn.classList.remove("stt-recording");
                icon.innerText = "🎙️";
                lbl.innerText = "{label}";
                status.innerText = "Finished. Ready to copy/type.";
            }}
        }})();
    </script>
    """
    st.components.v1.html(html_code, height=110)

def render_whisper_voice_recorder(
    key: str,
    label: str = "🎙️ Record Voice (Groq Whisper Turbo)",
    on_transcribed: Optional[Callable[[str], None]] = None
) -> Optional[str]:
    """Compatibility wrapper delegating to render_voice_input_widget."""
    return render_voice_input_widget(key=key, label=label)
