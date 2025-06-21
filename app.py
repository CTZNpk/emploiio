
# --------------------------------------------------------------------------- #
#  emploio – Interview-Sheet – Flask-Backend                                  #
# --------------------------------------------------------------------------- #
from pprint import pprint
import os
import itertools
import datetime as dt
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import requests
import cachetools
import json
import time


# -----------------------------  Konfiguration  ----------------------------- #
load_dotenv()
RECRUITCRM_API_KEY = os.getenv("RECRUITCRM_API_KEY")
RECRUITCRM_BASE_URL = "https://api.recruitcrm.io/v1"
HEADERS = {
    "Authorization": f"Bearer {RECRUITCRM_API_KEY}",
    "Content-Type":  "application/json"
}
PDFMONKEY_API_KEY = os.getenv("MONKEYPDF_API_KEY")
SALES_TRANSPARENT_TEMPLATE_ID = "27D99758-E3D4-4661-998C-6DB52835467D"
SALES_ANONYMOUS_TEMPLATE_ID = "E781DCB1-E3D2-41C8-AD05-F176481447AA"
MED_TRANSPARENT_TEMPLATE_ID = "EB0C33E8-3458-4A19-BCE4-C609DDAA71F3"
MED_ANONYMOUS_TEMPLATE_ID = "4AD5DBFA-4803-49FF-B7ED-44720FEEB14F"
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = "appE2c4HLRRkHAr3y"
SALES_TABLE_ID = "tbl3FmKzmSWmxJhS0"
MED_TABLE_ID = "tbltjg6SO2Px8PzMy"


app = Flask(__name__)

# -------------------------  Paginierte Listen-Helfer  ---------------------- #


def paginated(url: str, page_size: int = 100):
    page = 1
    while True:
        r = requests.get(url,
                         # params={"page": page, "per_page": page_size},
                         headers=HEADERS, timeout=20)
        if r.status_code != 200:
            break
        chunk = r.json().get("data", [])
        if not chunk:
            break
        yield from chunk
        page += 1

# ----------------------------  Custom-Field-Cache  ------------------------- #


@cachetools.cached(cachetools.TTLCache(maxsize=1, ttl=30*60))
def build_cf_map() -> dict[int, str]:
    """field_id → field_name für alle Kandidaten-Custom-Fields (‹ 10 Seiten ›)."""
    url = f"{RECRUITCRM_BASE_URL}/candidates"
    cf_map: dict[int, str] = {}
    for cand in itertools.islice(paginated(url), 1_000):
        for cf in cand.get("custom_fields", []):
            cf_map.setdefault(cf["field_id"], cf["field_name"])
    return cf_map


def name_to_id(): return {v: k for k, v in build_cf_map().items()}

# -----------------------------  Fallback-Suche  ---------------------------- #


@app.route("/api/custom-fields")
def api_custom_fields():
    return jsonify(build_cf_map())


@app.route("/debug/cf-meta")
def debug_cf_meta():
    url = f"{RECRUITCRM_BASE_URL}/custom-fields/candidates"
    r = requests.get(url, headers=HEADERS, timeout=20)

    if not r.ok:
        return jsonify(
            error=True,
            message=f"Failed to fetch metadata: {r.status_code} {r.text}"
        )

    fields = r.json()  # it's already a list
    result = []
    for f in fields:
        line = f'{f["field_id"]:>4} | {
            f["field_name"]:<40} | {f["field_type"]:>10}'
        if f["field_type"] == "dropdown":
            opts = [o["value"] for o in f.get("dropdown_options", [])]
            line += f' → {opts}'
        result.append(line)
    return "<pre>" + "\n".join(result) + "</pre>"


def fetch_candidate_from_list(cid: int) -> dict | None:
    url = f"{RECRUITCRM_BASE_URL}/candidates"
    return next((c for c in paginated(url) if c["id"] == cid), None)

# ---------------------------  Mapping → Frontend  -------------------------- #


