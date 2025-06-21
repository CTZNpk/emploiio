"""
Emploio Interview Sheet - Flask Backend Application

This Flask application manages candidate interview data by integrating with:
- RecruitCRM API for candidate management
- Airtable for data storage and organization
- PDFMonkey for generating interview sheets and reports

The app processes candidate forms, generates PDFs, and syncs data across platforms.
"""

import os
import itertools
import datetime as dt
import json
import time
from pprint import pprint

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import requests

from utils.recruit_mapper import recruit_to_form
from utils.custom_field_mapper import build_custom_field_payload, paginated_fetch, build_custom_fields_map
from utils.sales_mapper import generate_airtable_payload_sales, generate_transparent_sales_pdf
from utils.med_mapper import generate_airtable_payload_med, generate_med_transparent_pdf


# ============================================================================
# Configuration and Setup
# ============================================================================

load_dotenv()

# RecruitCRM API Configuration
RECRUITCRM_API_KEY = os.getenv("RECRUITCRM_API_KEY")
RECRUITCRM_BASE_URL = "https://api.recruitcrm.io/v1"
HEADERS = {
    "Authorization": f"Bearer {RECRUITCRM_API_KEY}",
    "Content-Type": "application/json"
}

# PDFMonkey API Configuration
PDFMONKEY_API_KEY = os.getenv("MONKEYPDF_API_KEY")
PDFMONKEY_HEADERS = {
    "Authorization": f"Bearer {PDFMONKEY_API_KEY}",
    "Accept": "application/json"
}

# PDF Template IDs for different document types
SALES_TRANSPARENT_TEMPLATE_ID = "27D99758-E3D4-4661-998C-6DB52835467D"
SALES_ANONYMOUS_TEMPLATE_ID = "E781DCB1-E3D2-41C8-AD05-F176481447AA"
MED_TRANSPARENT_TEMPLATE_ID = "EB0C33E8-3458-4A19-BCE4-C609DDAA71F3"
MED_ANONYMOUS_TEMPLATE_ID = "4AD5DBFA-4803-49FF-B7ED-44720FEEB14F"

# Airtable API Configuration
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = "appE2c4HLRRkHAr3y"
SALES_TABLE_ID = "tbl3FmKzmSWmxJhS0"
MED_TABLE_ID = "tbltjg6SO2Px8PzMy"

app = Flask(__name__)


# ============================================================================
# Utility Functions
# ============================================================================


def fetch_candidate_from_list(candidate_id: int) -> dict | None:
    """
    Fallback method to find candidate by ID when direct API call fails.

    Args:
        candidate_id: The candidate's ID

    Returns:
        Candidate data dictionary or None if not found
    """
    url = f"{RECRUITCRM_BASE_URL}/candidates"
    for candidate in paginated_fetch(url):
        if candidate["id"] == candidate_id:
            return candidate
    return None


# ============================================================================
# Airtable Integration Functions
# ============================================================================

def update_or_create_sales_record(form_data):
    """
    Update existing sales record or create new one based on email.

    Args:
        form_data: Dictionary containing form submission data

    Returns:
        API response or None if operation failed
    """
    email = form_data.get("email")
    if not email:
        print("❌ Email is required for sales record operation")
        return None

    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Search for existing record by email
    search_url = f"https://api.airtable.com/v0/{BASE_ID}/{SALES_TABLE_ID}"
    search_params = {
        "filterByFormula": f"LOWER({{email}}) = '{email.lower()}'"
    }

    search_response = requests.get(
        search_url, headers=headers, params=search_params)

    if search_response.status_code != 200:
        print(f"❌ Error searching sales records: {
              search_response.status_code}")
        print(search_response.text)
        return None

    existing_records = search_response.json().get("records", [])
    payload = {"fields": generate_airtable_payload_sales(form_data)}

    if existing_records:
        # Update existing record
        record_id = existing_records[0]["id"]
        update_url = f"{search_url}/{record_id}"
        response = requests.patch(update_url, headers=headers, json=payload)

        if response.status_code == 200:
            print("✅ Sales record updated successfully")
            return response.json()
        else:
            print(f"❌ Failed to update sales record: {response.status_code}")
            print(response.text)
            return None
    else:
        # Create new record
        response = requests.post(search_url, headers=headers, json=payload)

        if response.status_code in [200, 201]:
            print("✅ New sales record created successfully")
            return response.json()
        else:
            print(f"❌ Failed to create sales record: {response.status_code}")
            print(response.text)
            return None


