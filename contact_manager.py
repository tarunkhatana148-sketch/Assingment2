"""
contact_manager.py
Author : Tarun Khatana
Date   : 2025-11-15 (updated 2025-11-15)
Project: Contact Book - File Handling System (CSV & JSON)
Course : Programming for Problem Solving Using Python (ETCCPP171)
Faculty: Ms. Neha Kaushik

Behavior:
 - On start: ensures contacts.csv (with header) and contacts.json (empty list) exist.
 - Any change (add/update/delete/import/write) writes to both CSV and JSON so files stay synced.
 - Displays absolute paths for CSV, JSON and error log at startup and when files are synced.
 - Provides full CRUD via a simple menu.
 - Error logging to error_log.txt with timestamps and tracebacks.
"""

import csv
import json
import os
import re
import traceback
from datetime import datetime

CSV_FILE = "contacts.csv"
JSON_FILE = "contacts.json"
ERROR_LOG = "error_log.txt"
FIELDNAMES = ["name", "phone", "email"]


def log_error(operation: str, exc: Exception):
    """Append a structured error entry to ERROR_LOG with timestamp and operation."""
    try:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] OPERATION: {operation}\n")
            f.write(f"ERROR: {repr(exc)}\n")
            tb = traceback.format_exc()
            f.write(f"TRACEBACK:\n{tb}\n")
            f.write("-" * 60 + "\n")
    except Exception:
        # If logging itself fails, print to console (do not crash program)
        print("Failed to write to error log.")


def abs_paths_info():
    """Return absolute paths tuple for CSV, JSON and ERROR log."""
    return os.path.abspath(CSV_FILE), os.path.abspath(JSON_FILE), os.path.abspath(ERROR_LOG)


def ensure_csv_exists(show_path: bool = False):
    """Ensure CSV_FILE exists and has header row."""
    try:
        created = False
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
            created = True
        if show_path or created:
            csv_path = os.path.abspath(CSV_FILE)
            print(f"CSV file ready at: {csv_path}")
    except Exception as e:
        log_error("ensure_csv_exists", e)
        print("Unable to create contacts.csv. Check permissions.")


def ensure_json_exists(show_path: bool = False):
    """Ensure JSON_FILE exists and contains an array (possibly empty)."""
    try:
        created = False
        if not os.path.exists(JSON_FILE):
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            created = True
        else:
            # If exists but corrupted / not an array, attempt to fix it
            try:
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("JSON root is not a list")
            except Exception:
                # overwrite with empty list to recover
                with open(JSON_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4, ensure_ascii=False)
                created = True

        if show_path or created:
            json_path = os.path.abspath(JSON_FILE)
            print(f"JSON file ready at: {json_path}")
    except Exception as e:
        log_error("ensure_json_exists", e)
        print("Unable to create or fix contacts.json. Check permissions.")


def sync_files(contacts):
    """
    Write provided contacts list to both CSV and JSON files.
    This ensures both files remain consistent.
    contacts: list of dicts with keys: 'name','phone','email'
    """
    try:
        # Write CSV
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for c in contacts:
                writer.writerow({k: c.get(k, "") for k in FIELDNAMES})

        # Write JSON (pretty)
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=4, ensure_ascii=False)

        # Show file paths after successful sync
        csv_path, json_path, log_path = abs_paths_info()
        print("\nFiles synced successfully:")
        print(f"  CSV : {csv_path}")
        print(f"  JSON: {json_path}")
        print(f"  LOG : {log_path}\n")
    except Exception as e:
        log_error("sync_files", e)
        print("Failed to synchronize files. See error_log.txt.")