def update_or_create_sales_record_by_email(form):
    email = form.get("email")
    if not email:
        print("❌ Email is required in form data.")
        return None

    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    search_url = f"https://api.airtable.com/v0/{BASE_ID}/{SALES_TABLE_ID}"
    params = {
        "filterByFormula": f"LOWER({{email}}) = '{email.lower()}'"
    }
    search_response = requests.get(search_url, headers=headers, params=params)

    if search_response.status_code != 200:
        print(f"❌ Error searching records: {search_response.status_code}")
        print(search_response.text)
        return None

    records = search_response.json().get("records", [])

    payload = {
        "fields": generate_airtable_payload_sales(form)
    }

    if records:
        record_id = records[0]["id"]
        update_url = f"{search_url}/{record_id}"
        update_response = requests.patch(
            update_url, headers=headers, json=payload)
        if update_response.status_code == 200:
            print("✅ Record updated successfully")
            return update_response.json()
        else:
            print(f"❌ Failed to update: {update_response.status_code}")
            print(update_response.text)
            return None
    else:
        create_response = requests.post(
            search_url, headers=headers, json=payload)
        if create_response.status_code in [200, 201]:
            print("✅ New record created successfully")
            return create_response.json()
        else:
            print(f"❌ Failed to create: {create_response.status_code}")
            print(create_response.text)
            return None


def update_or_create_med_record_by_email(form):
    email = form.get("email")
    if not email:
        print("❌ Email is required in form data.")
        return None

    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    search_url = f"https://api.airtable.com/v0/{BASE_ID}/{MED_TABLE_ID}"
    params = {
        "filterByFormula": f"LOWER({{email}}) = '{email.lower()}'"
    }
    search_response = requests.get(search_url, headers=headers, params=params)

    if search_response.status_code != 200:
        print(f"❌ Error searching records: {search_response.status_code}")
        print(search_response.text)
        return None

    records = search_response.json().get("records", [])

    payload = {
        # same field structure
        "fields": generate_airtable_payload_med(form)
    }

    if records:
        record_id = records[0]["id"]
        update_url = f"{search_url}/{record_id}"
        update_response = requests.patch(
            update_url, headers=headers, json=payload)
        if update_response.status_code == 200:
            print("✅ Medical record updated successfully")
            return update_response.json()
        else:
            print(f"❌ Failed to update: {update_response.status_code}")
            print(update_response.text)
            return None
    else:
        create_response = requests.post(
            search_url, headers=headers, json=payload)
        if create_response.status_code in [200, 201]:
            print("✅ New medical record created successfully")
            return create_response.json()
        else:
            print(f"❌ Failed to create: {create_response.status_code}")
            print(create_response.text)
            return None


