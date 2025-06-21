
import cachetools
import itertools
import requests
import os

RECRUITCRM_BASE_URL = "https://api.recruitcrm.io/v1"
RECRUITCRM_API_KEY = os.getenv("RECRUITCRM_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {RECRUITCRM_API_KEY}",
    "Content-Type": "application/json"
}


def build_custom_field_payload(form) -> list[dict]:
    """Convert form data → [{field_id, value}, …] for RecruitCRM PATCH request."""

    def join_multi(n):
        return ", ".join(form.getlist(n)).strip() or None

    wanted = {
        "Branche": form.get("branche"),
        "Kündigungsfrist": form.get("kuendigungsfrist"),
        "Aktuelle Anstellungsart": form.get("anstellungsart"),
        "Zusatzqualifikation": form.get("zusatzqualifikation"),
        "Zusatzbezeichnungen": join_multi("zusatzbezeichnungen[]"),
        "Wechselmotivation": form.get("wechselmotivation"),
        "Bonushöhe": form.get("bonus_amount"),
        "Bonustyp": form.get("bonus_type"),
        "Soll das Gehalt erhöht werden?": form.get("gehalt_erhoehen"),
        "Offen für unsere Key-Clients?": form.get("key_clients"),
        "Blacklist: Bitte nicht an diese Unternehmen": form.get("nicht_an"),
        "Whitelist: An wen soll der Kandidat auf jeden Fall geschickt werden?": form.get("soll_auf_jeden_fall"),
        "Wahrscheinlichkeit auf einen Aufhebungsvertrag": form.get("aufhebungsvertrag_wahrscheinlichkeit"),
        "Ab wann wäre der Kandidat verfügbar?": form.get("verfuegbar_ab"),
        "Arbeitsort (Standort)": form.get("arbeitgeber_standort"),
        "Zusatzleistungen (aktuell)": form.get("additional_benefits"),
        "Extras (Interview-Notes)": form.get("job_extras"),
        "Interview-Notes Schwerpunkte": form.get("interview_schwerpunkte"),
        "Gewünschter Unternehmenstyp": form.get("unternehmen_wahl"),
        "Ist der Kandidat aktiv auf der Suche?": form.get("aktiv_suche"),
        "Ist der Kandidat aktiv in Bewerbungsprozessen?": form.get("aktiv_bewerbung"),
        "Arbeitet der Kandidat mit weiteren Personalvermittlungen zusammen?": form.get("weitere_personalvermittlungen"),
        "CV wird zugeschickt bis zum": form.get("cv_submission_deadline"),
        "Art des Arbeitgebers": form.get("arbeitgeber_art"),
        "Aktueller Arbeitgeber": form.get("arbeitgeber_name"),
        "Wunsch Job Fachbereich": join_multi("kategorie[]"),
        "Welches Verkehrsmittel wird genutzt?": form.get("verkehrsmittel"),
        "Home-Office (aktuell)": form.get("home_office_aktuell"),
        "Home-Office (gewünscht)": form.get("home_office_gewuenscht"),
        "Wunsch Flexible Arbeitszeiten?": form.get("flexible_arbeitszeiten"),
        "Aktueller Prozess (IV-Notizen)": form.get("current_process"),
        "Erreichbare Städte": form.get("erreichbare_stadtname"),
        "Aktuelle Berufliche Lage des Kandidaten": form.get("arbeitgeber_lage"),
        "Wohnort (PLZ)": form.get("wohnort_plz"),
        "Wohnort (Stadt)": form.get("wohnort"),
        "Aktuelle Position": form.get("aktuelle_position"),
        "Pendelbarer Radius (in km)": form.get("radius"),
        "Wuensche am neuen Job": form.get("wuensche_an_den_job"),
        "Aktuelle Berufliche Lage des Kandidaten": form.get("berufliche_erfahrung"),

        # ✅ Newly added custom field mappings
        "Umzugsbereit": join_multi("umzugsbereit[]"),           # multiselect
        "Relevante Berufserfahrung": form.get("relevante_berufserfahrung"),
        "Berufliche Ziele": form.get("berufliche_ziele"),
        "Private Ziele": form.get("private_ziele"),
        "Sonstiges": form.get("sonstiges"),
        "Umgang mit Rückschlägen": form.get("umgang_mit_rueckschlaegen"),
        "Weiterentwicklung": form.get("weiterentwicklung"),
        "Finanzielle Motivation": form.get("finanzielle_motivation"),
        "Erfolgsmethodik & KPIs": form.get("erfolgsmethodik_kpis"),
        "Wechselkommitment (von 1-10)": form.get("wechselkommitment"),
        "Wunschklinik": form.get("wunschklinik"),
        # "Auswertung": form.get("auswertung"),
        # "Auswertung": "HELLO",
        "Anonyme Auswertung": form.get("anonym_auswertung"),
    }

    n2id = name_to_id()  # assumes this returns a dict: {"Branche": 13, ...}
    return [{"field_id": n2id[k], "value": v}
            for k, v in wanted.items()
            if v and k in n2id]


@cachetools.cached(cachetools.TTLCache(maxsize=1, ttl=30*60))
def build_custom_fields_map() -> dict[int, str]:
    """
    Build a mapping of custom field IDs to field names.
    Cached for 30 minutes to reduce API calls.

    Returns:
        Dictionary mapping field_id to field_name for all candidate custom fields
    """
    url = f"{RECRUITCRM_BASE_URL}/candidates"
    custom_fields_map = {}

    # Limit to first 1000 candidates to avoid excessive API calls
    for candidate in itertools.islice(paginated_fetch(url), 1_000):
        for custom_field in candidate.get("custom_fields", []):
            field_id = custom_field["field_id"]
            field_name = custom_field["field_name"]
            custom_fields_map.setdefault(field_id, field_name)

    return custom_fields_map


def get_field_name_to_id_mapping():
    """
    Reverse mapping: field_name -> field_id

    Returns:
        Dictionary mapping field names to field IDs
    """
    return {name: field_id for field_id, name in build_custom_fields_map().items()}


def name_to_id():
    """
    Legacy function name for backward compatibility.
    Returns mapping of field names to field IDs.

    Returns:
        Dictionary mapping field names to field IDs
    """
    return get_field_name_to_id_mapping()


def paginated_fetch(url: str, page_size: int = 100):
    """
    Generator function to fetch paginated data from APIs.

    Args:
        url: The API endpoint URL
        page_size: Number of items per page (default: 100)

    Yields:
        Individual items from the paginated response
    """
    page = 1
    while True:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        if response.status_code != 200:
            break

        data_chunk = response.json().get("data", [])
        if not data_chunk:
            break

        yield from data_chunk
        page += 1