def read_contacts():
    """Read and return list of contacts from CSV (preferred)."""
    contacts = []
    try:
        # If CSV missing, ensure existence then return empty
        if not os.path.exists(CSV_FILE):
            ensure_csv_exists(show_path=True)
            ensure_json_exists(show_path=True)
            return contacts

        with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                contact = {k: (row.get(k) or "").strip() for k in FIELDNAMES}
                if any(contact.values()):
                    contacts.append(contact)
        return contacts
    except Exception as e:
        log_error("read_contacts", e)
        print("Failed to read contacts. See error_log.txt.")
        return contacts


def display_contacts(contacts=None):
    """Display contacts in a neat tabular format using f-strings and tabs."""
    try:
        if contacts is None:
            contacts = read_contacts()

        if not contacts:
            print("\nNo contacts to display.\n")
            return

        name_w = max(len("Name"), max((len(c["name"]) for c in contacts), default=0))
        phone_w = max(len("Phone"), max((len(c["phone"]) for c in contacts), default=0))
        email_w = max(len("Email"), max((len(c["email"]) for c in contacts), default=0))

        header = f"{'Name':<{name_w}}\t{'Phone':<{phone_w}}\t{'Email':<{email_w}}"
        print("\n" + header)
        print("-" * (len(header) + 8))
        for c in contacts:
            print(f"{c['name']:<{name_w}}\t{c['phone']:<{phone_w}}\t{c['email']:<{email_w}}")
        print()
    except Exception as e:
        log_error("display_contacts", e)
        print("Failed to display contacts. See error_log.txt.")


def validate_phone(phone: str) -> bool:
    """Basic phone validation: digits only, length 7-15."""
    phone_clean = re.sub(r"\s+", "", phone)
    return phone_clean.isdigit() and 7 <= len(phone_clean) <= 15


def validate_email(email: str) -> bool:
    """Simple email validation (basic pattern)."""
    if not email:
        return True  # allow empty email
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


def is_duplicate(new_contact, contacts):
    """Detect duplicate by name (case-insensitive) + phone."""
    name_lower = new_contact["name"].strip().lower()
    phone = new_contact["phone"].strip()
    for c in contacts:
        if c["name"].strip().lower() == name_lower and c["phone"].strip() == phone:
            return True
    return False


def add_contact():
    """Add a new contact; writes changes to both CSV and JSON (via sync)."""
    try:
        name = input("Enter Name: ").strip()
        if not name:
            print("Name cannot be empty. Aborting add.")
            return

        phone = input("Enter Phone Number: ").strip()
        email = input("Enter Email Address: ").strip()

        if phone and not validate_phone(phone):
            print("Phone looks invalid (digits only, length 7-15).")
            proceed = input("Keep it anyway? (y/n): ").strip().lower()
            if proceed != "y":
                print("Aborting add.")
                return

        if email and not validate_email(email):
            print("Email looks invalid.")
            proceed = input("Keep it anyway? (y/n): ").strip().lower()
            if proceed != "y":
                print("Aborting add.")
                return

        contact = {"name": name, "phone": phone, "email": email}

        ensure_csv_exists()
        ensure_json_exists()
        contacts = read_contacts()
        if is_duplicate(contact, contacts):
            print("A contact with the same name and phone already exists. Aborting add to avoid duplicate.")
            return

        contacts.append(contact)
        sync_files(contacts)
        print(f"Contact for '{name}' added and saved to CSV & JSON.")
    except Exception as e:
        log_error("add_contact", e)
        print("An error occurred while adding contact. See error_log.txt.")


def search_contact(name_query: str):
    """Search contacts by name (case-insensitive substring match)."""
    try:
        contacts = read_contacts()
        found = [c for c in contacts if name_query.lower() in c["name"].lower()]
        return found
    except Exception as e:
        log_error("search_contact", e)
        print("Search failed. See error_log.txt.")
        return []