def recruit_to_form(raw: dict) -> dict:
    cf = {f["field_name"]: f["value"] for f in raw.get("custom_fields", [])}
    print(json.dumps(raw, indent=2))

    return {
        # ----- Standardfelder ----- #
        "vorname":          raw.get("first_name"),
        "nachname":         raw.get("last_name"),
        "avatar":           raw.get("avatar"),
        "email":            raw.get("email"),
        "telefon":          raw.get("contact_number"),
        "geschlecht":       raw.get("gender_id"),
        "wohnort":          raw.get("city"),
        "arbeitgeber_name":      raw.get("current_organization"),
        "slug":             raw.get("slug"),
        "consultant":       str(raw.get("owner")),
        "cv_link":          raw.get("resume", {}).get("file_link")
        if isinstance(raw.get("resume"), dict) else None,
        "xing":             raw.get("xing"),
        "linkedin":         raw.get("linkedin"),

        # ----- Beispiel-Customs (erweiterbar) ----- #
        "branche": cf.get("Branche"),
        "kuendigungsfrist": cf.get("Kündigungsfrist"),
        "anstellungsart": cf.get("Aktuelle Anstellungsart"),
        "zusatzqualifikation": cf.get("Zusatzqualifikation"),
        "zusatzbezeichnungen[]": cf.get("Zusatzbezeichnungen"),
        "wechselmotivation": cf.get("Wechselmotivation"),
        "bonus_amount": cf.get("Bonushöhe"),
        "bonus_type": cf.get("Bonustyp"),
        "gehalt_erhoehen": cf.get("Soll das Gehalt erhöht werden?"),
        "key_clients": cf.get("Offen für unsere Key-Clients?"),
        "nicht_an": cf.get("Blacklist: Bitte nicht an diese Unternehmen"),
        "soll_auf_jeden_fall": cf.get("Whitelist: An wen soll der Kandidat auf jeden Fall geschickt werden?"),
        "aufhebungsvertrag_wahrscheinlichkeit": cf.get("Wahrscheinlichkeit auf einen Aufhebungsvertrag"),
        "verfuegbar_ab": cf.get("Ab wann wäre der Kandidat verfügbar?"),
        "arbeitgeber_standort": cf.get("Arbeitsort (Standort)"),
        "additional_benefits": cf.get("Zusatzleistungen (aktuell)"),
        "job_extras": cf.get("Extras (Interview-Notes)"),
        "interview_schwerpunkte": cf.get("Interview-Notes Schwerpunkte"),
        "aktiv_suche": cf.get("Ist der Kandidat aktiv auf der Suche?"),
        "aktiv_bewerbung": cf.get("Ist der Kandidat aktiv in Bewerbungsprozessen?"),
        "weitere_personalvermittlungen": cf.get("Arbeitet der Kandidat mit weiteren Personalvermittlungen zusammen?"),
        "cv_submission_deadline": cf.get("CV wird zugeschickt bis zum"),
        "arbeitgeber_art": cf.get("Art des Arbeitgebers"),
        "kategorie[]": cf.get("Wunsch Job Fachbereich"),
        "verkehrsmittel": cf.get("Welches Verkehrsmittel wird genutzt?"),
        "home_office_aktuell": cf.get("Home-Office (aktuell)"),
        "home_office_gewuenscht": cf.get("Home-Office (gewünscht)"),
        "flexible_arbeitszeiten": cf.get("Wunsch Flexible Arbeitszeiten?"),
        "current_process": cf.get("Aktueller Prozess (IV-Notizen)"),
        "erreichbare_stadtname": cf.get("Erreichbare Städte"),
        "wohnort_plz": cf.get("Wohnort (PLZ)"),
        "wohnort": cf.get("Wohnort (Stadt)"),
        "aktuelle_position": raw.get("position"),
        "radius": cf.get("Pendelbarer Radius (in km)"),
        "current_salary": raw.get("current_salary"),
        "expected_salary": raw.get("salary_expectation"),
        "wuensche_an_den_job": cf.get("Wuensche am neuen Job"),
        "berufliche_erfahrung": cf.get("Aktuelle Berufliche Lage des Kandidaten"),

        # ----- Newly Added Custom Fields ----- #
        "umzugsbereit[]": cf.get("Umzugsbereit"),            # multiselect
        "relevante_berufserfahrung": cf.get("Relevante Berufserfahrung"),
        "berufliche_ziele": cf.get("Berufliche Ziele"),
        "private_ziele": cf.get("Private Ziele"),
        "sonstiges": cf.get("Sonstiges"),
        "umgang_mit_rueckschlaegen": cf.get("Umgang mit Rückschlägen"),
        "weiterentwicklung": cf.get("Weiterentwicklung"),
        "finanzielle_motivation": cf.get("Finanzielle Motivation"),
        "erfolgsmethodik_kpis": cf.get("Erfolgsmethodik & KPIs"),

        "wechselkommitment": cf.get("Wechselkommitment (von 1-10)"),
        "wunschklinik": cf.get("Wunschklinik"),
    }


# -------------------------------  Routen  ---------------------------------- #
@app.route("/")
def index():
    return render_template("kandidatenformular.html")


@app.route("/test")
def test():
    return render_template("test_form.html")


@app.route("/api/kandidat/<int:cid>")
def api_kandidat(cid: int):
    direct = requests.get(f"{RECRUITCRM_BASE_URL}/candidates/{cid}",
                          headers=HEADERS, timeout=20)
    raw = direct.json() if direct.ok else fetch_candidate_from_list(cid)
    skills = raw.get("skill", "")
    email = raw.get("email")
    update_skills_in_airtable(email, skills)
    print(email)
    print(skills)
    if not raw:
        return jsonify(error=True,
                       message=f"Kandidat {cid} nicht gefunden."), 404
    return jsonify(recruit_to_form(raw))


