"""Contenuti e regole trasparenti per il percorso sui cuscinetti."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Mapping


INTERESTS = (
    "Come il cuscinetto riduce l'attrito",
    "Funzione di anelli, sfere e gabbia",
    "Carichi radiali e assiali",
    "Materiali e lubrificazione",
    "Calore, rumore e vibrazioni",
    "Cause di usura o rottura",
    "Come scegliere il cuscinetto corretto",
    "Applicazioni nelle macchine reali",
)

LEARNING_TOOLS = (
    "Video o animazioni",
    "Libro o dispensa",
    "Ricerca su Internet",
    "Dialogo con un'intelligenza artificiale",
    "Spiegazione dell'insegnante",
    "Confronto con un compagno",
    "Cataloghi e siti dei produttori",
    "Esperienza in laboratorio",
    "Non ho ancora una preferenza",
)

LAB_ACTIVITIES = (
    "Smontare un componente e cercare il cuscinetto",
    "Osservare e confrontare diversi cuscinetti",
    "Analizzare un cuscinetto usurato",
    "Costruire un piccolo meccanismo",
    "Progettare un attrezzo che utilizza un cuscinetto",
    "Cercare una soluzione a un guasto reale",
    "Fare una ricerca in gruppo",
    "Preparare una breve relazione con fotografie",
    "Discutere le conclusioni con i compagni",
)

RESEARCH_SOURCES = (
    "Internet",
    "Intelligenza artificiale",
    "Libro o dispensa",
    "Insegnante",
    "Compagni",
    "Catalogo di un produttore",
    "Osservazione o prova in laboratorio",
)

FINAL_OUTPUTS = (
    "Un'idea tecnica",
    "Un disegno o modello",
    "Una prova o osservazione",
    "Una relazione",
    "Un progetto in costruzione",
    "Un progetto completato",
    "Una nuova ipotesi da verificare",
)

EVIDENCE_TYPES = (
    "Una osservazione o prova",
    "Il confronto tra almeno due fonti",
    "Un dato di catalogo",
    "Un calcolo",
    "Il parere motivato di un esperto",
    "Un modello o prototipo funzionante",
    "Per ora soprattutto la mia intuizione",
)

SYSTEM_IMPACTS = (
    "Sicurezza",
    "Affidabilità e durata",
    "Manutenzione",
    "Attrito ed energia",
    "Costo",
    "Montaggio e ingombri",
    "Rumore e vibrazioni",
    "Impatto ambientale",
)

LEARNING_STEPS = (
    "Il video iniziale",
    "La possibilità di scegliere",
    "La ricerca autonoma",
    "Il confronto tra le fonti",
    "La pratica o il progetto",
    "Il momento di riflessione",
    "Il confronto con altre persone",
)

NEXT_STRATEGIES = (
    "Definire meglio la domanda iniziale",
    "Confrontare almeno due fonti",
    "Fare prima una previsione",
    "Provare concretamente l'idea",
    "Cercare un limite o un'eccezione",
    "Chiedere aiuto quando mi blocco",
    "Annotare come cambia la mia idea",
)


@dataclass(frozen=True)
class LearningSuggestion:
    title: str
    mission: str
    first_step: str


@dataclass(frozen=True)
class FinalFeedback:
    headline: str
    message: str
    next_habit: str


ITALIAN_MONTHS = (
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
)


def research_deadline(days: int, start: date | None = None) -> tuple[str, str]:
    """Restituisce data ISO e data italiana del prossimo incontro."""
    if days not in (3, 7, 14):
        raise ValueError("La durata della ricerca deve essere 3, 7 oppure 14 giorni.")
    target = (start or date.today()) + timedelta(days=days)
    italian = f"{target.day} {ITALIAN_MONTHS[target.month - 1]} {target.year}"
    return target.isoformat(), italian


_MISSIONS = {
    INTERESTS[0]: LearningSuggestion(
        "Sfida: dal trascinamento al rotolamento",
        "Confronta due oggetti, uno che scivola e uno che rotola, e individua dove si perde meno energia.",
        "Scrivi una previsione prima della prova e controlla se l'osservazione la conferma.",
    ),
    INTERESTS[1]: LearningSuggestion(
        "Sfida: riconosci ogni funzione",
        "Osserva un cuscinetto reale o sezionato e associa anello interno, anello esterno, corpi volventi e gabbia alla loro funzione.",
        "Scegli il componente che ti sembra meno importante e prova a immaginare che cosa succederebbe senza di esso.",
    ),
    INTERESTS[2]: LearningSuggestion(
        "Sfida: segui il percorso delle forze",
        "Scegli una macchina reale e disegna con frecce come il carico arriva al cuscinetto.",
        "Distingui il carico radiale da quello assiale prima di cercare una soluzione.",
    ),
    INTERESTS[3]: LearningSuggestion(
        "Sfida: proteggi il movimento",
        "Confronta condizioni pulite, sporche e poco lubrificate e prevedi come cambierebbe la durata del cuscinetto.",
        "Cerca quale funzione svolge il lubrificante oltre a ridurre l'attrito.",
    ),
    INTERESTS[4]: LearningSuggestion(
        "Sfida: ascolta i segnali della macchina",
        "Collega rumore, temperatura e vibrazione a possibili cambiamenti nel funzionamento del cuscinetto.",
        "Prepara tre osservazioni che faresti prima di smontare la macchina.",
    ),
    INTERESTS[5]: LearningSuggestion(
        "Sfida: diventa investigatore del guasto",
        "Analizza un cuscinetto usato o una fotografia e formula due possibili cause del danneggiamento.",
        "Per ogni ipotesi indica quale prova potrebbe confermarla oppure smentirla.",
    ),
    INTERESTS[6]: LearningSuggestion(
        "Sfida: scegli senza indovinare",
        "Parti da una macchina reale e costruisci l'elenco dei dati necessari prima di aprire un catalogo.",
        "Non cercare subito un codice: identifica prima carico, velocità, ambiente, ingombro e durata richiesta.",
    ),
    INTERESTS[7]: LearningSuggestion(
        "Sfida: caccia ai cuscinetti",
        "Individua tre macchine vicine a te che potrebbero contenere cuscinetti e spiega quale movimento devono sostenere.",
        "Scegli il caso più sorprendente e verifica la tua ipotesi con una fonte affidabile.",
    ),
}


def build_suggestion(
    interests: list[str],
    tools: list[str],
    activities: list[str],
) -> LearningSuggestion:
    """Crea una proposta breve partendo dalle preferenze, senza valutare lo studente."""
    primary_interest = next((item for item in interests if item in _MISSIONS), INTERESTS[7])
    base = _MISSIONS[primary_interest]

    if activities:
        first_step = f"Come primo passo hai scelto: {activities[0].lower()}."
    elif tools and tools[0] != "Non ho ancora una preferenza":
        first_step = f"Puoi iniziare usando: {tools[0].lower()}."
    else:
        first_step = base.first_step

    return LearningSuggestion(base.title, base.mission, first_step)


def build_second_suggestion(
    interests: list[str],
    source_trust: str,
    idea_change: str,
    project_status: str,
) -> LearningSuggestion:
    """Propone una seconda missione orientata a pensiero critico e metacognizione."""
    subject = interests[0].lower() if interests else "il funzionamento dei cuscinetti"

    if source_trust in ("Poco", "Non so ancora valutarle"):
        return LearningSuggestion(
            "Sfida: controlla una informazione",
            f"Scegli una affermazione importante su {subject} e cercala in due fonti diverse.",
            "Annota dove le fonti concordano, dove differiscono e quale ti sembra più affidabile, spiegando perché.",
        )
    if idea_change == "Ho cambiato una parte della mia idea":
        return LearningSuggestion(
            "Sfida: ricostruisci il cambiamento",
            "Confronta la tua idea iniziale con quella attuale e individua l'informazione che ha prodotto il cambiamento.",
            "Scrivi: «Prima pensavo…; ora penso…; perché ho osservato o scoperto…». Basta una frase completa.",
        )
    if idea_change == "La mia idea iniziale si è rafforzata":
        return LearningSuggestion(
            "Sfida: cerca l'eccezione",
            "La tua idea sembra confermata. Ora cerca una situazione nella quale potrebbe non funzionare oppure avere un limite.",
            "Una buona idea diventa più solida quando proviamo anche a metterla in difficoltà.",
        )
    if project_status in ("È in costruzione", "Ho un progetto da presentare"):
        return LearningSuggestion(
            "Sfida: metti alla prova il progetto",
            "Individua l'ipotesi più debole del tuo progetto e pensa a una prova semplice per controllarla.",
            "Non devi dimostrare che il progetto è perfetto: devi scoprire che cosa potrebbe migliorarlo.",
        )
    return LearningSuggestion(
        "Sfida: trasforma il dubbio in una domanda",
        f"Formula una domanda precisa su {subject} e prepara due possibili risposte da confrontare.",
        "Per ciascuna risposta indica quale osservazione o informazione potrebbe confermarla.",
    )


def build_summary(
    student_code: str,
    interests: list[str],
    deepen_choice: str,
    tools: list[str],
    practice_help: str,
    activities: list[str],
    suggestion: LearningSuggestion,
    research_days: int = 0,
    return_date_label: str = "",
) -> str:
    """Restituisce una sintesi scaricabile del percorso scelto."""
    bullets = lambda values: "\n".join(f"- {value}" for value in values) or "- Nessuna scelta"
    return f"""IL MIO PERCORSO – CUSCINETTI

