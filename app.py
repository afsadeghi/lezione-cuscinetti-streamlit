from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import streamlit as st

from learning_path import (
    EVIDENCE_TYPES,
    FINAL_OUTPUTS,
    INTERESTS,
    LAB_ACTIVITIES,
    LEARNING_STEPS,
    LEARNING_TOOLS,
    NEXT_STRATEGIES,
    RESEARCH_SOURCES,
    SYSTEM_IMPACTS,
    build_final_feedback,
    build_final_report,
    build_second_suggestion,
    build_second_summary,
    build_suggestion,
    build_summary,
    research_deadline,
)
from progress_store import ProgressStore, ProgressStoreError


BASE_DIR = Path(__file__).parent
VIDEO_PATH = BASE_DIR / "assets" / "video_cuscinetti.mp4"

st.set_page_config(
    page_title="Esploriamo i cuscinetti",
    page_icon="🧭",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 980px; padding-top: 2rem; padding-bottom: 4rem;}
    .hero {padding: 1.35rem 1.5rem; border-radius: 20px; background: linear-gradient(135deg,#eef6ff,#f5efff); border: 1px solid #cedcf0;}
    .hero h1 {margin: 0 0 .35rem 0; color: #173b5f;}
    .wonder {margin: 2rem 0 1rem; padding: 2.2rem 1.8rem; text-align: center; border-radius: 22px; background: linear-gradient(135deg,#162a46,#4a3571); color: white; box-shadow: 0 14px 32px rgba(22,42,70,.18); animation: reveal 1.2s ease both;}
    .wonder p {font-size: clamp(1.45rem,3vw,2.2rem); line-height: 1.35; font-weight: 700; margin: 0;}
    .your-turn {text-align:center; font-size:1.25rem; font-weight:650; color:#173b5f; animation: reveal 1s ease 1.4s both;}
    .mission {padding: 1.2rem 1.3rem; border-left: 6px solid #6a4bbc; background:#f5f1ff; border-radius:12px;}
    .step-ok {padding: 1rem 1.2rem; border-left: 6px solid #2e7d32; background:#edf7ee; border-radius:12px;}
    .question-title {font-size:1.35rem; line-height:1.4; font-weight:700; color:#173b5f; margin:1.15rem 0 .45rem;}
    @keyframes reveal {from {opacity:0; transform:translateY(12px)} to {opacity:1; transform:translateY(0)}}
    </style>
    """,
    unsafe_allow_html=True,
)


DEFAULTS = {
    "stage": 0,
    "video_done": False,
    "interests": [],
    "deepen_choice": "",
    "learning_tools": [],
    "practice_help": "",
    "lab_activities": [],
    "path_done": False,
    "research_days": 0,
    "return_date_iso": "",
    "return_date_label": "",
    "followup_confirmed": False,
    "second_started": False,
    "progress_level": "",
    "discovery": "",
    "research_sources": [],
    "source_trust": "",
    "idea_change": "",
    "idea_reflection": "",
    "difficulty": "",
    "project_status": "",
    "project_description": "",
    "project_link": "",
    "second_done": False,
    "third_days": 0,
    "third_date_iso": "",
    "third_date_label": "",
    "third_started": False,
    "final_output_type": "",
    "final_project_title": "",
    "technical_problem": "",
    "final_decision": "",
    "final_project_description": "",
    "final_project_link": "",
    "evidence_type": "",
    "evidence_note": "",
    "limitation_area": "",
    "limitation_note": "",
    "alternative_note": "",
    "system_impacts": [],
    "initial_confidence": 30,
    "final_confidence": 60,
    "most_useful_step": "",
    "learning_change": "",
    "next_strategies": [],
    "new_question": "",
    "third_done": False,
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value.copy() if isinstance(value, list) else value)

PERSISTED_KEYS = tuple(DEFAULTS)
try:
    PROGRESS_STORE = ProgressStore.from_secrets(st.secrets)
except Exception:
    PROGRESS_STORE = None


def normalize_student_code(raw_code: str) -> str:
    return re.sub(r"[^A-Z0-9-]", "", raw_code.upper().strip())


def progress_snapshot() -> dict:
    return {key: st.session_state[key] for key in PERSISTED_KEYS}


def snapshot_digest(snapshot: dict | None = None) -> str:
    return json.dumps(snapshot or progress_snapshot(), ensure_ascii=False, sort_keys=True)


def restore_progress(saved: dict) -> None:
    for key in PERSISTED_KEYS:
        if key in saved:
            st.session_state[key] = saved[key]
    st.session_state.stage = min(15, max(0, int(st.session_state.stage)))


def save_progress(force: bool = False) -> bool:
    if PROGRESS_STORE is None or not st.session_state.get("progress_identity_ready"):
        return False
    snapshot = progress_snapshot()
    digest = snapshot_digest(snapshot)
    if not force and digest == st.session_state.get("last_saved_digest"):
        return True
    try:
        PROGRESS_STORE.save(st.session_state.student_code, snapshot)
    except ProgressStoreError as exc:
        st.session_state.save_error = str(exc)
        return False
    st.session_state.last_saved_digest = digest
    st.session_state.save_error = ""
    return True


def go_to(stage: int) -> None:
    st.session_state.stage = max(st.session_state.stage, stage)
    save_progress(force=True)


def reset_lesson() -> None:
    for key, value in DEFAULTS.items():
        st.session_state[key] = value.copy() if isinstance(value, list) else value


if PROGRESS_STORE is not None and not st.session_state.get("progress_identity_ready", False):
    st.title("🧭 Esploriamo i cuscinetti")
    st.subheader("Entra o riprendi il percorso")
    st.write("Inserisci sempre lo stesso codice: ritroverai automaticamente le tue scelte.")
    with st.form("student_access_form"):
        raw_code = st.text_input(
            "Codice personale",
            placeholder="Esempio: AMI-4827",
            help="Usa lettere, numeri o trattino. Non inserire dati personali.",
        )
        access_submit = st.form_submit_button("Entra o continua", type="primary", use_container_width=True)
    if access_submit:
        code = normalize_student_code(raw_code)
        if not 6 <= len(code) <= 20:
            st.warning("Scegli un codice tra 6 e 20 caratteri, usando lettere, numeri o trattino.")
        else:
            try:
                saved_progress = PROGRESS_STORE.load(code)
            except ProgressStoreError as exc:
                st.error(str(exc) + " Riprova tra poco.")
            else:
                reset_lesson()
                if saved_progress:
                    restore_progress(saved_progress)
                st.session_state.student_code = code
                st.session_state.progress_identity_ready = True
                st.session_state.last_saved_digest = snapshot_digest(saved_progress) if saved_progress else ""
                st.session_state.resume_notice = bool(saved_progress)
                save_progress(force=not bool(saved_progress))
                st.rerun()
    st.info("Conserva il codice: potrai continuare anche da un altro dispositivo.")
    st.stop()

save_progress()

st.markdown(
    """
    <div class="hero">
      <h1>🧭 Esploriamo i cuscinetti</h1>
      <p>Non è un'interrogazione. Guarda, scegli ciò che ti incuriosisce e costruisci il tuo percorso.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.pop("resume_notice", False):
    if st.session_state.stage >= 7:
        st.success("Bentornato! Ho recuperato la tua ricerca e possiamo ripartire da dove eri arrivato.")
    else:
        st.success("Bentornato! Ho recuperato le scelte già salvate.")

with st.sidebar:
    st.header("Il tuo percorso")
    labels = [
        "Inizio", "Video", "Meraviglia", "Curiosità", "Come imparare", "Pratica",
        "Prima missione", "Primo rientro", "La ricerca", "Rifletti", "Seconda missione",
        "Secondo rientro", "Presenta", "Metti alla prova", "Come hai imparato", "Sintesi finale",
    ]
    current = min(st.session_state.stage, 15)
    st.progress(current / 15 if current else 0)
    st.caption(f"Fase {current + 1} di 16: {labels[current]}")
    for index, label in enumerate(labels):
        symbol = "✅" if index < current else ("▶️" if index == current else "○")
        st.write(f"{symbol} {label}")
    st.divider()
    if PROGRESS_STORE is not None:
        st.caption(f"☁️ Salvataggio automatico · **{st.session_state.student_code}**")
        if st.session_state.get("save_error"):
            st.warning(st.session_state.save_error)
        if st.button("Cambia studente", use_container_width=True):
            save_progress(force=True)
            reset_lesson()
            for key in ("student_code", "progress_identity_ready", "last_saved_digest", "save_error"):
                st.session_state.pop(key, None)
            st.rerun()
    else:
        st.caption("Modalità prova locale: i dati restano solo in questa sessione.")
    with st.expander("Ricominciare"):
        if st.button("Azzera il percorso", use_container_width=True):
            reset_lesson()
            save_progress(force=True)
            st.rerun()


if st.session_state.stage == 0:
    st.subheader("Un piccolo componente, una grande idea")
    st.write(
        "Questo breve video è soltanto l'inizio. Non devi ricordare tutto: osserva e nota che cosa accende la tua curiosità."
    )
    c1, c2, c3 = st.columns(3)
    c1.info("**Guarda**\n\nSegui il movimento e i componenti.")
    c2.info("**Scegli**\n\nIndica ciò che vuoi capire meglio.")
    c3.info("**Costruisci**\n\nRicevi una proposta adatta ai tuoi interessi.")
    if st.button("Inizia l'esplorazione →", type="primary", use_container_width=True):
        go_to(1)
        st.rerun()

elif st.session_state.stage == 1:
    st.subheader("1. Guarda il video")
    if VIDEO_PATH.exists():
        st.video(str(VIDEO_PATH))
    else:
        st.warning("Il video non è ancora presente nella cartella assets.")
    st.info("Quando il video termina, premi il pulsante. Non ci sono domande di verifica.")
    if st.button("Ho terminato il video", type="primary", use_container_width=True):
        st.session_state.video_done = True
        go_to(2)
        st.rerun()

elif st.session_state.stage == 2:
    st.markdown(
        """
        <div class="wonder"><p>Che meraviglia l’ingegno umano: anche dietro un piccolo cuscinetto c’è una grande idea che rende più semplice il nostro mondo.</p></div>
        <div class="your-turn">Ora tocca a te: quale parte di questa idea ti incuriosisce di più?</div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("Scopri cosa ti interessa →", type="primary", use_container_width=True):
        go_to(3)
        st.rerun()

elif st.session_state.stage == 3:
    st.subheader("2. Cosa ti incuriosisce?")
    st.write("Non stiamo controllando ciò che sai. Scegli fino a tre aspetti che vorresti capire meglio.")
    with st.form("interests_form"):
        interests = st.multiselect(
            "I miei interessi",
            INTERESTS,
            default=st.session_state.interests,
            max_selections=3,
            placeholder="Scegli da uno a tre argomenti",
        )
        submitted = st.form_submit_button("Conferma le mie curiosità", type="primary", use_container_width=True)
    if submitted:
        if not interests:
            st.warning("Scegli almeno un argomento: anche una piccola curiosità è sufficiente.")
        else:
            st.session_state.interests = interests
            go_to(4)
            st.rerun()

elif st.session_state.stage == 4:
    st.subheader("3. Come preferisci approfondire?")
    with st.form("learning_form"):
        deepen = st.radio(
            "Ti piacerebbe approfondire almeno uno degli argomenti scelti?",
            ["Sì", "Forse, se trovo un modo interessante", "Non ancora"],
            index=(
                ["Sì", "Forse, se trovo un modo interessante", "Non ancora"].index(st.session_state.deepen_choice)
                if st.session_state.deepen_choice in ["Sì", "Forse, se trovo un modo interessante", "Non ancora"]
                else None
            ),
        )
        st.markdown(
            '<p class="question-title">Quali strumenti useresti più volentieri? '
            'Puoi sceglierne più di uno.</p>',
            unsafe_allow_html=True,
        )
        tools = st.multiselect(
            "Strumenti preferiti",
            LEARNING_TOOLS,
            default=st.session_state.learning_tools,
            placeholder="Scegli i mezzi che preferisci",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Continua", type="primary", use_container_width=True)
    if submitted:
        if deepen is None or not tools:
            st.warning("Indica una risposta e almeno uno strumento, anche se non hai ancora una preferenza.")
        else:
            st.session_state.deepen_choice = deepen
            st.session_state.learning_tools = tools
            go_to(5)
            st.rerun()

elif st.session_state.stage == 5:
    st.subheader("4. Imparare facendo")
    with st.form("practice_form"):
        practice_help = st.radio(
            "Secondo te, un'esperienza pratica ti aiuterebbe a comprendere meglio i cuscinetti?",
            ["Sì", "Non lo so ancora", "No"],
            index=(
                ["Sì", "Non lo so ancora", "No"].index(st.session_state.practice_help)
                if st.session_state.practice_help in ["Sì", "Non lo so ancora", "No"]
                else None
            ),
        )
        activities = st.multiselect(
            "Quali attività proveresti? Puoi sceglierne più di una.",
            LAB_ACTIVITIES,
            default=st.session_state.lab_activities,
            placeholder="Scegli le attività che ti attirano",
        )
        submitted = st.form_submit_button("Costruisci il mio percorso", type="primary", use_container_width=True)
    if submitted:
        if practice_help is None:
            st.warning("Indica se la pratica potrebbe aiutarti.")
        elif practice_help != "No" and not activities:
            st.warning("Scegli almeno un'attività che proveresti.")
        else:
            st.session_state.practice_help = practice_help
            st.session_state.lab_activities = activities
            st.session_state.path_done = True
            go_to(6)
            st.rerun()

elif st.session_state.stage == 6:
    suggestion = build_suggestion(
        st.session_state.interests,
        st.session_state.learning_tools,
        st.session_state.lab_activities,
    )
    st.markdown(
        '<div class="step-ok"><strong>Hai costruito il tuo percorso.</strong><br>Le tue scelte non sono un voto: indicano da dove può partire la tua esplorazione.</div>',
        unsafe_allow_html=True,
    )
    st.subheader("La tua prima missione")
    st.markdown(f"### {suggestion.title}")
    st.write(suggestion.mission)
    st.info(suggestion.first_step)

    with st.expander("Rivedi le tue scelte", expanded=True):
        st.write("**Ti incuriosisce:** " + "; ".join(st.session_state.interests))
        st.write("**Preferisci usare:** " + "; ".join(st.session_state.learning_tools))
        if st.session_state.lab_activities:
            st.write("**Vorresti provare:** " + "; ".join(st.session_state.lab_activities))

    st.divider()
    st.subheader("Quanto tempo ti serve per la tua ricerca?")
    st.write("Scegli un tempo realistico. Non è una gara: l'obiettivo è tornare con almeno una scoperta, una domanda o un'idea.")
    with st.form("research_time_form"):
        research_days = st.radio(
            "Tempo a disposizione",
            [3, 7, 14],
            format_func=lambda value: f"{value} giorni",
            index=None,
            horizontal=True,
        )
        schedule = st.form_submit_button("Fissa il prossimo incontro", type="primary", use_container_width=True)
    if schedule:
        if research_days is None:
            st.warning("Scegli 3, 7 oppure 14 giorni.")
        else:
            iso_date, date_label = research_deadline(research_days)
            st.session_state.research_days = research_days
            st.session_state.return_date_iso = iso_date
            st.session_state.return_date_label = date_label
            st.session_state.followup_confirmed = True
            go_to(7)
            st.rerun()

elif st.session_state.stage == 7:
    suggestion = build_suggestion(
        st.session_state.interests,
        st.session_state.learning_tools,
        st.session_state.lab_activities,
    )
    days = st.session_state.research_days
    date_label = st.session_state.return_date_label
    student_code = st.session_state.get("student_code", "")

    st.markdown(
        '<div class="step-ok"><strong>Appuntamento fissato!</strong><br>Adesso hai una missione e il tempo necessario per esplorarla.</div>',
        unsafe_allow_html=True,
    )
    st.subheader(f"Ci vediamo tra {days} giorni")
    st.markdown(f"### 📅 {date_label}")
    st.write(
        "Quando tornerai, mi dirai dove sei arrivato, che cosa hai scoperto e quali difficoltà hai incontrato. "
        "Potrai anche inserire un tuo progetto, una fotografia, un disegno o una breve relazione; poi andremo avanti insieme."
    )
    if student_code:
        st.warning(
            f"Per ritrovare questo percorso devi rientrare usando lo stesso codice personale: **{student_code}**"
        )
    else:
        st.warning(
            "Questa è una prova locale. Quando l'app sarà collegata a Supabase, dovrai rientrare usando sempre lo stesso codice personale."
        )
    st.info("Non devi arrivare con una risposta perfetta: basta portare una scoperta, una domanda oppure un tentativo.")

    try:
        remaining_days = (date.fromisoformat(st.session_state.return_date_iso) - date.today()).days
    except (TypeError, ValueError):
        remaining_days = 0
    if remaining_days > 1:
        st.info(f"Mancano ancora **{remaining_days} giorni** all'incontro. Puoi continuare la ricerca oppure condividere già ciò che hai trovato.")
    elif remaining_days == 1:
        st.info("Manca **1 giorno** all'incontro. Puoi continuare la ricerca oppure condividere già ciò che hai trovato.")
    elif remaining_days == 0:
        st.success("È arrivato il giorno del nostro secondo incontro.")
    else:
        st.success("La data stabilita è passata, ma non sei in ritardo: ripartiamo da ciò che sei riuscito a fare.")

    summary = build_summary(
        student_code,
        st.session_state.interests,
        st.session_state.deepen_choice,
        st.session_state.learning_tools,
        st.session_state.practice_help,
        st.session_state.lab_activities,
        suggestion,
        days,
        date_label,
    )
    st.download_button(
        "Scarica il promemoria del mio percorso (.txt)",
        data=summary,
        file_name="percorso_cuscinetti.txt",
        mime="text/plain",
        use_container_width=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Continuo la ricerca", use_container_width=True):
            st.toast("Va bene. Torna con lo stesso codice quando sei pronto.")
    with c2:
        if st.button("Ho qualcosa da condividere →", type="primary", use_container_width=True):
            st.session_state.second_started = True
            go_to(8)
            st.rerun()

elif st.session_state.stage == 8:
    st.subheader("Secondo incontro · Dove sei arrivato?")
    st.write("Qui non misuriamo quanto hai prodotto. Cerchiamo di capire quale passo hai compiuto.")
    progress_options = [
        "Ho appena cominciato",
        "Ho raccolto alcune informazioni",
        "Ho fatto un'osservazione o una prova",
        "Ho sviluppato un'idea o un progetto",
    ]
    trust_options = ["Molto", "Abbastanza", "Poco", "Non so ancora valutarle"]
    with st.form("research_return_form"):
        progress_level = st.radio(
            "Quale frase descrive meglio dove sei arrivato?",
            progress_options,
            index=progress_options.index(st.session_state.progress_level) if st.session_state.progress_level in progress_options else None,
        )
        discovery = st.text_area(
            "Qual è la cosa più interessante o sorprendente che hai scoperto?",
            value=st.session_state.discovery,
            placeholder="Basta anche una frase breve...",
            height=100,
        )
        sources = st.multiselect(
            "Quali fonti o esperienze hai utilizzato?",
            RESEARCH_SOURCES,
            default=st.session_state.research_sources,
        )
        source_trust = st.radio(
            "Quanto ti fidi delle informazioni che hai trovato?",
            trust_options,
            index=trust_options.index(st.session_state.source_trust) if st.session_state.source_trust in trust_options else None,
        )
        submitted = st.form_submit_button("Continua a riflettere", type="primary", use_container_width=True)
    if submitted:
        if progress_level is None or len(discovery.strip()) < 5 or not sources or source_trust is None:
            st.warning("Indica dove sei arrivato, una breve scoperta, almeno una fonte e quanto ti fidi delle informazioni.")
        else:
            st.session_state.progress_level = progress_level
            st.session_state.discovery = discovery.strip()
            st.session_state.research_sources = sources
            st.session_state.source_trust = source_trust
            go_to(9)
            st.rerun()

elif st.session_state.stage == 9:
    st.subheader("Secondo incontro · Come è cambiato il tuo pensiero?")
    st.write("Cambiare idea non significa aver sbagliato: significa aver incontrato nuove informazioni.")
    idea_options = [
        "La mia idea iniziale si è rafforzata",
        "Ho cambiato una parte della mia idea",
        "Ho più dubbi di prima",
        "Non avevo ancora un'idea chiara",
    ]
    project_options = ["No, non ancora", "Ho un'idea", "È in costruzione", "Ho un progetto da presentare"]
    with st.form("metacognition_form"):
        idea_change = st.radio(
            "Dopo la ricerca, quale frase ti rappresenta meglio?",
            idea_options,
            index=idea_options.index(st.session_state.idea_change) if st.session_state.idea_change in idea_options else None,
        )
        idea_reflection = st.text_area(
            "Che cosa ha confermato, cambiato o messo in dubbio la tua idea?",
            value=st.session_state.idea_reflection,
            placeholder="Prima pensavo... ora penso... perché...",
            height=110,
        )
        difficulty = st.text_input(
            "Quale dubbio o difficoltà ti è rimasto? (facoltativo)",
            value=st.session_state.difficulty,
        )
        project_status = st.radio(
            "Hai trasformato la ricerca in qualcosa di concreto?",
            project_options,
            index=project_options.index(st.session_state.project_status) if st.session_state.project_status in project_options else None,
        )
        project_description = st.text_area(
            "Descrivi brevemente la tua idea, prova o progetto (facoltativo)",
            value=st.session_state.project_description,
            height=90,
        )
        project_link = st.text_input(
            "Se esiste, inserisci un collegamento al progetto (facoltativo)",
            value=st.session_state.project_link,
            placeholder="Canva, Drive, GitHub o altro collegamento condivisibile",
        )
        submitted = st.form_submit_button("Costruisci il prossimo passo", type="primary", use_container_width=True)
    if submitted:
        if idea_change is None or len(idea_reflection.strip()) < 5 or project_status is None:
            st.warning("Scegli come è cambiata la tua idea, scrivi una breve riflessione e indica lo stato del progetto.")
        else:
            st.session_state.idea_change = idea_change
            st.session_state.idea_reflection = idea_reflection.strip()
            st.session_state.difficulty = difficulty.strip()
            st.session_state.project_status = project_status
            st.session_state.project_description = project_description.strip()
            st.session_state.project_link = project_link.strip()
            st.session_state.second_done = True
            go_to(10)
            st.rerun()

elif st.session_state.stage == 10:
    second_suggestion = build_second_suggestion(
        st.session_state.interests,
        st.session_state.source_trust,
        st.session_state.idea_change,
        st.session_state.project_status,
    )
    st.markdown(
        '<div class="step-ok"><strong>Hai completato il secondo incontro.</strong><br>Hai osservato non soltanto il cuscinetto, ma anche il modo in cui cerchi, valuti e modifichi le tue idee.</div>',
        unsafe_allow_html=True,
    )
    st.subheader("La tua seconda missione")
    st.markdown(f"### {second_suggestion.title}")
    st.write(second_suggestion.mission)
    st.info(second_suggestion.first_step)
    st.divider()
    st.subheader("Quanto tempo ti serve per il prossimo passo?")
    with st.form("third_meeting_form"):
        third_days = st.radio(
            "Scegli quando incontrarci di nuovo",
            [3, 7, 14],
            format_func=lambda value: f"{value} giorni",
            index=None,
            horizontal=True,
        )
        submitted = st.form_submit_button("Fissa il terzo incontro", type="primary", use_container_width=True)
    if submitted:
        if third_days is None:
            st.warning("Scegli 3, 7 oppure 14 giorni.")
        else:
            iso_date, date_label = research_deadline(third_days)
            st.session_state.third_days = third_days
            st.session_state.third_date_iso = iso_date
            st.session_state.third_date_label = date_label
            go_to(11)
            st.rerun()

elif st.session_state.stage == 11:
    second_suggestion = build_second_suggestion(
        st.session_state.interests,
        st.session_state.source_trust,
        st.session_state.idea_change,
        st.session_state.project_status,
    )
    student_code = st.session_state.get("student_code", "")
    st.markdown(
        '<div class="step-ok"><strong>Secondo incontro concluso.</strong><br>La tua ricerca ora ha una domanda più precisa e un nuovo passo da compiere.</div>',
        unsafe_allow_html=True,
    )
    st.subheader(f"Ci rivediamo tra {st.session_state.third_days} giorni")
    st.markdown(f"### 📅 {st.session_state.third_date_label}")
    st.write(
        "Nel terzo incontro useremo quello che hai scoperto per motivare una decisione, discutere i limiti e collegare il cuscinetto all'intero sistema meccanico."
    )
    if student_code:
        st.warning(f"Rientra usando ancora lo stesso codice personale: **{student_code}**")
    else:
        st.warning("Nella versione online dovrai rientrare usando lo stesso codice personale.")
    st.info("Il tuo obiettivo non è avere ragione: è riuscire a spiegare su quali prove si basa la tua idea e che cosa resta ancora incerto.")

    try:
        remaining_days = (date.fromisoformat(st.session_state.third_date_iso) - date.today()).days
    except (TypeError, ValueError):
        remaining_days = 0
    if remaining_days > 1:
        st.info(f"Mancano ancora **{remaining_days} giorni**. Puoi continuare oppure iniziare già il terzo incontro.")
    elif remaining_days == 1:
        st.info("Manca **1 giorno**. Puoi continuare oppure iniziare già il terzo incontro.")
    elif remaining_days == 0:
        st.success("È arrivato il giorno del terzo incontro.")
    else:
        st.success("La data stabilita è passata, ma il percorso resta aperto: ripartiamo da ciò che hai realizzato.")

    second_summary = build_second_summary(
        student_code,
        st.session_state.progress_level,
        st.session_state.discovery,
        st.session_state.research_sources,
        st.session_state.source_trust,
        st.session_state.idea_change,
        st.session_state.idea_reflection,
        st.session_state.difficulty,
        st.session_state.project_status,
        st.session_state.project_description,
        st.session_state.project_link,
        second_suggestion,
        st.session_state.third_days,
        st.session_state.third_date_label,
    )
    st.download_button(
        "Scarica il promemoria del secondo incontro (.txt)",
        data=second_summary,
        file_name="secondo_incontro_cuscinetti.txt",
        mime="text/plain",
        use_container_width=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Continuo la seconda missione", use_container_width=True):
            st.toast("Va bene. Torna con lo stesso codice quando sei pronto.")
    with c2:
        if st.button("Sono pronto per il terzo incontro →", type="primary", use_container_width=True):
            st.session_state.third_started = True
            go_to(12)
            st.rerun()

elif st.session_state.stage == 12:
    st.subheader("Terzo incontro · Rendi visibile la tua idea")
    st.markdown(
        "> **Un progetto non serve a dimostrare che avevi ragione. Serve a rendere visibile il tuo ragionamento.**"
    )
    st.write("Puoi presentare anche un lavoro incompleto: ciò che conta è spiegare il problema e la decisione che stai proponendo.")
    with st.form("final_project_form"):
        output_type = st.radio(
            "Che cosa porti oggi?",
            FINAL_OUTPUTS,
            index=FINAL_OUTPUTS.index(st.session_state.final_output_type) if st.session_state.final_output_type in FINAL_OUTPUTS else None,
        )
        project_title = st.text_input(
            "Dai un titolo breve al tuo lavoro",
            value=st.session_state.final_project_title,
            placeholder="Esempio: supporto per un piccolo albero rotante",
        )
        technical_problem = st.text_area(
            "Quale problema tecnico vuoi comprendere o risolvere?",
            value=st.session_state.technical_problem,
            placeholder="Il problema è...",
            height=90,
        )
        final_decision = st.text_area(
            "Quale scelta, soluzione o ipotesi proponi?",
            value=st.session_state.final_decision,
            placeholder="Propongo di... perché...",
            height=100,
        )
        project_description = st.text_area(
            "Descrivi brevemente ciò che hai realizzato o immaginato",
            value=st.session_state.final_project_description or st.session_state.project_description,
            height=100,
        )
        project_link = st.text_input(
            "Collegamento a disegno, fotografia o progetto (facoltativo)",
            value=st.session_state.final_project_link or st.session_state.project_link,
            placeholder="Canva, Drive, GitHub o altro collegamento condivisibile",
        )
        submitted = st.form_submit_button("Metti alla prova la mia proposta", type="primary", use_container_width=True)
    if submitted:
        required_text = (project_title, technical_problem, final_decision, project_description)
        if output_type is None or any(len(text.strip()) < 5 for text in required_text):
            st.warning("Scegli che cosa presenti e completa le quattro brevi descrizioni.")
        else:
            st.session_state.final_output_type = output_type
            st.session_state.final_project_title = project_title.strip()
            st.session_state.technical_problem = technical_problem.strip()
            st.session_state.final_decision = final_decision.strip()
            st.session_state.final_project_description = project_description.strip()
            st.session_state.final_project_link = project_link.strip()
            go_to(13)
            st.rerun()

elif st.session_state.stage == 13:
    st.subheader("Terzo incontro · Metti alla prova la tua proposta")
    st.write("Un tecnico non presenta soltanto una soluzione: mostra le prove, riconosce un limite e osserva le conseguenze sul sistema.")
    limitation_options = [
        "Dati sul carico ancora incerti",
        "Materiale o lubrificazione",
        "Dimensioni, montaggio o tolleranze",
        "Durata e manutenzione",
        "Costo o possibilità di costruzione",
        "Sicurezza",
        "Affidabilità delle informazioni",
        "Non ho ancora individuato il limite principale",
    ]
    with st.form("critical_thinking_form"):
        evidence_type = st.radio(
            "Qual è il sostegno principale della tua proposta?",
            EVIDENCE_TYPES,
            index=EVIDENCE_TYPES.index(st.session_state.evidence_type) if st.session_state.evidence_type in EVIDENCE_TYPES else None,
        )
        evidence_note = st.text_area(
            "Spiega in una frase che cosa mostra questa prova",
            value=st.session_state.evidence_note,
            placeholder="Questa prova mi fa pensare che...",
            height=90,
        )
        limitation_area = st.radio(
            "Qual è oggi il punto più debole o incerto della proposta?",
            limitation_options,
            index=limitation_options.index(st.session_state.limitation_area) if st.session_state.limitation_area in limitation_options else None,
        )
        limitation_note = st.text_area(
            "Che cosa dovresti verificare per ridurre questa incertezza?",
            value=st.session_state.limitation_note,
            placeholder="Dovrei misurare, confrontare o provare...",
            height=90,
        )
        alternative_note = st.text_input(
            "Quale alternativa potresti confrontare? (facoltativo)",
            value=st.session_state.alternative_note,
        )
        system_impacts = st.multiselect(
            "Quali parti dell'intero sistema potrebbero essere influenzate dalla tua scelta?",
            SYSTEM_IMPACTS,
            default=st.session_state.system_impacts,
            max_selections=4,
        )
        submitted = st.form_submit_button("Osserva come hai imparato", type="primary", use_container_width=True)
    if submitted:
        if (
            evidence_type is None
            or len(evidence_note.strip()) < 5
            or limitation_area is None
            or len(limitation_note.strip()) < 5
            or not system_impacts
        ):
            st.warning("Indica una prova, un limite, una verifica possibile e almeno una conseguenza sul sistema.")
        else:
            st.session_state.evidence_type = evidence_type
            st.session_state.evidence_note = evidence_note.strip()
            st.session_state.limitation_area = limitation_area
            st.session_state.limitation_note = limitation_note.strip()
            st.session_state.alternative_note = alternative_note.strip()
            st.session_state.system_impacts = system_impacts
            go_to(14)
            st.rerun()

elif st.session_state.stage == 14:
    st.subheader("Terzo incontro · Osserva il tuo modo di imparare")
    st.write("Ora il soggetto non è soltanto il cuscinetto: sei anche tu mentre affronti un problema nuovo.")
    with st.form("final_metacognition_form"):
        c1, c2 = st.columns(2)
        initial_confidence = c1.slider(
            "All'inizio: quanto ti sentivi capace di affrontare l'argomento?",
            0,
            100,
            int(st.session_state.initial_confidence),
            5,
            format="%d%%",
        )
        final_confidence = c2.slider(
            "Adesso: quanto ti senti capace di continuare da solo?",
            0,
            100,
            int(st.session_state.final_confidence),
            5,
            format="%d%%",
        )
        most_useful_step = st.radio(
            "Quale passaggio ti ha aiutato di più?",
            LEARNING_STEPS,
            index=LEARNING_STEPS.index(st.session_state.most_useful_step) if st.session_state.most_useful_step in LEARNING_STEPS else None,
        )
        learning_change = st.text_area(
            "Che cosa hai capito del tuo modo di imparare?",
            value=st.session_state.learning_change,
            placeholder="Ho capito che imparo meglio quando...",
            height=100,
        )
        next_strategies = st.multiselect(
            "Nel prossimo problema, quali strategie vorresti riutilizzare? Scegline fino a tre.",
            NEXT_STRATEGIES,
            default=st.session_state.next_strategies,
            max_selections=3,
        )
        new_question = st.text_input(
            "Quale nuova domanda ti è nata? (facoltativo)",
            value=st.session_state.new_question,
        )
        submitted = st.form_submit_button("Concludi e guarda il mio percorso", type="primary", use_container_width=True)
    if submitted:
        if most_useful_step is None or len(learning_change.strip()) < 5 or not next_strategies:
            st.warning("Indica il passaggio più utile, una breve riflessione e almeno una strategia futura.")
        else:
            st.session_state.initial_confidence = initial_confidence
            st.session_state.final_confidence = final_confidence
            st.session_state.most_useful_step = most_useful_step
            st.session_state.learning_change = learning_change.strip()
            st.session_state.next_strategies = next_strategies
            st.session_state.new_question = new_question.strip()
            st.session_state.third_done = True
            go_to(15)
            st.rerun()

else:
    first_suggestion = build_suggestion(
        st.session_state.interests,
        st.session_state.learning_tools,
        st.session_state.lab_activities,
    )
    feedback = build_final_feedback(
        st.session_state.initial_confidence,
        st.session_state.final_confidence,
        st.session_state.evidence_type,
        st.session_state.system_impacts,
        st.session_state.new_question,
    )
    st.markdown(
        '<div class="step-ok"><strong>Hai completato i tre incontri.</strong><br>Sei partito da una curiosità e sei arrivato a una decisione che sa mostrare prove, limiti e conseguenze.</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Che cosa mostra il tuo percorso")
    st.markdown(f"### {feedback.headline}")
    st.write(feedback.message)
    st.info(feedback.next_habit)

    st.markdown("#### Le tracce del tuo ragionamento")
    st.write("✅ Hai scelto una direzione che ti interessava.")
    st.write("✅ Hai cercato e confrontato informazioni.")
    st.write("✅ Hai reso visibile una decisione tecnica.")
    st.write("✅ Hai riconosciuto un limite della tua proposta.")
    st.write("✅ Hai collegato il componente alle conseguenze sul sistema.")
    st.write("✅ Hai osservato come è cambiato il tuo modo di imparare.")

    if st.session_state.new_question:
        st.success(f"La domanda con cui continui: **{st.session_state.new_question}**")
    else:
        st.success("Il percorso è concluso, ma puoi riaprirlo ogni volta che nasce una nuova domanda.")

    final_data = progress_snapshot()
    final_data["first_mission"] = f"{first_suggestion.title}: {first_suggestion.mission}"
    report = build_final_report(st.session_state.get("student_code", ""), final_data)
    st.download_button(
        "Scarica il dossier finale dei tre incontri (.txt)",
        data=report,
        file_name="dossier_cuscinetti.txt",
        mime="text/plain",
        use_container_width=True,
    )
    st.caption("Questo dossier non assegna un voto: documenta come una curiosità è diventata ricerca, decisione e consapevolezza.")

save_progress()