def update_skills_in_airtable(email, skills):
    if not email or not skills:
        print("❌ Missing email or skills")
        return

    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    search_url = f"https://api.airtable.com/v0/{BASE_ID}/{MED_TABLE_ID}"
    params = {
        "filterByFormula": f"LOWER({{email}}) = '{email.lower()}'"
    }

    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        print("❌ Failed to search for record:", response.text)
        return

    records = response.json().get("records", [])
    if not records:
        print("⚠️ No record found with that email")
        return

    record_id = records[0]["id"]
    update_payload = {"fields": {"skills": skills}}

    update_response = requests.patch(
        f"{search_url}/{record_id}",
        headers=headers,
        json=update_payload
    )

    if update_response.status_code == 200:
        print("✅ Skills updated in Airtable")
    else:
        print("❌ Failed to update skills:", update_response.text)
# -------------------------  Payload-Generator  ----------------------------- #


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
# ------------------------------  Submit  ----------------------------------- #


def generate_transparent_sales_pdf(form_data):

    return {
        "kandidat": {
            "vorname": form_data.get("vorname"),
            "nachname": form_data.get("nachname"),
            "email": form_data.get("email"),
            "telefon": form_data.get("phone"),
            "wohnort": form_data.get("wohnort"),
            "aktuelle_organisation": form_data.get("arbeitgeber_name"),
            "aktuelle_position": form_data.get("aktuelle_position"),
            "branche": form_data.get("branche"),
            "kuendigungsfrist": form_data.get("kuendigungsfrist"),
            "verfuegbar_ab": form_data.get("verfuegbar_ab"),
            "homeoffice_aktuell": form_data.get("home_office_aktuell"),
            "homeoffice_wunsch": form_data.get("home_office_gewuenscht"),
            "arbeitsort": form_data.get("arbeitgeber_standort") or form_data.get("wohnort"),
            "aktuelles_gehalt": form_data.get("current_salary_display"),
            "wechselmotiv": form_data.get("wechselmotivation"),
            "foto_url": form_data.get("avatar"),
            "wunschgehalt": form_data.get("expected_salary_display"),
            "umzugsbereitschaft": form_data.get("umzugsbereit[]"),
            "wechselkommitment": form_data.get("wechselkommitment", "Nein"),
            "berufserfahrung": form_data.get("relevante_berufserfahrung", "0"),
            "erfolgsmethodik": form_data.get("erfolgsmethodik_kpis"),
            "umgang_rueckschlaege": form_data.get("umgang_mit_rueckschlaegen"),
            "weiterentwicklung": form_data.get("weiterentwicklung"),
            "finanzielle_motivation": form_data.get("finanzielle_motivation"),
            "sonstiges": form_data.get("sonstiges"),
            "berufliche_ziele": form_data.get("berufliche_ziele"),
            "private_ziele": form_data.get("private_ziele"),
            # NOT PROVIDED
            "vertriebs_erfahrung": form_data.get("relevante_berufserfahrung", "Keine Angaben"),
        }
    }


def generate_airtable_payload_sales(form):
    return {
        "foto_url": form.get("avatar"),
        "vorname": form.get("vorname"),
        "nachname": form.get("nachname"),
        "email": form.get("email"),
        "telefon": form.get("phone"),
        "aktuelle_position": form.get("aktuelle_position"),
        "aktuelle_organisation": form.get("arbeitgeber_name"),
        "aktuelles_gehalt": form.get("current_salary"),
        "wunschgehalt": form.get("expected_salary"),
        "verfuegbar_ab": form.get("verfuegbar_ab"),
        "kuendigungsfrist": form.get("kuendigungsfrist"),
        "umzugsbereitschaft": form.get("umzugsbereit[]"),
        "wechselkommitment": form.get("wechselkommitment"),
        "fachbereich_aktuell": form.get("branche"),
        "arbeitsort": form.get("arbeitgeber_standort") or form.get("wohnort"),
        "wuensche_an_den_neuen_job": form.get("wuensche_an_den_job"),
        "berufliche_erfahrung": form.get("relevante_berufserfahrung"),
        "sonstiges": form.get("sonstiges"),
    }