Codice: {student_code or "sessione locale"}

COSA MI INCURIOSISCE
{bullets(interests)}

VOGLIA DI APPROFONDIRE
- {deepen_choice or "Non indicata"}

STRUMENTI CHE PREFERISCO
{bullets(tools)}

LA PRATICA PUÒ AIUTARMI?
- {practice_help or "Non indicato"}

ATTIVITÀ CHE PROVEREI
{bullets(activities)}

MISSIONE PROPOSTA
{suggestion.title}
{suggestion.mission}
{suggestion.first_step}

PROSSIMO INCONTRO
- Tempo scelto: {f"{research_days} giorni" if research_days else "Non ancora scelto"}
- Data prevista: {return_date_label or "Da definire"}
- Per continuare, rientrerò usando lo stesso codice personale.

Non è una valutazione: è il punto di partenza del mio percorso.
"""


def build_second_summary(
    student_code: str,
    progress_level: str,
    discovery: str,
    sources: list[str],
    source_trust: str,
    idea_change: str,
    reflection: str,
    difficulty: str,
    project_status: str,
    project_description: str,
    project_link: str,
    suggestion: LearningSuggestion,
    third_days: int,
    third_date_label: str,
) -> str:
    """Crea il promemoria del secondo incontro e della nuova missione."""
    source_lines = "\n".join(f"- {source}" for source in sources) or "- Nessuna fonte indicata"
    return f"""SECONDO INCONTRO – CUSCINETTI