def update_contact():
    """Update phone and/or email of an existing contact; syncs files afterwards."""
    try:
        name = input("Enter the name of the contact to update: ").strip()
        if not name:
            print("Name is required.")
            return

        contacts = read_contacts()
        matches = [c for c in contacts if c["name"].lower() == name.lower()]
        if not matches:
            print(f"No contact found with the exact name '{name}'. Use search to find similar names.")
            return

        if len(matches) > 1:
            print("Multiple contacts found:")
            for idx, c in enumerate(matches, start=1):
                print(f"{idx}. {c}")
            choice = input("Select the number to update (or press Enter to cancel): ").strip()
            if not choice.isdigit() or not (1 <= int(choice) <= len(matches)):
                print("Invalid selection. Cancelling update.")
                return
            selected = matches[int(choice) - 1]
        else:
            selected = matches[0]

        print("Current details:")
        print(f"Name : {selected['name']}")
        print(f"Phone: {selected['phone']}")
        print(f"Email: {selected['email']}")

        new_phone = input("Enter new phone (press Enter to keep unchanged): ").strip()
        new_email = input("Enter new email (press Enter to keep unchanged): ").strip()

        if new_phone and not validate_phone(new_phone):
            print("New phone looks invalid.")
            proceed = input("Keep it anyway? (y/n): ").strip().lower()
            if proceed != "y":
                print("Aborting update.")
                return

        if new_email and not validate_email(new_email):
            print("New email looks invalid.")
            proceed = input("Keep it anyway? (y/n): ").strip().lower()
            if proceed != "y":
                print("Aborting update.")
                return

        updated = False
        for c in contacts:
            if c["name"].lower() == selected["name"].lower() and c["phone"] == selected["phone"] and c["email"] == selected["email"]:
                if new_phone:
                    c["phone"] = new_phone
                if new_email:
                    c["email"] = new_email
                updated = True
                break

        if not updated:
            print("Failed to locate the selected contact in the master list. Aborting.")
            return

        sync_files(contacts)
        print(f"Contact '{selected['name']}' updated in both CSV & JSON.")
    except Exception as e:
        log_error("update_contact", e)
        print("An error occurred while updating contact. See error_log.txt.")


def delete_contact():
    """Delete contact(s) by name (case-insensitive exact match) and sync files."""
    try:
        name = input("Enter the name of the contact to delete: ").strip()
        if not name:
            print("Name is required.")
            return

        contacts = read_contacts()
        remaining = [c for c in contacts if c["name"].lower() != name.lower()]
        removed_count = len(contacts) - len(remaining)

        if removed_count == 0:
            print(f"No contact found with the name '{name}'.")
            return

        confirm = input(f"Are you sure you want to delete {removed_count} contact(s) named '{name}'? (y/n): ").strip().lower()
        if confirm != "y":
            print("Deletion cancelled.")
            return

        sync_files(remaining)
        print(f"Deleted {removed_count} contact(s) named '{name}' and synced files.")
    except Exception as e:
        log_error("delete_contact", e)
        print("An error occurred while deleting contact. See error_log.txt.")


def load_from_json_and_display():
    """
    Load contacts from JSON and display them. If JSON missing/corrupt, offers to recreate from CSV.
    Note: Primary source is CSV; JSON is kept in sync. This function is mainly for viewing JSON contents.
    """
    try:
        ensure_csv_exists()
        ensure_json_exists()

        # Try loading JSON
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                contacts = json.load(f)
            if not isinstance(contacts, list):
                raise ValueError("JSON root is not a list")
        except Exception:
            print(f"JSON file '{JSON_FILE}' missing or corrupted.")
            choice = input("Do you want to create it now from the existing CSV file? (y/n): ").strip().lower()
            if choice == "y":
                contacts = read_contacts()
                sync_files(contacts)
                print(f"Created '{JSON_FILE}' from CSV and synced files.")
            else:
                return

        valid_contacts = []
        for c in contacts:
            if isinstance(c, dict):
                item = {k: str(c.get(k, "")).strip() for k in FIELDNAMES}
                if any(item.values()):
                    valid_contacts.append(item)

        if not valid_contacts:
            print("No valid contacts found in JSON file.")
            return

        print(f"Loaded {len(valid_contacts)} contacts from '{os.path.abspath(JSON_FILE)}':")
        display_contacts(valid_contacts)
    except Exception as e:
        log_error("load_from_json_and_display", e)
        print("Failed to load from JSON. See error_log.txt.")