def generate_airtable_payload_med(form):
    return {
        "foto_url": form.get("avatar"),
        "vorname": form.get("vorname"),
        "nachname": form.get("nachname"),
        "email": form.get("email"),
        "telefon": form.get("phone"),
        "aktuelle_position": form.get("aktuelle_position"),
        "aktuelle_organisation": form.get("arbeitgeber_name"),
        "aktuelles_gehalt": form.get("current_salary"),
        "wunschgehalt": form.get("expected_salary"),
        "verfuegbar_ab": form.get("verfuegbar_ab"),
        "kuendigungsfrist": form.get("kuendigungsfrist"),
        "wechselkommitment": form.get("wechselkommitment"),
        "fachbereich_aktuell": form.get("fachbereich_aktuell"),
        "fachbereich_wunsch": form.get("fachbereich_wunsch"),

        "wohnort": form.get("wohnort"),
        "arbeitsort": form.get("arbeitgeber_standort") or form.get("wohnort"),
        "berufliche_ziele": form.get("berufliche_ziele"),
        "private_ziele": form.get("private_ziele"),
        "sonstiges": form.get("sonstiges"),
        "berufliche_erfahrung": form.get("berufliche_erfahrung"),
    }


def generate_med_transparent_pdf(form_data):
    return {
        "kandidat": {
            "foto_url": form_data.get("avatar", ""),
            "vorname": form_data.get("vorname", ""),
            "nachname": form_data.get("nachname", ""),
            "email": form_data.get("email", ""),
            "telefon": form_data.get("phone", ""),
            "aktuelle_position": form_data.get("aktuelle_position", ""),
            "aktuelle_organisation": form_data.get("arbeitgeber_name", ""),
            "aktuelles_gehalt": form_data.get("current_salary_display", "Nicht angegeben"),
            "wunschgehalt": form_data.get("expected_salary_display", "Nicht angegeben"),
            "verfuegbar_ab": form_data.get("verfuegbar_ab", ""),
            "kuendigungsfrist": form_data.get("kuendigungsfrist", "Nicht angegeben"),
            "umzugsbereitschaft": form_data.get("umzugsbereit[]", "Nein"),
            "wechselkommitment": form_data.get("wechselkommitment", "0"),
            "fachbereich_aktuell": form_data.get("branche", "Nicht angegeben"),
            "fachbereich_wunsch": form_data.get("kategorie[]", "Nicht angegeben"),
            "wohnort": form_data.get("wohnort", ""),
            "berufserfahrung_in_jahren": form_data.get("berufserfahrung", "0"),
            "arbeitsort": form_data.get("arbeitgeber_standort", form_data.get("wohnort", "")),
            "wunschklinik": form_data.get("wunschklinik", "Nicht angegeben"),
            "wunscharbeitsort": form_data.get("wunscharbeitsort", form_data.get("locality", "Nicht angegeben")),
            "wuensche_an_den_neuen_job": form_data.get("wuensche_an_den_job", "Nicht angegeben"),
            "berufliche_erfahrung": form_data.get("berufliche_erfahrung", "Nicht angegeben"),
            "sonstiges": form_data.get("sonstiges", "Keine Bemerkungen")
        }
    }


PDFMONKEY_HEADERS = {
    "Authorization": f"Bearer {PDFMONKEY_API_KEY}",
    "Accept": "application/json"
}


def call_pdfMonkey(form, TemplateId):
    if TemplateId == SALES_TRANSPARENT_TEMPLATE_ID:
        pdf_payload = generate_transparent_sales_pdf(form)
    elif TemplateId == SALES_ANONYMOUS_TEMPLATE_ID:
        pdf_payload = generate_transparent_sales_pdf(form)
    elif TemplateId == MED_TRANSPARENT_TEMPLATE_ID:
        pdf_payload = generate_med_transparent_pdf(form)
    else:
        pdf_payload = generate_med_transparent_pdf(form)

    pdf_response = requests.post(
        "https://api.pdfmonkey.io/api/v1/documents",
        json={
            "document": {
                "document_template_id": TemplateId,
                "payload": pdf_payload,
                "status": "pending"
            }
        },
        headers={"Authorization": f"Bearer {PDFMONKEY_API_KEY}"},
        timeout=30
    )
    return pdf_response


def poll_until_ready(document_id, max_wait=60, interval=5):
    """
    Poll PDFMonkey until the document is ready (status: 'success') or timeout.
    Returns the download_url if ready, or None.
    """
    url = f"https://api.pdfmonkey.io/api/v1/document_cards/{document_id}"
    waited = 0

    while waited < max_wait:
        response = requests.get(url, headers=PDFMONKEY_HEADERS)
        if response.status_code != 200:
            print("Error checking document status:", response.text)
            return None

        data = response.json()
        print(data)
        status = data["document_card"]["status"]

        if status == "success":
            return data["document_card"]["public_share_link"]

        elif status == "failure":
            print("Document generation failed:",
                  )
            return None

        time.sleep(interval)
        waited += interval

    print("Timed out waiting for document.")
    return None


