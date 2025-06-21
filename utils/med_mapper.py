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