def import_json_to_csv():
    """
    Import contacts from JSON to CSV (merge) and sync files.
    Duplicate detection uses name (case-insensitive) + phone.
    """
    try:
        ensure_json_exists()
        ensure_csv_exists()

        with open(JSON_FILE, "r", encoding="utf-8") as f:
            json_contacts = json.load(f)

        json_valid = []
        for c in json_contacts:
            if isinstance(c, dict):
                item = {k: str(c.get(k, "")).strip() for k in FIELDNAMES}
                if any(item.values()):
                    json_valid.append(item)

        if not json_valid:
            print("No valid contacts to import from JSON.")
            return

        existing = read_contacts()
        existing_set = set((c["name"].lower(), c["phone"]) for c in existing)
        new_added = 0
        for c in json_valid:
            key = (c["name"].lower(), c["phone"])
            if key not in existing_set:
                existing.append(c)
                existing_set.add(key)
                new_added += 1

        if new_added:
            sync_files(existing)
            print(f"Imported {new_added} new contact(s) from JSON to CSV and synced files.")
        else:
            print("No new contacts were found in JSON to import.")
    except Exception as e:
        log_error("import_json_to_csv", e)
        print("Failed to import JSON to CSV. See error_log.txt.")


def menu():
    csv_path, json_path, log_path = abs_paths_info()
    welcome = f"""
    =============================================
      Welcome to Contact Book (CSV & JSON)

      Behavior:
        - CSV & JSON are auto-created at startup (if missing).
        - Any changes are written to both files (keeps them in sync).

      File Locations:
        CSV  : {csv_path}
        JSON : {json_path}
        LOG  : {log_path}

    =============================================
    """
    print(welcome)

    # Make sure files exist and are sane; show their paths if created
    ensure_csv_exists(show_path=False)
    ensure_json_exists(show_path=False)

    # Print confirmed paths (in case they were created/fixed)
    csv_path, json_path, log_path = abs_paths_info()
    print("Files ready:")
    print(f"  CSV : {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  LOG : {log_path}\n")

    while True:
        print("Menu:")
        print("1. Add Contact")
        print("2. View All Contacts (from CSV)")
        print("3. Search Contact by Name")
        print("4. Update Contact (phone/email)")
        print("5. Delete Contact")
        print("6. Export (force-sync CSV -> JSON)")
        print("7. Load & Display Contacts from JSON")
        print("8. Import Contacts from JSON to CSV (merge)")
        print("9. Exit")

        choice = input("Enter choice (1-9): ").strip()
        if choice == "1":
            add_contact()
        elif choice == "2":
            display_contacts()
        elif choice == "3":
            q = input("Enter name to search: ").strip()
            if q:
                results = search_contact(q)
                if results:
                    print(f"\nFound {len(results)} matching contact(s):")
                    display_contacts(results)
                else:
                    print("No matching contacts found.\n")
            else:
                print("Search query empty.")
        elif choice == "4":
            update_contact()
        elif choice == "5":
            delete_contact()
        elif choice == "6":
            # force sync (reads CSV then overwrites both)
            contacts = read_contacts()
            sync_files(contacts)
            print("Forced sync complete: CSV -> JSON.")
        elif choice == "7":
            load_from_json_and_display()
        elif choice == "8":
            import_json_to_csv()
        elif choice == "9":
            print("Goodbye — files are saved in this folder (contacts.csv, contacts.json).")
            break
        else:
            print("Invalid choice. Enter a number between 1 and 9.")

        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting.")
    except Exception as e:
        log_error("main_unhandled_exception", e)
        print("An unexpected error occurred. See error_log.txt.")