Codice: {student_code or "sessione locale"}

DOVE SONO ARRIVATO
- {progress_level or "Non indicato"}

SCOPERTA PRINCIPALE
{discovery or "Non indicata"}

FONTI UTILIZZATE
{source_lines}

FIDUCIA NELLE FONTI
- {source_trust or "Non indicata"}

COME È CAMBIATA LA MIA IDEA
- {idea_change or "Non indicato"}
{reflection or "Nessuna riflessione inserita"}

DIFFICOLTÀ O DUBBIO
{difficulty or "Nessuno indicato"}

PROGETTO
- Stato: {project_status or "Non indicato"}
- Descrizione: {project_description or "Non inserita"}
- Collegamento: {project_link or "Non inserito"}

NUOVA MISSIONE
{suggestion.title}
{suggestion.mission}
{suggestion.first_step}

TERZO INCONTRO
- Tra {third_days} giorni
- Data prevista: {third_date_label}
- Rientrerò usando lo stesso codice personale.
"""


def build_final_feedback(
    initial_confidence: int,
    final_confidence: int,
    evidence_type: str,
    system_impacts: list[str],
    new_question: str,
) -> FinalFeedback:
    """Restituisce un feedback descrittivo, senza punteggio né finta valutazione."""
    if final_confidence < initial_confidence:
        headline = "Hai sostituito una sicurezza semplice con una consapevolezza più realistica."
        message = (
            "Sentirsi meno sicuri dopo aver approfondito non indica un fallimento: spesso significa "
            "che ora riconosci variabili e limiti che prima non vedevi."
        )
    elif final_confidence > initial_confidence:
        headline = "La tua fiducia ora poggia su un percorso visibile."
        message = (
            "La sicurezza è cresciuta insieme a ricerca, confronto e decisione. Il valore non è il numero, "
            "ma la capacità di spiegare da dove nasce la tua convinzione."
        )
    else:
        headline = "La tua sicurezza è rimasta stabile, ma il ragionamento è diventato più esplicito."
        message = "Ora puoi distinguere meglio ciò che sai, ciò che supponi e ciò che deve ancora essere verificato."

    if evidence_type == "Per ora soprattutto la mia intuizione":
        next_habit = "Conserva l'intuizione, ma trasformala in un'ipotesi e cerca una prova che possa anche smentirla."
    elif len(system_impacts) >= 3:
        next_habit = "Continua a osservare ogni componente come parte di un sistema: una scelta modifica più conseguenze insieme."
    elif new_question.strip():
        next_habit = "Usa la nuova domanda come punto di partenza: una buona ricerca termina generando una domanda migliore."
    else:
        next_habit = "Nel prossimo problema, prova a cercare prima il limite della soluzione che preferisci."
    return FinalFeedback(headline, message, next_habit)


def build_final_report(student_code: str, data: Mapping[str, object]) -> str:
    """Crea il dossier conclusivo dei tre incontri usando soltanto dati già salvati."""
    def value(key: str, fallback: str = "Non indicato") -> str:
        item = data.get(key)
        return str(item).strip() if item not in (None, "") else fallback

    def bullets(key: str) -> str:
        items = data.get(key, [])
        if not isinstance(items, (list, tuple)) or not items:
            return "- Nessuna scelta"
        return "\n".join(f"- {item}" for item in items)

    return f"""DOSSIER FINALE – PERCORSO SUI CUSCINETTI

