import json


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