def update_or_create_medical_record(form_data):
    """
    Update existing medical record or create new one based on email.

    Args:
        form_data: Dictionary containing form submission data

    Returns:
        API response or None if operation failed
    """
    email = form_data.get("email")
    if not email:
        print("❌ Email is required for medical record operation")
        return None

    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Search for existing record by email
    search_url = f"https://api.airtable.com/v0/{BASE_ID}/{MED_TABLE_ID}"
    search_params = {
        "filterByFormula": f"LOWER({{email}}) = '{email.lower()}'"
    }

    search_response = requests.get(
        search_url, headers=headers, params=search_params)

    if search_response.status_code != 200:
        print(f"❌ Error searching medical records: {
              search_response.status_code}")
        print(search_response.text)
        return None

    existing_records = search_response.json().get("records", [])
    payload = {"fields": generate_airtable_payload_med(form_data)}

    if existing_records:
        # Update existing record
        record_id = existing_records[0]["id"]
        update_url = f"{search_url}/{record_id}"
        response = requests.patch(update_url, headers=headers, json=payload)

        if response.status_code == 200:
            print("✅ Medical record updated successfully")
            return response.json()
        else:
            print(f"❌ Failed to update medical record: {response.status_code}")
            print(response.text)
            return None
    else:
        # Create new record
        response = requests.post(search_url, headers=headers, json=payload)

        if response.status_code in [200, 201]:
            print("✅ New medical record created successfully")
            return response.json()
        else:
            print(f"❌ Failed to create medical record: {response.status_code}")
            print(response.text)
            return None


def update_skills_in_airtable(email, skills):
    """
    Update skills field for a candidate record in Airtable.

    Args:
        email: Candidate's email address
        skills: Skills data to update
    """
    if not email or not skills:
        print("❌ Missing email or skills data")
        return

    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Find record by email
    search_url = f"https://api.airtable.com/v0/{BASE_ID}/{MED_TABLE_ID}"
    search_params = {
        "filterByFormula": f"LOWER({{email}}) = '{email.lower()}'"
    }

    response = requests.get(search_url, headers=headers, params=search_params)
    if response.status_code != 200:
        print("❌ Failed to search for candidate record:", response.text)
        return

    records = response.json().get("records", [])
    if not records:
        print("⚠️ No candidate record found with that email")
        return

    # Update skills field
    record_id = records[0]["id"]
    update_payload = {"fields": {"skills": skills}}

    update_response = requests.patch(
        f"{search_url}/{record_id}",
        headers=headers,
        json=update_payload
    )

    if update_response.status_code == 200:
        print("✅ Skills updated successfully in Airtable")
    else:
        print("❌ Failed to update skills:", update_response.text)


# ============================================================================
# PDF Generation Functions
# ============================================================================

def generate_pdf_document(form_data, template_id):
    """
    Generate PDF document using PDFMonkey API.

    Args:
        form_data: Form data for PDF generation
        template_id: PDFMonkey template ID

    Returns:
        API response from PDFMonkey
    """
    # Select appropriate payload generator based on template
    if template_id in [SALES_TRANSPARENT_TEMPLATE_ID, SALES_ANONYMOUS_TEMPLATE_ID]:
        pdf_payload = generate_transparent_sales_pdf(form_data)
    else:  # Medical templates
        pdf_payload = generate_med_transparent_pdf(form_data)

    response = requests.post(
        "https://api.pdfmonkey.io/api/v1/documents",
        json={
            "document": {
                "document_template_id": template_id,
                "payload": pdf_payload,
                "status": "pending"
            }
        },
        headers={"Authorization": f"Bearer {PDFMONKEY_API_KEY}"},
        timeout=30
    )

    return response


