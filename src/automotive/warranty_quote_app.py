
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Dict, List

import fitz  # PyMuPDF
import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = REPO_ROOT / 'data' / 'reference' / 'automotive'
VEHICLE_PDF = DATA_DIR / 'vehicle_details.pdf'
COMPONENT_PDF = DATA_DIR / 'component_prices.pdf'
LABOUR_PDF = DATA_DIR / 'labour_prices.pdf'
LOG_FILE = Path('complaints_log.txt')


def extract_text_from_pdf(pdf_path: Path) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f'Missing reference PDF: {pdf_path}')
    with fitz.open(pdf_path) as doc:
        return ''.join(page.get_text() for page in doc)


def _lines_to_dict(text: str, expected_fields: int) -> List[List[str]]:
    rows: List[List[str]] = []
    for line in text.split('
'):
        parts = [part.strip() for part in line.split(',')]
        if len(parts) >= expected_fields:
            rows.append(parts)
    return rows


def parse_vehicle_details(text: str) -> Dict[str, Dict[str, str]]:
    vehicles: Dict[str, Dict[str, str]] = {}
    for parts in _lines_to_dict(text, 5):
        reg_number, model, purchase_date, mfg_year, warranty_till = parts[:5]
        vehicles[reg_number] = {
            'model': model,
            'purchase_date': purchase_date,
            'mfg_year': mfg_year,
            'warranty_valid_till': warranty_till,
        }
    return vehicles


def parse_component_prices(text: str) -> Dict[str, Dict[str, Dict[str, str]]]:
    prices: Dict[str, Dict[str, Dict[str, str]]] = {}
    for parts in _lines_to_dict(text, 5):
        model, component_id, component_name, price, availability = parts[:5]
        prices.setdefault(model, {})[component_id] = {
            'name': component_name,
            'price': float(price),
            'availability': availability,
        }
    return prices


def parse_labour_prices(text: str) -> Dict[str, Dict[str, float]]:
    labour: Dict[str, Dict[str, float]] = {}
    for parts in _lines_to_dict(text, 4):
        _, component_name, labour_cost, time_to_replace = parts[:4]
        labour[component_name] = {
            'labour_cost': float(labour_cost),
            'time_to_replace': float(time_to_replace),
        }
    return labour


def log_complaints_and_fixes(file_path: Path, reg_number: str, issue: str, quote: Dict) -> None:
    with file_path.open('a', encoding='utf-8') as handle:
        handle.write(f"
Registration Number: {reg_number}
")
        handle.write(f"Issue: {issue}
")
        handle.write('Components to Replace:
')
        for detail in quote['details']:
            handle.write(f" - {detail['component_name']} (ID: {detail['component_id']})
")


def is_under_warranty(warranty_valid_till: str) -> bool:
    current_date = dt.date.today()
    warranty_end_date = dt.datetime.strptime(warranty_valid_till, '%Y-%m-%d').date()
    return current_date <= warranty_end_date


def generate_quote(
    vehicle_details: Dict[str, Dict[str, str]],
    component_prices: Dict[str, Dict[str, Dict[str, str]]],
    labour_prices: Dict[str, Dict[str, float]],
    reg_number: str,
    components_to_replace: List[str],
) -> Dict[str, object]:
    vehicle = vehicle_details.get(reg_number)
    if not vehicle:
        raise KeyError('Vehicle not found.')

    model = vehicle['model']
    if model not in component_prices:
        raise KeyError(f'Component pricing unavailable for model {model}.')

    under_warranty = is_under_warranty(vehicle['warranty_valid_till'])
    quote_details = []
    total_cost = 0.0
    total_time = 0.0

    for component in components_to_replace:
        component = component.strip()
        matches = component_prices[model]
        match_id = next((cid for cid, details in matches.items() if component.lower() in {cid.lower(), details['name'].lower()}), None)
        if not match_id:
            raise KeyError(f'Component {component} not found for model {model}.')

        comp_details = matches[match_id]
        labour_details = labour_prices.get(comp_details['name'])
        if not labour_details:
            raise KeyError(f'Labour details missing for component {comp_details["name"]}.')

        cost = 0.0 if under_warranty else comp_details['price'] + labour_details['labour_cost']
        total_cost += cost
        total_time += labour_details['time_to_replace']

        quote_details.append(
            {
                'component_id': match_id,
                'component_name': comp_details['name'],
                'cost': cost,
                'expected_wait_time': labour_details['time_to_replace'],
            }
        )

    return {'total_cost': total_cost, 'total_time': total_time, 'details': quote_details}


def main() -> None:
    st.title('Vehicle Warranty and Repair Quote Generator')

    try:
        vehicle_details = parse_vehicle_details(extract_text_from_pdf(VEHICLE_PDF))
        component_prices = parse_component_prices(extract_text_from_pdf(COMPONENT_PDF))
        labour_prices = parse_labour_prices(extract_text_from_pdf(LABOUR_PDF))
    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()

    reg_number = st.text_input("Enter vehicle's registration number:")
    if reg_number:
        vehicle = vehicle_details.get(reg_number)
        if not vehicle:
            st.error('Vehicle not found.')
            return

        st.table(pd.DataFrame([vehicle]))
        issue = st.text_area('Describe the issue:')
        components = [item for item in st.text_input('Enter components to replace (comma-separated):').split(',') if item.strip()]

        if st.button('Generate Quote'):
            try:
                quote = generate_quote(vehicle_details, component_prices, labour_prices, reg_number, components)
            except Exception as exc:  # pylint: disable=broad-except
                st.error(str(exc))
            else:
                st.table(pd.DataFrame(quote['details']))
                log_complaints_and_fixes(LOG_FILE, reg_number, issue, quote)
                st.success('Complaint and fix logged successfully.')


if __name__ == '__main__':
    main()