@app.route("/api/submit", methods=["POST"])
def submit():
    print(f"[{dt.datetime.now():%H:%M:%S}]  POST /api/submit")

    form = request.form.copy()
    kid = form.get("kandidat_slug")

    if not kid:

        return jsonify(status="error", message="Keine Kandidaten-ID übergeben"), 400

    branche = form.get("branche")

    if "Med" in branche:
        pdf_transparent_response = call_pdfMonkey(
            form, MED_TRANSPARENT_TEMPLATE_ID)
        pdf_anonymous_response = call_pdfMonkey(
            form, MED_ANONYMOUS_TEMPLATE_ID)
        update_or_create_med_record_by_email(form)
    else:
        pdf_transparent_response = call_pdfMonkey(
            form, SALES_TRANSPARENT_TEMPLATE_ID)
        pdf_anonymous_response = call_pdfMonkey(
            form, SALES_ANONYMOUS_TEMPLATE_ID)
        update_or_create_sales_record_by_email(form)

    anon_id = pdf_anonymous_response.json()["document"]["id"]
    transparent_id = pdf_transparent_response.json()["document"]["id"]

    anon_url = poll_until_ready(anon_id)
    transparent_url = poll_until_ready(transparent_id)

    form["auswertung"] = transparent_url
    form["anonym_auswertung"] = anon_url

    # First handle RecruitCRM API call
    cf = build_custom_field_payload(form)

    contact_raw = form.get("phone")
    contact_number = int(
        contact_raw) if contact_raw and contact_raw.isdigit() else None

    geschlecht = form.get("geschlecht")
    try:
        gender_id = int(geschlecht)
    except (ValueError, TypeError):
        gender_id = 3

    payload = {
        "first_name": form.get("vorname"),
        "last_name": form.get("nachname"),
        "email": form.get("email"),
        "contact_number": contact_number,
        "position": form.get("aktuelle_position"),
        "gender_id": gender_id,
        "city": form.get("wohnort"),
        "current_organization": form.get("arbeitgeber_name"),
        "slug": form.get("slug"),
        "owner": form.get("consultant"),
        "resume": form.get("cv_link") if form.get("cv_link") else None,
        "xing": form.get("xing_link"),
        "linkedin": form.get("linkedin_link"),
        "current_salary": form.get("current_salary"),
        "salary_expectation": form.get("expected_salary"),
        "available_from": form.get("verfuegbar_ab"),
        "locality": form.get("erreichbare_stadtname"),
        "notice_period": form.get("kuendigungsfrist"),
        "custom_fields": cf
    }

    print(json.dumps(payload, indent=2))

    rc_url = f"{RECRUITCRM_BASE_URL}/candidates/{kid}"

    try:
        # First save to RecruitCRM
        r = requests.post(
            rc_url,
            headers={**HEADERS, "Accept": "application/json"},
            json=payload,
            timeout=20
        )

        print(r.json())
        if r.status_code != 200:
            return jsonify(
                status="error",
                message=f"RecruitCRM-Fehler {r.status_code}: {r.text}"
            ), r.status_code

        return jsonify(
            status="success",
            message="Kandidat erfolgreich gespeichert.",
        )

    except requests.exceptions.RequestException as e:
        return jsonify(
            status="error",
            message=f"API Fehler: {str(e)}"
        ), 500

# ------------------------ Debug-Ausgabe aller Regeln ----------------------- #


print("\n=== Aktive Flask-Regeln ===")
for rule in app.url_map.iter_rules():
    print(f"{rule}  →  {sorted(rule.methods)}")
print()  # Leerzeile zur Übersicht
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    app.run(debug=True, extra_files=["kandidatenformular.html"])
# --------------------------------------------------------------------------- #

print("\n=== Aktive Flask-Regeln ===")
pprint(app.url_map.iter_rules())
print()          # Leerzeile für Übersicht

if __name__ == "__main__":
    app.run(debug=True, extra_files=["kandidatenformular.html"])