def poll_pdf_generation_status(document_id, max_wait_seconds=60, check_interval=5):
    """
    Poll PDFMonkey API until document is ready or timeout occurs.

    Args:
        document_id: PDFMonkey document ID
        max_wait_seconds: Maximum time to wait (default: 60 seconds)
        check_interval: Time between status checks (default: 5 seconds)

    Returns:
        Download URL if successful, None if failed or timed out
    """
    status_url = f"https://api.pdfmonkey.io/api/v1/document_cards/{
        document_id}"
    elapsed_time = 0

    while elapsed_time < max_wait_seconds:
        response = requests.get(status_url, headers=PDFMONKEY_HEADERS)

        if response.status_code != 200:
            print("❌ Error checking PDF generation status:", response.text)
            return None

        document_data = response.json()
        print(f"PDF Status Check: {document_data}")

        status = document_data["document_card"]["status"]

        if status == "success":
            print("✅ PDF generated successfully")
            return document_data["document_card"]["public_share_link"]
        elif status == "failure":
            print("❌ PDF generation failed")
            return None

        time.sleep(check_interval)
        elapsed_time += check_interval

    print("⏰ PDF generation timed out")
    return None


# ============================================================================
# Flask Routes
# ============================================================================

@app.route("/")
def index():
    """Render the main candidate form page."""
    return render_template("kandidatenformular.html")


@app.route("/test")
def test_page():
    """Render the test form page for development/testing."""
    return render_template("test_form.html")


@app.route("/api/custom-fields")
def api_custom_fields():
    """
    API endpoint to get all custom fields mapping.

    Returns:
        JSON mapping of field IDs to field names
    """
    return jsonify(build_custom_fields_map())


@app.route("/debug/cf-meta")
def debug_custom_fields_metadata():
    """
    Debug endpoint to display custom field metadata in readable format.

    Returns:
        HTML formatted display of custom fields with their properties
    """
    url = f"{RECRUITCRM_BASE_URL}/custom-fields/candidates"
    response = requests.get(url, headers=HEADERS, timeout=20)

    if not response.ok:
        return jsonify(
            error=True,
            message=f"Failed to fetch custom fields metadata: {
                response.status_code} {response.text}"
        )

    fields = response.json()
    formatted_output = []

    for field in fields:
        line = f'{field["field_id"]:>4} | {
            field["field_name"]:<40} | {field["field_type"]:>10}'

        # Add dropdown options if applicable
        if field["field_type"] == "dropdown":
            options = [option["value"]
                       for option in field.get("dropdown_options", [])]
            line += f' → {options}'

        formatted_output.append(line)

    return "<pre>" + "\n".join(formatted_output) + "</pre>"


@app.route("/api/kandidat/<int:candidate_id>")
def api_get_candidate(candidate_id: int):
    """
    Get candidate data by ID and update skills in Airtable.

    Args:
        candidate_id: The candidate's ID

    Returns:
        JSON response with candidate data or error message
    """
    # Try direct API call first
    direct_response = requests.get(
        f"{RECRUITCRM_BASE_URL}/candidates/{candidate_id}",
        headers=HEADERS,
        timeout=20
    )

    # Use direct response if successful, otherwise fallback to list search
    candidate_data = (
        direct_response.json() if direct_response.ok
        else fetch_candidate_from_list(candidate_id)
    )

    if not candidate_data:
        return jsonify(
            error=True,
            message=f"Candidate {candidate_id} not found"
        ), 404

    # Extract and update skills in Airtable
    skills = candidate_data.get("skill", "")
    email = candidate_data.get("email")

    if email and skills:
        update_skills_in_airtable(email, skills)
        print(f"Updated skills for {email}: {skills}")

    return jsonify(recruit_to_form(candidate_data))