Codice: {student_code or "sessione locale"}

1. DA DOVE SONO PARTITO
Interessi scelti:
{bullets("interests")}

Prima missione:
{value("first_mission")}

2. CHE COSA HO SCOPERTO
{value("discovery")}

Fonti utilizzate:
{bullets("research_sources")}

Come è cambiata la mia idea:
- {value("idea_change")}
{value("idea_reflection")}

3. CHE COSA HO PRODOTTO
- Tipo: {value("final_output_type")}
- Titolo: {value("final_project_title")}
- Problema affrontato: {value("technical_problem")}
- Decisione proposta: {value("final_decision")}
- Descrizione: {value("final_project_description")}
- Collegamento: {value("final_project_link", "Non inserito")}

4. SU QUALI PROVE MI BASO
- Prova principale: {value("evidence_type")}
{value("evidence_note")}

5. LIMITE E ALTERNATIVA
- Punto debole: {value("limitation_area")}
{value("limitation_note")}
- Alternativa considerata: {value("alternative_note", "Non inserita")}

6. CONSEGUENZE SUL SISTEMA
{bullets("system_impacts")}

7. COME È CAMBIATO IL MIO MODO DI IMPARARE
- Sicurezza iniziale: {value("initial_confidence")} su 100
- Sicurezza finale: {value("final_confidence")} su 100
- Passaggio più utile: {value("most_useful_step")}
{value("learning_change")}

Strategie che userò ancora:
{bullets("next_strategies")}

NUOVA DOMANDA
{value("new_question", "Nessuna domanda inserita")}

Questo documento non assegna un voto: rende visibile il percorso di ricerca, decisione e riflessione.
"""
