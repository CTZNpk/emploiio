
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