@app.route("/api/submit", methods=["POST"])
def submit_candidate_form():
    """
    Process candidate form submission.

    Handles:
    - PDF generation (transparent and anonymous versions)
    - Airtable record creation/update
    - RecruitCRM candidate update

    Returns:
        JSON response indicating success or failure
    """
    print(f"[{dt.datetime.now():%H:%M:%S}] Processing form submission")

    form_data = request.form.copy()
    candidate_id = form_data.get("kandidat_slug")

    if not candidate_id:
        return jsonify(
            status="error",
            message="No candidate ID provided"
        ), 400

    branch = form_data.get("branche", "")

    try:
        # Generate PDFs based on branch type
        if "Med" in branch:
            pdf_transparent = generate_pdf_document(
                form_data, MED_TRANSPARENT_TEMPLATE_ID)
            pdf_anonymous = generate_pdf_document(
                form_data, MED_ANONYMOUS_TEMPLATE_ID)
            update_or_create_medical_record(form_data)
        else:
            pdf_transparent = generate_pdf_document(
                form_data, SALES_TRANSPARENT_TEMPLATE_ID)
            pdf_anonymous = generate_pdf_document(
                form_data, SALES_ANONYMOUS_TEMPLATE_ID)
            update_or_create_sales_record(form_data)

        # Extract document IDs from responses
        anonymous_doc_id = pdf_anonymous.json()["document"]["id"]
        transparent_doc_id = pdf_transparent.json()["document"]["id"]

        # Wait for PDFs to be generated and get download URLs
        anonymous_url = poll_pdf_generation_status(anonymous_doc_id)
        transparent_url = poll_pdf_generation_status(transparent_doc_id)

        # Add PDF URLs to form data
        form_data["auswertung"] = transparent_url
        form_data["anonym_auswertung"] = anonymous_url

        # Prepare RecruitCRM payload
        custom_fields = build_custom_field_payload(form_data)

        # Process contact number
        contact_raw = form_data.get("phone")
        contact_number = (
            int(contact_raw) if contact_raw and contact_raw.isdigit()
            else None
        )

        # Process gender ID
        try:
            gender_id = int(form_data.get("geschlecht", 3))
        except (ValueError, TypeError):
            gender_id = 3  # Default gender ID

        # Build complete payload for RecruitCRM
        recruitcrm_payload = {
            "first_name": form_data.get("vorname"),
            "last_name": form_data.get("nachname"),
            "email": form_data.get("email"),
            "contact_number": contact_number,
            "position": form_data.get("aktuelle_position"),
            "gender_id": gender_id,
            "city": form_data.get("wohnort"),
            "current_organization": form_data.get("arbeitgeber_name"),
            "slug": form_data.get("slug"),
            "owner": form_data.get("consultant"),
            "resume": form_data.get("cv_link") if form_data.get("cv_link") else None,
            "xing": form_data.get("xing_link"),
            "linkedin": form_data.get("linkedin_link"),
            "current_salary": form_data.get("current_salary"),
            "salary_expectation": form_data.get("expected_salary"),
            "available_from": form_data.get("verfuegbar_ab"),
            "locality": form_data.get("erreichbare_stadtname"),
            "notice_period": form_data.get("kuendigungsfrist"),
            "custom_fields": custom_fields
        }

        print("RecruitCRM Payload:")
        print(json.dumps(recruitcrm_payload, indent=2))

        # Submit to RecruitCRM
        recruitcrm_url = f"{RECRUITCRM_BASE_URL}/candidates/{candidate_id}"
        recruitcrm_response = requests.post(
            recruitcrm_url,
            headers={**HEADERS, "Accept": "application/json"},
            json=recruitcrm_payload,
            timeout=20
        )

        print("RecruitCRM Response:")
        print(recruitcrm_response.json())

        if recruitcrm_response.status_code != 200:
            return jsonify(
                status="error",
                message=f"RecruitCRM API Error {
                    recruitcrm_response.status_code}: {recruitcrm_response.text}"
            ), recruitcrm_response.status_code

        return jsonify(
            status="success",
            message="Candidate data saved successfully"
        )

    except requests.exceptions.RequestException as e:
        return jsonify(
            status="error",
            message=f"API Request Error: {str(e)}"
        ), 500
    except Exception as e:
        return jsonify(
            status="error",
            message=f"Unexpected error occurred: {str(e)}"
        ), 500


# ============================================================================
# Application Startup
# ============================================================================

def print_flask_routes():
    """Print all registered Flask routes for debugging."""
    print("\n=== Registered Flask Routes ===")
    for rule in app.url_map.iter_rules():
        methods = sorted(
            [method for method in rule.methods if method not in ['HEAD', 'OPTIONS']])
        print(f"{str(rule):<30} → {methods}")
    print()


if __name__ == "__main__":
    print_flask_routes()
    app.run(
        debug=True,
        extra_files=["kandidatenformular.html"]
    )
