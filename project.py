import csv
from datetime import date, datetime
import hashlib
import locale
import os
import re
import sys
import time
from pwinput import pwinput

# Safe locale setup across Windows, macOS, and Linux
try:
    locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'en_IN')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, '')
        except locale.Error:
            pass

len_of_text: int = 101


# ---------------------------------------------------------
# CS50P REQUIRED TOP-LEVEL CUSTOM FUNCTIONS
# ---------------------------------------------------------

def output_month(month: int, form: int) -> str:
    """Returns the full or abbreviated name of a given month number (1-12)."""
    months = {
        1: ["January", "Jan"],
        2: ["February", "Feb"],
        3: ["March", "Mar"],
        4: ["April", "Apr"],
        5: ["May", "May"],
        6: ["June", "Jun"],
        7: ["July", "Jul"],
        8: ["August", "Aug"],
        9: ["September", "Sep"],
        10: ["October", "Oct"],
        11: ["November", "Nov"],
        12: ["December", "Dec"],
    }
    return months[month][form]


def output_date(date_, form: int) -> str:
    """Formats a date object or YYYY-MM-DD string into various standard representations."""
    year, month, day = str(date_).split("-")
    if form in [0, 1]:
        month_str = output_month(int(month), form)
        return f"{day} {month_str}, {year}"
    elif form == 2:
        return f"{day}-{month}-{year}"
    elif form == 3:
        return f"{day}/{month}/{year}"
    return f"{day}/{month}/{year}"


def sorted_list_wrt_date(records: list) -> list:
    """Sorts a list of transaction dictionaries chronologically by date string (YYYY-MM-DD)."""
    return sorted(records, key=lambda s: s["date"])


def output_amount(amount: int) -> str:
    """Formats an integer amount as an Indian Rupee currency string with commas."""
    try:
        formatted = locale.format_string("%d", int(amount), grouping=True)
    except Exception:
        # Fallback grouping if locale grouping is unavailable
        formatted = f"{int(amount):,}"
    return f"Rs. {formatted}"


def person_exists(names: list, persons: list, result: list = None) -> dict:
    """Checks whether requested names or 1-based indices exist in record list or search results."""
    if result is None:
        result = []
    person_status_dict = {True: [], False: []}
    if "All" in names and result == []:
        person_status_dict[False] = []
        for person in persons:
            if person["name"] not in person_status_dict[True]:
                person_status_dict[True].append(person["name"])
    else:
        for name in names:
            try:
                idx = int(name)
                if 0 < idx <= len(result):
                    target_name = result[idx - 1]
                    if target_name not in person_status_dict[True]:
                        person_status_dict[True].append(target_name)
                else:
                    person_status_dict[False].append(str(name))
            except ValueError:
                matched = False
                for person in persons:
                    if name == person["name"]:
                        if name not in person_status_dict[True]:
                            person_status_dict[True].append(name)
                        matched = True
                        break
                if not matched and name not in person_status_dict[True]:
                    person_status_dict[False].append(name)
    return person_status_dict


# ---------------------------------------------------------
# FILE STORAGE & HELPER FUNCTIONS
# ---------------------------------------------------------

def read_users() -> list:
    if not os.path.exists("users.csv") or os.path.getsize("users.csv") == 0:
        return []
    with open("users.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def write_users(users: list) -> None:
    with open("users.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["username", "password", "datetime", "failed_attempts", "lockout_time"],
        )
        writer.writeheader()
        writer.writerows(users)


def read_records(username=False) -> list:
    if not os.path.exists("records.csv") or os.path.getsize("records.csv") == 0:
        return []
    transaction_records = []
    with open("records.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if username:
                if row["username"] == username:
                    transaction_records.append(row)
            else:
                transaction_records.append(row)
    return transaction_records


def append_records(records: dict) -> None:
    file_exists = os.path.exists("records.csv") and os.path.getsize("records.csv") > 0
    with open("records.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["username", "name", "direction", "amount", "mode", "note", "date", "imp"],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(records)


def write_records(records: list) -> None:
    with open("records.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["username", "name", "direction", "amount", "mode", "note", "date", "imp"],
        )
        writer.writeheader()
        writer.writerows(records)


def detail_output_date(date_, form: int) -> str:
    if "/" in date_:
        day, month, year = date_.split("/")
    elif "-" in date_:
        day, month, year = date_.split("-")
    else:
        return date_
    if form in [0, 1]:
        month_str = output_month(int(month), form)
        return f"{day} {month_str}, {year}"
    elif form == 2:
        return f"{day}-{month}-{year}"
    elif form == 3:
        return f"{day}/{month}/{year}"
    return f"{day}/{month}/{year}"


def length_list(record_dict, rows, head=False):
    d_length, n_length, t_length, a_length, m_length, r_length, i_length, s_length = 4, 4, 9, 6, 4, 4, 1, 5
    for record in record_dict:
        d_length = max(d_length, len(record.get("date", "")))
        n_length = max(n_length, len(record.get("name", "")))
        a_length = max(a_length, len(record.get("amount", "")))
        m_length = max(m_length, len(record.get("mode", "")))
        r_length = max(r_length, len(record.get("note", "")))
        s_length = max(s_length, len(record.get("s.no.", "")))
    measurement_dict = {}
    length = 0
    if head:
        if "date" == head:
            length = max(d_length, length)
        elif "name" == head:
            length = max(n_length, length)
        elif "direction" == head:
            length = max(t_length, length)
        elif "amount" == head:
            length = max(a_length, length)
        elif "mode" == head:
            length = max(m_length, length)
        elif "note" == head:
            length = max(r_length, length)
        elif "imp" == head:
            length = max(i_length, length)
        elif "s.no." == head:
            length = max(s_length, length)
        else:
            length = max(len(head), length)
    if "date" not in rows:
        d_length = 0
    if "name" not in rows:
        n_length = 0
    if "direction" not in rows:
        t_length = 0
    if "amount" not in rows:
        a_length = 0
    if "mode" not in rows:
        m_length = 0
    if "note" not in rows:
        r_length = 0
    if "imp" not in rows:
        i_length = 0
    if "s.no." not in rows:
        s_length = 0
    gap = int((length - (d_length + n_length + t_length + a_length + m_length + r_length + i_length + s_length)) / (len(rows) + 1))
    if gap < 4:
        gap = 4
    length = max(d_length + n_length + t_length + a_length + m_length + r_length + i_length + s_length + ((len(rows) + 1) * gap), length)
    measurement_dict.update({
        "length": length, "gap": gap, "date": d_length, "name": n_length,
        "direction": t_length, "amount": a_length, "mode": m_length,
        "note": r_length, "imp": i_length, "s.no.": s_length
    })
    return measurement_dict


def print_list(measurement, records_dict, rows, head=None):
    prev_head = ""
    prev_heading = 0
    print("╭" + "─" * measurement["length"] + "┐")
    for record in records_dict:
        if head in ["date", "name", "direction", "mode", "note", "imp", "amount"]:
            if record.get(head):
                if record[head] != prev_head:
                    print("│" + f"{record[head]}".center(measurement["length"]) + "│")
                    print("├" + "─" * measurement["length"] + "┤")
                    prev_head = record[head]
        else:
            if head and head != prev_head:
                print("│" + f"{head}".center(measurement["length"]) + "│")
                print("├" + "─" * measurement["length"] + "┤")
                prev_head = head
        if not prev_heading:
            print("│" + " " * measurement["gap"], end="")
            for row in rows:
                print(f"{row.upper()}".center(measurement[row]), end="")
                print(" " * measurement["gap"], end="")
            print("│")
            print("├" + "─" * measurement["length"] + "┤")
            prev_heading = 1
        print("│" + " " * measurement["gap"], end="")
        for row in rows:
            print(f"{record.get(row, '')}".ljust(measurement[row]), end="")
            print(" " * measurement["gap"], end="")
        print("│")
    print("└" + "─" * measurement["length"] + "╯")


def output_records_formet(records, form, repeat_name=True):
    if repeat_name:
        for i, record in enumerate(records):
            record["amount"] = output_amount(int(record["amount"]))
            record["date"] = output_date(record["date"], form)
            record.update({"s.no.": f"{i+1}."})
        return records
    else:
        output_records = []
        for record in sorted(records, key=lambda s: s["name"]):
            f_n = 0
            for output_record in output_records:
                if record["name"] in output_record["name"]:
                    f_n = 1
                    break
            if not f_n:
                output_records.append(record)
        for i, output_record in enumerate(output_records):
            output_record["amount"] = output_amount(int(output_record["amount"]))
            output_record["date"] = output_date(output_record["date"], form)
            output_record.update({"s.no.": f"{i+1}."})
        return output_records


def show_person_details(index, records):
    person = records[index]
    formatted_date = detail_output_date(person["date"], 0)
    length = 2 + max(
        len(f"  {person['imp']} {person['mode'].title()} {person['direction']}ed  "),
        len("  Name: ".ljust(10) + f"{person['name']}  "),
        len("  Amount: ".ljust(10) + f"{person['amount']}  "),
        len("  Note: ".ljust(10) + f"{person['note']}  "),
        len("  Date: ".ljust(10) + formatted_date),
    )
    print(("╭" + "─" * length + "┐").center(len_of_text))
    print((("│" + f"  {person['imp']} {person['mode'].title()} {person['direction']}ed  ".center(length)).ljust(length) + "│").center(len_of_text))
    print((("│" + "  Name: ".ljust(10) + f"{person['name']}  ").ljust(length) + " │").center(len_of_text))
    print((("│" + "  Amount: ".ljust(10) + f"{person['amount']}  ").ljust(length) + " │").center(len_of_text))
    note_val = person["note"] if person["note"] else "N/A"
    print((("│" + "  Note: ".ljust(10) + f"{note_val}  ").ljust(length) + " │").center(len_of_text))
    print((("│" + "  Date: ".ljust(10) + formatted_date).ljust(length) + " │").center(len_of_text))
    print(("└" + "─" * length + "╯").center(len_of_text))


def print_empty_history():
    print(("╭" + "─" * 39 + "┐").center(len_of_text))
    print((("│" + " ⚠️ Empty Record History ".center(39)) + "│").center(len_of_text))
    print(("└" + "─" * 39 + "╯").center(len_of_text))
    print("Type:")
    print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
    while True:
        select = input(": ").lower().strip()
        if select in ['1', 'b', 'back']:
            print("─" * (len_of_text + 2))
            return
        elif select in ['2', 'e', 'exit']:
            print("─" * (len_of_text + 2))
            exit_()
        else:
            print("╭" + "─" * 19 + "┐")
            print("│" + " ⚠️ Invalid Input!" + " │")
            print("└" + "─" * 19 + "╯")


def print_empty_search():
    print(("╭" + "─" * 39 + "┐").center(len_of_text))
    print((("│" + " ⚠️ No Data to Search ".center(39)) + "│").center(len_of_text))
    print(("└" + "─" * 39 + "╯").center(len_of_text))
    print("Type:")
    print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
    while True:
        select = input(": ").lower().strip()
        if select in ['1', 'b', 'back']:
            print("─" * (len_of_text + 2))
            return
        elif select in ['2', 'e', 'exit']:
            print("─" * (len_of_text + 2))
            exit_()
        else:
            print("╭" + "─" * 19 + "┐")
            print("│" + " ⚠️ Invalid Input!" + " │")
            print("└" + "─" * 19 + "╯")


def print_empty_imp():
    print(("╭" + "─" * 55 + "┐").center(len_of_text))
    print((("│" + " ⚠️ No Important Record ".center(55)) + "│").center(len_of_text))
    print((("│" + " Press 'p' or 'profile' for return to Profile. ".center(55)) + "│").center(len_of_text))
    print(("└" + "─" * 55 + "╯").center(len_of_text))
    print("Type:")
    print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
    while True:
        select = input(": ").lower().strip()
        if select in ['p', 'profile']:
            print("─" * (len_of_text + 2))
            return "profile"
        if select in ['1', 'b', 'back']:
            print("─" * (len_of_text + 2))
            return "back"
        elif select in ['2', 'e', 'exit']:
            print("─" * (len_of_text + 2))
            exit_()
        else:
            print("╭" + "─" * 19 + "┐")
            print("│" + " ⚠️ Invalid Input!" + " │")
            print("└" + "─" * 19 + "╯")


def print_empty_manage():
    print(("╭" + "─" * 55 + "┐").center(len_of_text))
    print((("│" + " ⚠️ No Record to Manage ".center(55)) + "│").center(len_of_text))
    print((("│" + " Press 'p' or 'profile' for return to Profile. ".center(55)) + "│").center(len_of_text))
    print(("└" + "─" * 55 + "╯").center(len_of_text))
    print("Type:")
    print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
    while True:
        select = input(": ").lower().strip()
        if select in ['p', 'profile']:
            print("─" * (len_of_text + 2))
            return "profile"
        if select in ['1', 'b', 'back']:
            print("─" * (len_of_text + 2))
            return "back"
        elif select in ['2', 'e', 'exit']:
            print("─" * (len_of_text + 2))
            exit_()
        else:
            print("╭" + "─" * 19 + "┐")
            print("│" + " ⚠️ Invalid Input!" + " │")
            print("└" + "─" * 19 + "╯")


def print_empty_stats():
    print(("╭" + "─" * 55 + "┐").center(len_of_text))
    print((("│" + " ⚠️ No Record Stats ".center(55)) + "│").center(len_of_text))
    print((("│" + " Press 'p' or 'profile' for return to Profile. ".center(55)) + "│").center(len_of_text))
    print(("└" + "─" * 55 + "╯").center(len_of_text))
    print("Type:")
    print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
    while True:
        select = input(": ").lower().strip()
        if select in ['p', 'profile']:
            print("─" * (len_of_text + 2))
            return "profile"
        if select in ['1', 'b', 'back']:
            print("─" * (len_of_text + 2))
            return "back"
        elif select in ['2', 'e', 'exit']:
            print("─" * (len_of_text + 2))
            exit_()
        else:
            print("╭" + "─" * 19 + "┐")
            print("│" + " ⚠️ Invalid Input!" + " │")
            print("└" + "─" * 19 + "╯")


def exit_() -> None:
    print("╭" + "─" * len_of_text + "┐")
    print("│" + "Thank you for using LedgerMate. See you next time!".center(len_of_text) + "│")
    print("└" + "─" * len_of_text + "╯")
    sys.exit()


# ---------------------------------------------------------
# APPLICATION FLOW & MENUS
# ---------------------------------------------------------

def main() -> None:
    print("╔" + "═" * len_of_text + "╗")
    print("║" + "LEDGERMATE - MULTI USER SYSTEM".center(len_of_text) + "║")
    print("╚" + "═" * len_of_text + "╝")
    gap: int = int((len_of_text - (len("│ 1. Sign Up  │" + "│ 2. Sign In  │" + "│ 3. Learn More │"))) / 4)
    error = 1
    while True:
        print()
        while True:
            print(" " * gap + "╭" + "─" * 13 + "┐" + " " * gap + "╭" + "─" * 13 + "┐" + " " * gap + "╭" + "─" * 15 + "┐" + " " * gap)
            print(" " * gap + "│ 1. Sign Up  │" + " " * gap + "│ 2. Sign In  │" + " " * gap + "│ 3. Learn More │" + " " * gap)
            print(" " * gap + "└" + "─" * 13 + "╯" + " " * gap + "└" + "─" * 13 + "╯" + " " * gap + "└" + "─" * 15 + "╯" + " " * gap)
            print("\nType:\n     exit - quit program")
            option: str = input("Choose option: ").lower().strip()
            if error and option in ['h', "help"]:
                print("╭" + "─" * (int(len_of_text / 2) - 3) + " HELP " + "─" * (int(len_of_text / 2) - 2) + "┐")
                print(("│ 1. " + "Sign Up".ljust(10) + "- type '1' or 'up' or 'sign up'").ljust(len_of_text) + " │")
                print(("│ 2. " + "Sign in".ljust(10) + "- type '2' or 'in' or 'sign in' or 'log in'").ljust(len_of_text) + " │")
                print(("│ 3. " + "Learn more".ljust(10) + "- type '3' or 'l' or 'learn more' or 'learn'").ljust(len_of_text) + " │")
                print(("│ 4. " + "Exit".ljust(10) + "- type 'e'  or 'exit'").ljust(len_of_text) + " │")
                print(("│    Input is Case-insensitive").ljust(len_of_text) + " │")
                print("└" + "─" * len_of_text + "╯")
                error = 0
            else:
                break
        try:
            if option not in ['1', '2', '3', "up", "in", 'l', "e", "sign up", "sign in", "log in", "learn more", "learn", "exit"]:
                raise ValueError()
            if option in ['1', "up", "sign up"]:
                print("─" * (len_of_text + 2))
                sign_up()
            elif option in ['2', "in", "sign in", "log in"]:
                print("─" * (len_of_text + 2))
                sign_in()
            elif option in ['3', 'l', "learn more", "learn"]:
                learn_more()
            else:
                print("─" * (len_of_text + 2))
                exit_()
        except ValueError:
            error = 1
            print("╭" + "─" * len_of_text + "┐")
            print("│" + "⚠️ That doesn't look right.".center(len_of_text) + "│")
            print("│" + "Please try again, or type 'help' or 'h' for assistance.".center(len_of_text) + "│")
            print("└" + "─" * len_of_text + "╯")


def learn_more():
    print("─" * (int(len_of_text / 2) - 5) + " LEARN MORE " + "─" * (int(len_of_text / 2) - 4))
    print()
    print(("╭" + "─" * 67 + "┐").center(len_of_text))
    print(("│" + "ABOUT LEDGER MATE".center(67) + "│").center(len_of_text))
    print(("├" + "─" * 67 + "┤").center(len_of_text))
    print(("│" + "".ljust(67) + "│").center(len_of_text))
    print(("│" + " LedgerMate is a personal finance tracking application designed".ljust(67) + "│").center(len_of_text))
    print(("│" + " to help you manage informal money transactions with friends and".ljust(67) + "│").center(len_of_text))
    print(("│" + " acquaintances.".ljust(67) + "│").center(len_of_text))
    print(("│" + "".ljust(67) + "│").center(len_of_text))
    print(("│" + " WHAT IT DOES".ljust(67) + "│").center(len_of_text))
    print(("├" + "─" * 67 + "┤").center(len_of_text))
    print(("│" + "   • Records every transaction you lend or borrow, along with".ljust(67) + "│").center(len_of_text))
    print(("│" + "     the date, amount, and mode of payment.".ljust(67) + "│").center(len_of_text))
    print(("│" + "   • Maintains a complete transaction history for each person,".ljust(67) + "│").center(len_of_text))
    print(("│" + "     accessible anytime.".ljust(67) + "│").center(len_of_text))
    print(("│" + "   • Calculates and displays a clear balance summary — showing".ljust(67) + "│").center(len_of_text))
    print(("│" + "     exactly who owes whom, and how much.".ljust(67) + "│").center(len_of_text))
    print(("│" + "   • Supports multiple users, each with a private, secure account.".ljust(67) + "│").center(len_of_text))
    print(("│" + "".ljust(67) + "│").center(len_of_text))
    print(("│" + " WHY USE IT".ljust(67) + "│").center(len_of_text))
    print(("├" + "─" * 67 + "┤").center(len_of_text))
    print(("│" + "   • Eliminates the need to remember or manually track informal".ljust(67) + "│").center(len_of_text))
    print(("│" + "     loans between friends.".ljust(67) + "│").center(len_of_text))
    print(("│" + "   • Provides a searchable, organized record of all past".ljust(67) + "│").center(len_of_text))
    print(("│" + "     transactions.".ljust(67) + "│").center(len_of_text))
    print(("│" + "   • Helps avoid misunderstandings by keeping accurate, ".ljust(67) + "│").center(len_of_text))
    print(("│" + "     time-stamped records.".ljust(67) + "│").center(len_of_text))
    print(("│" + "".ljust(67) + "│").center(len_of_text))
    print(("│" + " PRIVACY & SECURITY".ljust(67) + "│").center(len_of_text))
    print(("├" + "─" * 67 + "┤").center(len_of_text))
    print(("│" + "   • Your account is protected with a password.".ljust(67) + "│").center(len_of_text))
    print(("│" + "   • Passwords are securely stored and never saved in plain text.".ljust(67) + "│").center(len_of_text))
    print(("│" + "   • Each user's data is private and accessible only to them.".ljust(67) + "│").center(len_of_text))
    print(("│" + "".ljust(67) + "│").center(len_of_text))
    print(("└" + "─" * 67 + "╯").center(len_of_text))
    input("\n Press Enter to return to the previous page.")
    print("─" * (len_of_text + 2))
    print()
    return


def sign_up() -> None:
    print("─" * (int(len_of_text / 2) - 3) + " SIGN UP " + "─" * (int(len_of_text / 2) - 3))
    while True:
        while True:
            username: str = input("Enter username: ").lower().strip()
            matches1: bool = re.search(r"^[a-z]\w*$", username, re.I)
            user_found = False
            if os.path.exists("users.csv") and os.path.getsize("users.csv") != 0:
                users: list = read_users()
                for _ in users:
                    if _["username"] == username:
                        user_found = _
                        break
            try:
                if not matches1:
                    raise ValueError()
                if os.path.exists("users.csv") and os.path.getsize("users.csv") != 0:
                    if user_found:
                        raise NameError()
                break
            except ValueError:
                print("╭" + "─" * len_of_text + "┐")
                print("│" + "⚠️ Invalid Username!".center(len_of_text) + "│")
                print("│" + "  Username must start with a letter".ljust(len_of_text) + "│")
                print("│" + "  Username contain only letters, numbers, and _ Underscores".ljust(len_of_text) + "│")
                print("│" + "  Not allowed: special characters, and spaces".ljust(len_of_text) + "│")
                print("└" + "─" * len_of_text + "╯")
            except NameError:
                print("╭" + "─" * len_of_text + "┐")
                print("│" + "⚠️ Username already exists. Try something unique.".center(len_of_text) + "│")
                print("└" + "─" * len_of_text + "╯")
        while True:
            while True:
                created_password: str = pwinput("Create password: ")
                pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<> ]{8,}$'
                matches2 = re.search(pattern, created_password)
                try:
                    if not matches2:
                        raise ValueError()
                    break
                except ValueError:
                    print("╭" + "─" * len_of_text + "┐")
                    print("│" + "⚠️ Weak password!".center(len_of_text) + "│")
                    print("│" + " Needs 8+ characters, and".ljust(len_of_text) + "│")
                    print("│" + " Need at least a letter, a number, and a special character.".ljust(len_of_text) + "│")
                    print("└" + "─" * len_of_text + "╯")
            confirm_password: str = pwinput("Confirm password: ")
            try:
                if created_password != confirm_password:
                    raise ValueError()
                break
            except ValueError:
                print("╭" + "─" * len_of_text + "┐")
                print("│" + "⚠️ Passwords don't match. Please re-enter your password.".center(len_of_text) + "│")
                print("└" + "─" * len_of_text + "╯")
        if len(" username: " + username) > len(" password: " + created_password + "   (hidden)"):
            length: int = len(" username: " + username) + 2
        else:
            length: int = len(" password: " + created_password + "   (hidden)") + 2
        print()
        print(("╭" + "─" * length + "┐").center(len_of_text))
        print((("│" + "REVIEW".center(length)).ljust(length) + "│").center(len_of_text))
        print((("│" + " Username: " + username).ljust(length) + " │").center(len_of_text))
        print((("│" + " Password: " + "*" * len(created_password) + "   (hidden)").ljust(length) + " │").center(len_of_text))
        print(("└" + "─" * length + "╯").center(len_of_text))
        print()
        while True:
            confirm_sign_up: str = input("Confirm Sign Up? (yes/no): ").lower().strip()
            try:
                if confirm_sign_up not in ['1', '2', 'y', 'n', "yes", "no"]:
                    raise ValueError()
                break
            except ValueError:
                print("╭" + "─" * 19 + "┐")
                print("│" + " ⚠️ Invalid input!" + " │")
                print("└" + "─" * 19 + "╯")
        if confirm_sign_up in ['1', 'y', "yes"]:
            password = hashlib.sha256(created_password.encode()).hexdigest()
            users = read_users()
            user = {
                "username": username,
                "password": password,
                "datetime": datetime.now().isoformat(),
                "failed_attempts": "0",
                "lockout_time": "",
            }
            users.append(user)
            write_users(users)
            print(("╭" + "─" * 34 + "┐").center(len_of_text))
            print(("│" + "✅ Account created successfully!".center(33) + "│").center(len_of_text))
            print(("│" + "Redirecting to Home...".center(34) + "│").center(len_of_text))
            print(("└" + "─" * 34 + "╯").center(len_of_text))
            print("─" * (len_of_text + 2))
            select = home(username, users, user)
            if select == "back to main":
                return
        else:
            print(("╭" + "─" * 24 + "┐").center(len_of_text))
            print(("│" + "Sign Up cancelled.".center(24) + "│").center(len_of_text))
            print(("└" + "─" * 24 + "╯").center(len_of_text))
            print("─" * (len_of_text + 2))
        break


def sign_in():
    print("─" * (int(len_of_text / 2) - 3) + " SIGN IN " + "─" * (int(len_of_text / 2) - 3))
    while True:
        error = 0
        while True:
            username: str = input("Username: ").lower().strip()
            user = False
            users: list = read_users()
            for _ in users:
                if _["username"] == username:
                    user = _
                    break
            try:
                if not user:
                    raise ValueError()
                elif user["lockout_time"]:
                    elapsed = time.time() - float(user["lockout_time"])
                    if elapsed < 30:
                        remaining = int(30 - elapsed)
                        print("╭" + "─" * len_of_text + "┐")
                        print("│" + (f"🔒 Account locked. Try again in {remaining} seconds.").center(len_of_text - 1) + "│")
                        print("└" + "─" * len_of_text + "╯")
                        print("─" * (len_of_text + 2))
                        return
                    else:
                        user["lockout_time"] = ""
                        user["failed_attempts"] = "0"
                break
            except ValueError:
                if error:
                    print("╭" + "─" * 24 + "┐")
                    print("│" + " ⚠️ Username not found." + " │")
                    print("└" + "─" * 24 + "╯")
                else:
                    error = 1
                    print("╭" + "─" * 31 + "┐")
                    print("│" + "⚠️ Username not found!".center(31) + "│")
                    print("│" + " New user? Would you like to:".ljust(30) + " │")
                    print("│" + "  1. Try again".ljust(30) + " │")
                    print("│" + "  2. Sign up for a new account".ljust(30) + " │")
                    print("└" + "─" * 31 + "╯")
                    while True:
                        choice = input("Select: ").lower().strip()
                        try:
                            if choice not in ['1', '2', "try", "sign up", "up", 's', 't', "try again"]:
                                raise ValueError()
                            break
                        except ValueError:
                            print("╭" + "─" * 31 + "┐")
                            print("│" + " ⚠️ Invalid Choice. Try Again." + " │")
                            print("└" + "─" * 31 + "╯")
                    if choice in ['2', 's', "up", "sign up"]:
                        print("─" * (len_of_text + 2))
                        return sign_up()
        while True:
            password: str = hashlib.sha256(pwinput("Password: ").encode()).hexdigest()
            try:
                if user["password"] != password:
                    attempts = int(user['failed_attempts']) + 1
                    user['failed_attempts'] = str(attempts)
                    if attempts >= 5:
                        user["lockout_time"] = str(time.time())
                        raise NameError()
                    raise ValueError()
                user['failed_attempts'] = '0'
                user['lockout_time'] = ''
                write_users(users)
                break
            except ValueError:
                print("╭" + "─" * 42 + "┐")
                print("│" + " ⚠️ Incorrect password. Please try again." + " │")
                print("└" + "─" * 42 + "╯")
                write_users(users)
            except NameError:
                print("╭" + "─" * len_of_text + "┐")
                print("│" + "🔒 Too many failed attempts. Account locked for 30 seconds.".center(len_of_text - 1) + "│")
                print("└" + "─" * len_of_text + "╯")
                write_users(users)
                return
        length = len("Username: " + username) + 4
        print()
        print(("╭" + "─" * length + "┐").center(len_of_text))
        print(("│  " + "Username: " + username + "  │").center(len_of_text))
        print(("└" + "─" * length + "╯").center(len_of_text))
        print()
        while True:
            confirm_sign_in: str = input("Confirm Sign In? (yes/no): ").lower().strip()
            try:
                if confirm_sign_in not in ['1', '2', 'y', 'n', "yes", "no"]:
                    raise ValueError()
                break
            except ValueError:
                print("╭" + "─" * 19 + "┐")
                print("│" + " ⚠️ Invalid input!" + " │")
                print("└" + "─" * 19 + "╯")
        if confirm_sign_in in ['1', 'y', "yes"]:
            print(("╭" + "─" * 28 + "┐").center(len_of_text))
            print(("│" + "✅ Signed in successfully!".center(27) + "│").center(len_of_text))
            print(("│" + "Redirecting to Home...".center(28) + "│").center(len_of_text))
            print(("└" + "─" * 28 + "╯").center(len_of_text))
            print("─" * (len_of_text + 2))
            select = home(username, users, user)
            if select == "back to main":
                return
        else:
            print(("╭" + "─" * 24 + "┐").center(len_of_text))
            print(("│" + "Sign In cancelled.".center(24) + "│").center(len_of_text))
            print(("└" + "─" * 24 + "╯").center(len_of_text))
            print("─" * (len_of_text + 2))
        break


def print_main_menu():
    print("─" * (int(len_of_text / 2) - 2) + " HOME " + "─" * (int(len_of_text / 2) - 1))
    print()
    length: int = len(" 2. " + "History".ljust(10) + "- View all transactions ") + 2
    print(("╭" + "─" * length + "┐").center(len_of_text))
    print((("│" + "MAIN MENU".center(length)).ljust(length) + "│").center(len_of_text))
    print((("│ 1. " + "Record".ljust(10) + "- Add a new transaction").ljust(length) + " │").center(len_of_text))
    print((("│ 2. " + "History".ljust(10) + "- View all transactions").ljust(length) + " │").center(len_of_text))
    print((("│ 3. " + "Details".ljust(10) + "- View person's record").ljust(length) + " │").center(len_of_text))
    print((("│ 4. " + "Search".ljust(10) + "- Find transactions").ljust(length) + " │").center(len_of_text))
    print((("│ 5. " + "Profile".ljust(10) + "- Your account").ljust(length) + " │").center(len_of_text))
    print((("│ 6. " + "Exit".ljust(10) + "- Close the program").ljust(length) + " │").center(len_of_text))
    print(("└" + "─" * length + "╯").center(len_of_text))
    return


def home(username, users, user) -> None:
    print("╔" + "═" * len_of_text + "╗")
    print("║" + "WELCOME TO LEDGERMATE".center(len_of_text) + "║")
    print("║" + "Track what you owe & what's owed".center(len_of_text) + "║")
    print("╚" + "═" * len_of_text + "╝")
    print("─" * (len_of_text + 2))
    print_main_menu()
    error = 1
    while True:
        print()
        while True:
            choice: str = input("Enter your choice: ").lower().strip()
            if error and choice == "help":
                length = 45
                print((("╭" + ("─" * (int(length / 2) - 3) + " HELP " + "─" * (int(length / 2) - 2)).center(length)).ljust(length) + "┐").center(len_of_text + 3))
                print((("│ 1. " + "Record".ljust(10) + "- type '1' or 'r' or 'record'").ljust(length) + " │").center(len_of_text + 3))
                print((("│ 2. " + "History".ljust(10) + "- type '2' or 'h' or 'history'").ljust(length) + " │").center(len_of_text + 3))
                print((("│ 3. " + "Details".ljust(10) + "- type '3' or 'd' or 'details'").ljust(length) + " │").center(len_of_text + 3))
                print((("│ 4. " + "Search".ljust(10) + "- type '4' or 's' or 'search'").ljust(length) + " │").center(len_of_text + 3))
                print((("│ 5. " + "Profile".ljust(10) + "- type '5' or 'p' or 'profile'").ljust(length) + " │").center(len_of_text + 3))
                print((("│ 6. " + "Exit".ljust(10) + "- type '6' or 'e' or 'exit'").ljust(length) + " │").center(len_of_text + 3))
                print((("│    Input is Case-insensitive").ljust(length) + " │").center(len_of_text + 3))
                print(("└" + "─" * length + "╯").center(len_of_text + 3))
                error = 0
            else:
                break
        try:
            if choice not in ['1', '2', '3', '4', '5', '6', "r", "h", "d", "s", "p", "e", "record", "history", "details", "search", "profile", "exit"]:
                raise ValueError()
            if choice in ['1', 'r', 'record']:
                print("─" * (len_of_text + 2))
                record(username)
                print_main_menu()
                error = 1
            elif choice in ['2', 'h', 'history']:
                print("─" * (len_of_text + 2))
                history(username)
                print_main_menu()
                error = 1
            elif choice in ['3', 'd', 'details']:
                print("─" * (len_of_text + 2))
                details(username)
                print_main_menu()
                error = 1
            elif choice in ['4', 's', 'search']:
                print("─" * (len_of_text + 2))
                search(username)
                print_main_menu()
                error = 1
            elif choice in ['5', 'p', 'profile']:
                print("─" * (len_of_text + 2))
                select = profile(username, users, user)
                if select == "back to main":
                    return "back to main"
                print_main_menu()
                error = 1
            elif choice in ['6', 'e', 'exit']:
                print("─" * (len_of_text + 2))
                exit_()
        except ValueError:
            error = 1
            print("╭" + "─" * len_of_text + "┐")
            print("│" + "⚠️ Invalid choice.".center(len_of_text) + "│")
            print("│" + "Please try again, or type 'help' for assistance.".center(len_of_text) + "│")
            print("└" + "─" * len_of_text + "╯")


def record(username) -> None:
    while True:
        print("─" * (int(len_of_text / 2) - 8) + " NEW RECORD ENTRY " + "─" * (int(len_of_text / 2) - 7))
        print()
        while True:
            gap: int = int((len_of_text - 25) / 3)
            print(" " * gap + "╭" + "─" * 12 + "┐" + " " * gap + "╭" + "─" * 11 + "┐" + " " * gap)
            print(" " * gap + "│ 1. CREDIT  │" + " " * gap + "│ 2. DEBIT  │" + " " * gap)
            print(" " * gap + "└" + "─" * 12 + "╯" + " " * gap + "└" + "─" * 11 + "╯" + " " * gap)
            print("Type:")
            print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program\n")
            while True:
                entry_type: str = input("Select entry type: ").lower().strip()
                try:
                    if entry_type not in ['1', '2', 'c', 'd', 'b', 'e', 'credit', 'debit', 'back', 'exit']:
                        raise ValueError()
                    break
                except ValueError:
                    print("╭" + "─" * len_of_text + "┐")
                    print("│" + "⚠️ Invalid entry type.".center(len_of_text) + "│")
                    print("│" + "Enter '1' or 'c' or 'credit' for Credit.".center(len_of_text) + "│")
                    print("│" + "Enter '2' or 'd' or 'debit' for Debit.".center(len_of_text) + "│")
                    print("└" + "─" * len_of_text + "╯")
            if entry_type in ['1', 'c', 'credit']:
                entry_type = 'Credit'
            elif entry_type in ['2', 'd', 'debit']:
                entry_type = 'Debit'
            elif entry_type in ['b', 'back']:
                return
            elif entry_type in ['e', 'exit']:
                exit_()
            break
        print()
        persons = read_records(username)
        if len(persons):
            while True:
                is_new_person = input("Transaction with NEW Person? (yes/no): ").strip().lower()
                if is_new_person not in ['y', 'n', 'yes', 'no']:
                    print()
                    print("╭" + "─" * 19 + "┐")
                    print("│" + " ⚠️ Invalid input!" + " │")
                    print("└" + "─" * 19 + "╯")
                else:
                    break
        else:
            is_new_person = 'yes'

        if is_new_person in ['y', 'yes']:
            while True:
                person_name: str = input("Person's name: ").title().strip()
                matches = re.search(r'^([a-z][a-z0-9]* *)+$', person_name, re.I)
                try:
                    if not matches:
                        raise ValueError()
                    person_name = " ".join(person_name.split())
                    person_found = 0
                    for person in persons:
                        if person["name"] == person_name:
                            person_found = 1
                            break
                    if person_found:
                        raise NameError()
                    break
                except ValueError:
                    print()
                    print("╭" + "─" * 50 + "┐")
                    print("│" + "⚠️ Invalid name!".center(50) + "│")
                    print("│" + " Use only letters, numbers, and spaces.".ljust(49) + " │")
                    print("│" + " Each part of the name must start with a letter.".ljust(49) + " │")
                    print("└" + "─" * 50 + "╯")
                    print()
                except NameError:
                    print()
                    print("╭" + "─" * 50 + "┐")
                    print("│" + "⚠️ Person already exists. Try something unique.".center(50) + "│")
                    print("└" + "─" * 50 + "╯")
                    print()
        else:
            list_appears = 0
            search_appears = 0
            result_list = []
            while True:
                person_name = input("Person's name: ").title().strip()
                if list_appears or search_appears:
                    try:
                        p_f = 0
                        idx = int(person_name)
                        for i, person in enumerate(result_list):
                            if idx == i + 1:
                                p_f = 1
                                person_name = person
                                break
                        if p_f:
                            print()
                            l = len("Person Name: " + person_name) + 4
                            print("╭" + "─" * l + "┐")
                            print("│" + " Person's Name: " + person_name + " │")
                            print("└" + "─" * l + "╯")
                            print()
                            break
                    except ValueError:
                        pass
                person_found = 0
                for person in persons:
                    if person["name"] == person_name:
                        person_found = 1
                        break
                if not person_found:
                    print()
                    print("╭" + "─" * 40 + "┐")
                    print("│" + "⚠️ Person not found. ".center(40) + "│")
                    print("│" + " Type 'l' or 'list' to see all persons. ".center(40) + "│")
                    print("│" + " Type 's' or 'search' to search person. ".center(40) + "│")
                    print("│" + " Press Enter to retry.".ljust(40) + "│")
                    print("└" + "─" * 40 + "╯")
                    print()
                    selection = input(": ").lower().strip()
                    if selection in ['l', 'list']:
                        result_list = []
                        for person in sorted(persons, key=lambda s: s["name"]):
                            if person["name"] not in result_list:
                                result_list.append(person["name"])
                        length = len("PERSON'S LIST")
                        for person in result_list:
                            if length < len(person):
                                length = len(person)
                        length += 6
                        print()
                        print(("╭" + "─" * length + "┐").ljust(len_of_text))
                        print((("│" + "PERSON'S LIST".center(length)).ljust(length) + "│").ljust(len_of_text))
                        for i, person in enumerate(result_list):
                            print((("│" + f" {i+1}. {person}").ljust(length) + " │").ljust(len_of_text))
                        print(("└" + "─" * length + "╯").ljust(len_of_text))
                        print(" Enter S.No. or full name from list.")
                        print()
                        list_appears = 1
                        search_appears = 0
                    elif selection in ['s', 'search']:
                        keyword = input("Search Keyword: ").strip().lower()
                        result_list = []
                        for person in sorted(persons, key=lambda s: s["name"]):
                            if re.search(rf'\b{re.escape(keyword)}', person["name"], re.I) and person["name"] not in result_list:
                                result_list.append(person["name"])
                        if len(result_list):
                            length = len(f"SEARCH RESULT FOR {keyword}")
                            for person in result_list:
                                if length < len(person):
                                    length = len(person)
                            length += 6
                            print()
                            print(("╭" + "─" * length + "┐").ljust(len_of_text))
                            print((("│" + f"Search Result for '{keyword}'".center(length)).ljust(length) + "│").ljust(len_of_text))
                            for i, person in enumerate(result_list):
                                print((("│" + f" {i+1}. {person}").ljust(length) + " │").ljust(len_of_text))
                            print(("└" + "─" * length + "╯").ljust(len_of_text))
                            print(" Enter S.No. or full name from list.")
                            print()
                            search_appears = 1
                            list_appears = 0
                        else:
                            length = len(f" No match found for '{keyword}'") + 1
                            print()
                            print("╭" + "─" * length + "┐")
                            print("│" + f" No match found for '{keyword}'" + " │")
                            print("└" + "─" * length + "╯")
                            print()
                            search_appears = 0
                            list_appears = 0
                else:
                    break

        while True:
            try:
                amount_input: str = input("Amount: Rs. ").strip()
                if not re.match(r"^(?:[1-9]\d{0,2}(?:,\d{3})+|[1-9]\d{0,1}(?:,\d{2})*,\d{3}|[1-9]\d*|0*)$", amount_input):
                    raise TypeError()
                amount_val: int = int(amount_input.replace(',', ''))
                if amount_val == 0:
                    raise ValueError()
                break
            except TypeError:
                print()
                print("╭" + "─" * 34 + "┐")
                print("│" + " ⚠️ Not a valid amount. Try again" + " │")
                print("└" + "─" * 34 + "╯")
            except ValueError:
                print()
                print("╭" + "─" * 26 + "┐")
                print("│" + " ⚠️ Amount can't be Zero." + " │")
                print("└" + "─" * 26 + "╯")

        while True:
            mode_input: str = input("Mode (online/cash): ").strip().lower()
            try:
                if mode_input in ['1', 'o', "online"]:
                    mode = "Online"
                elif mode_input in ['2', 'c', "cash"]:
                    mode = "Cash"
                else:
                    raise ValueError()
                break
            except ValueError:
                print()
                print("╭" + "─" * 48 + "┐")
                print("│" + "⚠️ Invalid Mode! ".center(48) + "│")
                print("│" + " Type '1' or 'o' or 'online' for Online mode. ".center(48) + "│")
                print("│" + " Type '2' or 'c' or 'cash' for Cash mode. ".center(48) + "│")
                print("└" + "─" * 48 + "╯")

        print("╭" + "─" * len_of_text + "┐")
        print("│" + "ADD A NOTE OR PRESS ENTER TO SKIP".center(len_of_text) + "│")
        print("└" + "─" * len_of_text + "╯")
        note: str = input("Note: ").strip().capitalize()

        while True:
            is_date_today: str = input("Is this today's transaction? (yes/no): ").strip().lower()
            try:
                if is_date_today not in ['y', 'yes', 'n', 'no']:
                    raise ValueError()
                break
            except ValueError:
                print()
                print("╭" + "─" * 19 + "┐")
                print("│" + " ⚠️ Invalid input!" + " │")
                print("└" + "─" * 19 + "╯")

        if is_date_today in ['y', 'yes']:
            date_ = str(date.today())
        else:
            print("╭" + "─" * 40 + "┐")
            print("│" + "📆 Date Formats".center(38) + " │")
            print("│" + "  DD-MM-YYYY".ljust(18) + "eg. 25-11-2025       " + " │")
            print("│" + "  DD/MM/YYYY".ljust(18) + "eg. 25/11/2025       " + " │")
            print("│" + "  DD Month YYYY".ljust(18) + "eg. 25 November 2025 " + " │")
            print("└" + "─" * 40 + "╯")
            months = [
                "january", "february", "march", "april", "may", "june",
                "july", "august", "september", "october", "november", "december",
                "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"
            ]
            months = sorted(months, key=len, reverse=True)
            months_pattern = "|".join(map(re.escape, months))
            while True:
                input_date = input("Date: ").lower().strip()
                try:
                    if matches := re.search(rf"^(?P<day>\d{{1,2}})(?P<sep>\s+|-|/)(?P<month>\d{{1,2}}|{months_pattern})(?P=sep)(?P<year>\d{{4}})$", input_date):
                        day = int(matches.group("day"))
                        month_val = matches.group("month")
                        if month_val in months:
                            month_dict = {
                                "january": 1, "jan": 1, "february": 2, "feb": 2,
                                "march": 3, "mar": 3, "april": 4, "apr": 4,
                                "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
                                "august": 8, "aug": 8, "september": 9, "sep": 9,
                                "october": 10, "oct": 10, "november": 11, "nov": 11,
                                "december": 12, "dec": 12
                            }
                            month_num = month_dict[month_val]
                        else:
                            month_num = int(month_val)
                        year_num = int(matches.group("year"))
                        parsed_date = date(year_num, month_num, day)
                        if parsed_date > date.today():
                            raise TypeError()
                        date_ = str(parsed_date)
                        break
                    raise NameError()
                except NameError:
                    print()
                    print("╭" + "─" * 60 + "┐")
                    print("│" + "⚠️ Format doesn't match! Please check how you typed it.".center(60) + "│")
                    print("└" + "─" * 60 + "╯")
                except ValueError:
                    print()
                    print("╭" + "─" * 45 + "┐")
                    print("│" + " ⚠️ That date doesn't exist on the calendar. ".center(45) + "│")
                    print("│" + " Please check the date and try again.".center(45) + "│")
                    print("└" + "─" * 45 + "╯")
                except TypeError:
                    print()
                    print("╭" + "─" * 34 + "┐")
                    print("│" + " ⚠️ Future dates are not allowed.".center(34) + "│")
                    print("│" + " Date must be on or before today. ".center(34) + "│")
                    print("└" + "─" * 34 + "╯")

        while True:
            is_imp = input("Mark transaction as important? (yes/no): ").strip().lower()
            try:
                if is_imp in ['y', 'yes']:
                    imp = '★'
                elif is_imp in ['n', 'no']:
                    imp = ''
                else:
                    raise ValueError()
                break
            except ValueError:
                print()
                print("╭" + "─" * 19 + "┐")
                print("│" + " ⚠️ Invalid input!" + " │")
                print("└" + "─" * 19 + "╯")

        length = 2 + max(
            len(f"  {imp} {mode.title()} {entry_type}ed  "),
            len("  Name: ".ljust(10) + f"{person_name}  "),
            len("  Amount: ".ljust(10) + f"{output_amount(amount_val)}  "),
            len("  Note: ".ljust(10) + f"{note}  "),
            len("  Date: ".ljust(10) + output_date(date_, 0)),
        )
        print()
        print(("╭" + "─" * length + "┐").center(len_of_text))
        print((("│" + f"  {imp} {mode.title()} {entry_type}ed  ".center(length)).ljust(length) + "│").center(len_of_text))
        print((("│" + "  Name: ".ljust(10) + f"{person_name}  ").ljust(length) + " │").center(len_of_text))
        print((("│" + "  Amount: ".ljust(10) + f"{output_amount(amount_val)}  ").ljust(length) + " │").center(len_of_text))
        if note:
            print((("│" + "  Note: ".ljust(10) + f"{note}  ").ljust(length) + " │").center(len_of_text))
        print((("│" + "  Date: ".ljust(10) + output_date(date_, 0)).ljust(length) + " │").center(len_of_text))
        print(("└" + "─" * length + "╯").center(len_of_text))
        print()

        while True:
            save = input(" Save this record? (yes/no): ").strip().lower()
            try:
                if save in ['y', 'yes']:
                    save_records = {
                        "username": username,
                        "name": person_name,
                        "direction": entry_type,
                        "amount": amount_val,
                        "mode": mode,
                        "note": note,
                        "date": date_,
                        "imp": imp,
                    }
                    append_records(save_records)
                    print(("╭" + "─" * 20 + "┐").center(len_of_text))
                    print(("│ " + " ✅ Record saved! " + " │").center(len_of_text))
                    print(("└" + "─" * 20 + "╯").center(len_of_text))
                elif save in ['n', 'no']:
                    print(("╭" + "─" * 22 + "┐").center(len_of_text))
                    print(("│ " + " ❌ Entry cancelled." + " │").center(len_of_text))
                    print(("└" + "─" * 22 + "╯").center(len_of_text))
                else:
                    raise ValueError()
                break
            except ValueError:
                print("╭" + "─" * 19 + "┐")
                print("│" + " ⚠️ Invalid input!" + " │")
                print("└" + "─" * 19 + "╯")

        print("─" * (len_of_text + 2))
        print("╭" + "─" * 31 + "┐")
        print("│" + " 1. Another Record Entry  ".ljust(30) + " │")
        print("│" + " 2. back - previous (home) ".ljust(30) + " │")
        print("│" + " 3. exit - quit program ".ljust(30) + " │")
        print("└" + "─" * 31 + "╯")
        while True:
            select_option = input("Select option: ").strip().lower()
            if select_option in ['1', 'another', 'record', 'entry', 'another record', 'record entry', 'another entry', 'another record entry']:
                break
            elif select_option in ['2', 'b', 'back']:
                return
            elif select_option in ['3', 'e', 'exit']:
                print("─" * (len_of_text + 2))
                exit_()
            else:
                print("╭" + "─" * 23 + "┐")
                print("│" + " ⚠️ Invalid Selection!" + " │")
                print("└" + "─" * 23 + "╯")


def history(username: str) -> None:
    print("─" * (int(len_of_text / 2) - 3) + " HISTORY " + "─" * (int(len_of_text / 2) - 3))
    user_history: list = read_records(username)
    if user_history:
        user_history = sorted_list_wrt_date(user_history)
        user_history = output_records_formet(user_history, 3)
        rows = ["s.no.", "date", "name", "direction", "amount"]
        head = "RECORD HISTORY"
        measurement = length_list(user_history, rows, head)
        print_list(measurement, user_history, rows, head)
        while True:
            print(("╭" + "─" * 45 + "┐").center(len_of_text))
            print((("│" + "Enter S.No. to view Record Details.".center(45)) + "│").center(len_of_text))
            print(("└" + "─" * 45 + "╯").center(len_of_text))
            print("Type:")
            print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
            select = input(": ").lower().strip()
            try:
                if select in ['b', 'back']:
                    print("─" * (len_of_text + 2))
                    return
                elif select in ['e', 'exit']:
                    print("─" * (len_of_text + 2))
                    exit_()
                elif 0 < int(select) <= len(user_history):
                    show_person_details(int(select) - 1, user_history)
                else:
                    raise ValueError
            except ValueError:
                print("╭" + "─" * 19 + "┐")
                print("│" + " ⚠️ Invalid Input!" + " │")
                print("└" + "─" * 19 + "╯")
    else:
        print_empty_history()


def details(username: str) -> None:
    while True:
        print("─" * (int(len_of_text / 2) - 3) + " DETAILS " + "─" * (int(len_of_text / 2) - 3))
        print()
        gap: int = int((len_of_text - 25) / 3)
        print(" " * gap + "╭" + "─" * 12 + "┐" + " " * gap + "╭" + "─" * 11 + "┐" + " " * gap)
        print(" " * gap + "│ 1. DETAIL  │" + " " * gap + "│ 2. TOTAL  │" + " " * gap)
        print(" " * gap + "└" + "─" * 12 + "╯" + " " * gap + "└" + "─" * 11 + "╯" + " " * gap)
        print("Type:")
        print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program\n")
        while True:
            choose: str = input("Select : ").lower().strip()
            try:
                if choose not in ['1', '2', 't', 'd', 'b', 'e', 'total', 'detail', 'back', 'exit']:
                    raise ValueError()
                break
            except ValueError:
                print("╭" + "─" * len_of_text + "┐")
                print("│" + "⚠️ Invalid Selection!".center(len_of_text) + "│")
                print("│" + "Enter '1' or 'd' or 'detail' for Detail.".center(len_of_text) + "│")
                print("│" + "Enter '2' or 't' or 'total' for Total.".center(len_of_text) + "│")
                print("└" + "─" * len_of_text + "╯")
        if choose in ['b', 'back']:
            print("─" * (len_of_text + 2))
            return
        elif choose in ['e', 'exit']:
            print("─" * (len_of_text + 2))
            exit_()
        elif choose in ['2', 't', 'total']:
            list_appears = 0
            try:
                persons = read_records(username)
                if not persons:
                    raise MemoryError()
                while True:
                    name = input("Person's Name: ").strip().title()
                    if list_appears:
                        try:
                            p_f = 0
                            idx = int(name)
                            for i, person in enumerate(result_list):
                                if idx == i + 1:
                                    p_f = 1
                                    name = person
                                    break
                            if p_f:
                                l = len("Person Name: " + name) + 4
                                print("╭" + "─" * l + "┐")
                                print("│" + " Person's Name: " + name + " │")
                                print("└" + "─" * l + "╯")
                                break
                        except ValueError:
                            pass
                    person_found = 0
                    for person in persons:
                        if person["name"] == name:
                            person_found = 1
                            break
                    if person_found:
                        break
                    length = max(17 + len(f"{name}"), 40)
                    print("╭" + "─" * length + "┐")
                    print("│" + f" ⚠️ {name} not found. ".center(length) + "│")
                    print("│" + " Type 'l' or 'list' to see all persons. ".ljust(length) + "│")
                    print("│" + " Type 's' or 'search' to search person. ".ljust(length) + "│")
                    print("│" + " Press Enter to retry.".ljust(length) + "│")
                    print("└" + "─" * length + "╯")
                    selection = input(": ").lower().strip()
                    if selection in ['l', 'list']:
                        result_list = []
                        for person in sorted(persons, key=lambda s: s["name"]):
                            if person["name"] not in result_list:
                                result_list.append(person["name"])
                        length = len("PERSON'S LIST")
                        for person in result_list:
                            if length < len(person):
                                length = len(person)
                        length += 6
                        print()
                        print(("╭" + "─" * length + "┐").ljust(len_of_text))
                        print((("│" + "PERSON'S LIST".center(length)).ljust(length) + "│").ljust(len_of_text))
                        for i, person in enumerate(result_list):
                            print((("│" + f" {i+1}. {person}").ljust(length) + " │").ljust(len_of_text))
                        print(("└" + "─" * length + "╯").ljust(len_of_text))
                        print(" Enter S.No. or full name from list.")
                        print()
                        list_appears = 1
                    elif selection in ['s', 'search']:
                        keyword = input("Search Keyword: ").strip().lower()
                        result_list = []
                        for person in sorted(persons, key=lambda s: s["name"]):
                            if re.search(rf'\b{re.escape(keyword)}', person["name"], re.I) and person["name"] not in result_list:
                                result_list.append(person["name"])
                        if len(result_list):
                            length = len(f"SEARCH RESULT FOR {keyword}")
                            for person in result_list:
                                if length < len(person):
                                    length = len(person)
                            length += 6
                            print()
                            print(("╭" + "─" * length + "┐").ljust(len_of_text))
                            print((("│" + f"Search Result for '{keyword}'".center(length)).ljust(length) + "│").ljust(len_of_text))
                            for i, person in enumerate(result_list):
                                print((("│" + f" {i+1}. {person}").ljust(length) + " │").ljust(len_of_text))
                            print(("└" + "─" * length + "╯").ljust(len_of_text))
                            print(" Enter S.No. or full name from list.")
                            print()
                            list_appears = 1
                        else:
                            length = len(f" No match found for '{keyword}'") + 1
                            print()
                            print("╭" + "─" * length + "┐")
                            print("│" + f" No match found for '{keyword}'" + " │")
                            print("└" + "─" * length + "╯")
                            print()
                            list_appears = 0

                print("╭" + "─" * 47 + "┐")
                print("│" + "📆 Date Formats".center(45) + " │")
                print("│" + "  DD/MM/YYYY".ljust(25) + "eg. 25/11/2025       " + " │")
                print("│" + "  DD Month YYYY".ljust(25) + "eg. 25 November 2025 " + " │")
                print("│" + "  specific date".ljust(25) + "eg. write in format " + "  │")
                print("│" + "  between two dates".ljust(25) + "eg1. date1 - date2 " + "   │")
                print("│" + "  between two dates".ljust(25) + "eg2. date1 to date2 " + "  │")
                print("│" + " Press Enter to skip. ".ljust(47) + "│")
                print("└" + "─" * 47 + "╯")

                months = [
                    "january", "february", "march", "april", "may", "june",
                    "july", "august", "september", "october", "november", "december",
                    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"
                ]
                months = sorted(months, key=len, reverse=True)
                months_pattern = "|".join(map(re.escape, months))
                single_date_pattern = rf"\d{{1,2}}(?:/(?:\d{{1,2}}|{months_pattern})/|\s+(?:\d{{1,2}}|{months_pattern})\s+)\d{{4}}"

                while True:
                    date_input = input("Date: ").strip().lower()
                    if date_input == "":
                        filter_for_date = 0
                        break
                    elif re.search(rf"^{single_date_pattern}(?:\s*(?:-|to)\s*{single_date_pattern})?$", date_input, re.I):
                        month_dict = {
                            "january": 1, "jan": 1, "february": 2, "feb": 2,
                            "march": 3, "mar": 3, "april": 4, "apr": 4,
                            "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
                            "august": 8, "aug": 8, "september": 9, "sep": 9,
                            "october": 10, "oct": 10, "november": 11, "nov": 11,
                            "december": 12, "dec": 12
                        }
                        if '-' in date_input or 'to' in date_input:
                            filter_for_date = 1
                            specific_date = 0
                            if '-' in date_input:
                                date1_str, date2_str = date_input.split('-')
                            else:
                                date1_str, date2_str = date_input.split('to')
                            date1_str, date2_str = date1_str.strip(), date2_str.strip()

                            if '/' in date1_str:
                                day1, month1, year1 = date1_str.split('/')
                            else:
                                day1, month1, year1 = date1_str.split(' ')

                            if '/' in date2_str:
                                day2, month2, year2 = date2_str.split('/')
                            else:
                                day2, month2, year2 = date2_str.split(' ')

                            day1, day2 = int(day1.strip()), int(day2.strip())
                            month1, month2 = month1.strip(), month2.strip()
                            month1 = month_dict[month1] if month1 in month_dict else int(month1)
                            month2 = month_dict[month2] if month2 in month_dict else int(month2)
                            year1, year2 = int(year1.strip()), int(year2.strip())
                            try:
                                date1 = date(year1, month1, day1)
                                date2 = date(year2, month2, day2)
                                break
                            except ValueError:
                                print()
                                print("╭" + "─" * 45 + "┐")
                                print("│" + " ⚠️ That date doesn't exist on the calendar. ".center(45) + "│")
                                print("│" + " Please check the date and try again.".center(45) + "│")
                                print("└" + "─" * 45 + "╯")
                        else:
                            filter_for_date = 1
                            specific_date = 1
                            if '/' in date_input:
                                day, month_v, year_v = date_input.split("/")
                            else:
                                day, month_v, year_v = date_input.split(" ")
                            day = int(day.strip())
                            month_v = month_v.strip()
                            month_num = month_dict[month_v] if month_v in month_dict else int(month_v)
                            year_num = int(year_v.strip())
                            try:
                                date_obj = date(year_num, month_num, day)
                                break
                            except ValueError:
                                print()
                                print("╭" + "─" * 45 + "┐")
                                print("│" + " ⚠️ That date doesn't exist on the calendar. ".center(45) + "│")
                                print("│" + " Please check the date and try again.".center(45) + "│")
                                print("└" + "─" * 45 + "╯")
                    else:
                        print()
                        print("╭" + "─" * 60 + "┐")
                        print("│" + "⚠️ Format doesn't match! Please check how you typed it.".center(60) + "│")
                        print("└" + "─" * 60 + "╯")

                take, give = 0, 0
                lent, repaid = 0, 0
                borrowed, received = 0, 0
                for person in persons:
                    if name == person["name"]:
                        person_amount = int(person["amount"])
                        if filter_for_date:
                            person_year, person_month, person_day = person["date"].split("-")
                            person_date = date(int(person_year), int(person_month), int(person_day))
                            if specific_date:
                                if date_obj != person_date:
                                    continue
                            else:
                                if not (date1 <= person_date <= date2):
                                    continue
                        if person["direction"] == "Debit":
                            if take == 0:
                                give += person_amount
                                lent += person_amount
                            else:
                                if person_amount <= take:
                                    take -= person_amount
                                    repaid += person_amount
                                else:
                                    give += person_amount - take
                                    repaid += take
                                    lent += person_amount - take
                                    take = 0
                        if person["direction"] == "Credit":
                            if give == 0:
                                take += person_amount
                                borrowed += person_amount
                            else:
                                if person_amount <= give:
                                    give -= person_amount
                                    received += person_amount
                                else:
                                    take += person_amount - give
                                    received += give
                                    borrowed += person_amount - give
                                    give = 0
                take = borrowed + received
                give = lent + repaid
                if not (take or give):
                    print()
                    print(("╭" + "─" * 39 + "┐").center(len_of_text))
                    print((("│" + " ⚠️ Empty Record Total ".center(39)) + "│").center(len_of_text))
                    print(("└" + "─" * 39 + "╯").center(len_of_text))
                    print()
                else:
                    length = max(
                        len(f"  {name.upper()}  "),
                        len("  Credit: ".ljust(10) + f"{output_amount(take)}  "),
                        len("     Lent: ".ljust(12) + f"   {output_amount(lent)}  "),
                        len("     Repaid: ".ljust(12) + f"   {output_amount(repaid)}  "),
                        len("  Debit: ".ljust(10) + f"{output_amount(give)}  "),
                        len("     Borrowed: ".ljust(12) + f"   {output_amount(borrowed)}  "),
                        len("     Received: ".ljust(12) + f"   {output_amount(received)}  "),
                    )
                    if filter_for_date:
                        if specific_date:
                            length = max(length, len(f"  Date: {output_date(date_obj, 0)}  "))
                        else:
                            length = max(length, len(f"  Date: {output_date(date1, 1)} to {output_date(date2, 1)}  "))
                    if take > give:
                        length = max(length, len(f" ◈  You owe {name.title()} {output_amount(take-give)} "))
                    elif take < give:
                        length = max(length, len(f" ◈  {name.title()} owes you {output_amount(give-take)} "))
                    else:
                        length = max(length, len(f" ✓  You and {name.title()} are all settled "))
                    print()
                    print(("╭" + "─" * (length + 1) + "┐").center(len_of_text))
                    if filter_for_date:
                        if specific_date:
                            print((("│" + f"  Date: {output_date(date_obj, 0)}  ".center(length)).ljust(length) + " │").center(len_of_text))
                            print(("├" + "─" * (length + 1) + "┤").center(len_of_text))
                        else:
                            print((("│" + f"  Date: {output_date(date1, 1)} to {output_date(date2, 1)}  ".center(length)).ljust(length) + " │").center(len_of_text))
                            print(("├" + "─" * (length + 1) + "┤").center(len_of_text))
                    print((("│" + f"  {name.upper()}  ".center(length)).ljust(length) + " │").center(len_of_text))
                    print(("├" + "─" * (length + 1) + "┤").center(len_of_text))
                    print((("│" + "  Credit: ".ljust(10) + f"{output_amount(take)}  ").ljust(length) + "  │").center(len_of_text))
                    print((("│" + "     Borrowed: ".ljust(12) + f"{output_amount(borrowed)}  ").ljust(length) + "  │").center(len_of_text))
                    print((("│" + "     Received: ".ljust(12) + f"{output_amount(received)}  ").ljust(length) + "  │").center(len_of_text))
                    print((("│" + "  Debit: ".ljust(10) + f"{output_amount(give)}  ").ljust(length) + "  │").center(len_of_text))
                    print((("│" + "     Lent: ".ljust(12) + f"{output_amount(lent)}  ").ljust(length) + "  │").center(len_of_text))
                    print((("│" + "     Repaid: ".ljust(12) + f"{output_amount(repaid)}  ").ljust(length) + "  │").center(len_of_text))
                    print(("├" + "─" * (length + 1) + "┤").center(len_of_text))
                    if take > give:
                        print((("│" + f" ◈  You owe {name.title()} {output_amount(take-give)} ".center(length)).ljust(length) + " │").center(len_of_text))
                    elif take < give:
                        print((("│" + f" ◈  {name.title()} owes you {output_amount(give-take)} ".center(length)).ljust(length) + " │").center(len_of_text))
                    else:
                        print((("│" + f" ✓  You and {name.title()} are all settled ".center(length)).ljust(length) + " │").center(len_of_text))
                    print(("└" + "─" * (length + 1) + "╯").center(len_of_text))
                    print()

                print(" Press 'd' or 'detail' for another person's details. ")
                print("Type:")
                print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
                while True:
                    select = input(": ").lower().strip()
                    try:
                        if select in ['b', 'back']:
                            print("─" * (len_of_text + 2))
                            return
                        elif select in ['e', 'exit']:
                            print("─" * (len_of_text + 2))
                            exit_()
                        elif select in ["d", "detail"]:
                            print("─" * (len_of_text + 2))
                            break
                        else:
                            raise ValueError()
                    except ValueError:
                        print("╭" + "─" * 19 + "┐")
                        print("│" + " ⚠️ Invalid Input!" + " │")
                        print("└" + "─" * 19 + "╯")
            except MemoryError:
                print(("╭" + "─" * 39 + "┐").center(len_of_text))
                print((("│" + " ⚠️ Empty Record Total ".center(39)) + "│").center(len_of_text))
                print(("└" + "─" * 39 + "╯").center(len_of_text))
                print("Type:")
                print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
                while True:
                    select = input(": ").lower().strip()
                    if select in ['1', 'b', 'back']:
                        print("─" * (len_of_text + 2))
                        return
                    elif select in ['2', 'e', 'exit']:
                        print("─" * (len_of_text + 2))
                        exit_()
                    else:
                        print("╭" + "─" * 19 + "┐")
                        print("│" + " ⚠️ Invalid Input!" + " │")
                        print("└" + "─" * 19 + "╯")
        elif choose in ['1', 'd', 'detail']:
            detail = 0
            selection = ""
            first_time = 1
            first_list_appears = 0
            person_for_details = []
            result_list = []
            while True:
                try:
                    persons = read_records(username)
                    if not persons:
                        raise MemoryError()
                    list_appears = 0
                    while True:
                        if selection in ['l', 'list']:
                            first_list_appears = 1
                            result_list = []
                            for person in sorted(persons, key=lambda s: s["name"]):
                                if person["name"] not in result_list:
                                    result_list.append(person["name"])
                            length = len("PERSON'S LIST")
                            for person in result_list:
                                if length < len(person):
                                    length = len(person)
                            length += 6
                            print()
                            print(("╭" + "─" * length + "┐").ljust(len_of_text))
                            print((("│" + "PERSON'S LIST".center(length)).ljust(length) + "│").ljust(len_of_text))
                            for i, person in enumerate(result_list):
                                print((("│" + f" {i+1}. {person}").ljust(length) + " │").ljust(len_of_text))
                            print(("└" + "─" * length + "╯").ljust(len_of_text))
                            print(" Enter S.No(s). or full name(s) with comma(s) from list.")
                            list_appears = 1
                        elif selection in ['s', 'search']:
                            keyword = input("Search Keyword: ").strip().lower()
                            first_list_appears = 1
                            result_list = []
                            for person in sorted(persons, key=lambda s: s["name"]):
                                if re.search(rf'\b{re.escape(keyword)}', person["name"], re.I) and person["name"] not in result_list:
                                    result_list.append(person["name"])
                            if len(result_list):
                                length = len(f"SEARCH RESULT FOR {keyword}")
                                for person in result_list:
                                    if length < len(person):
                                        length = len(person)
                                length += 6
                                print()
                                print(("╭" + "─" * length + "┐").ljust(len_of_text))
                                print((("│" + f"Search Result for '{keyword}'".center(length)).ljust(length) + "│").ljust(len_of_text))
                                for i, person in enumerate(result_list):
                                    print((("│" + f" {i+1}. {person}").ljust(length) + " │").ljust(len_of_text))
                                print(("└" + "─" * length + "╯").ljust(len_of_text))
                                print(" Enter S.No(s). or full name(s) with comma(s) from list.")
                                list_appears = 1
                        else:
                            break
                        if len(result_list):
                            print(" Type retry to try again.")
                            print()
                            select = input(": ").strip().title()
                            if select in ["Retry"]:
                                list_appears = 0
                                break
                            else:
                                break
                        else:
                            first_list_appears = 1
                            print("╭" + "─" * len_of_text + "┐")
                            print("│" + f" No match found for '{keyword}'".center(len_of_text) + "│")
                            print("│" + " Type 'l' or 'list' to see all persons. ".center(len_of_text) + "│")
                            print("│" + " Type 's' or 'search' to search person. ".center(len_of_text) + "│")
                            print("│" + " Type retry to try again.".center(len_of_text) + "│")
                            print("└" + "─" * len_of_text + "╯")
                            list_appears = 0
                            while True:
                                select = input(": ").strip().lower()
                                if select in ["retry"]:
                                    break
                                elif select in ["l", 'list']:
                                    selection = "list"
                                    break
                                elif select in ["s", "search"]:
                                    selection = "search"
                                    break
                                else:
                                    print("╭" + "─" * 19 + "┐")
                                    print("│" + " ⚠️ Invalid input!" + " │")
                                    print("└" + "─" * 19 + "╯")
                            if select == "retry":
                                break

                    if not list_appears:
                        if first_time:
                            print("╭" + "─" * len_of_text + "┐")
                            print("│" + "  Enter single name or multiple names, seperated by comma(s)".ljust(len_of_text) + "│")
                            print("│" + "    single name    - satyam".ljust(len_of_text) + "│")
                            print("│" + "    multiple names - satyam, shivam".ljust(len_of_text) + "│")
                            print("│" + "    Type 'all' to select all persons.".ljust(len_of_text) + "│")
                            print("└" + "─" * len_of_text + "╯")
                            print("Type:")
                            print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
                            first_time = 0

                    while True:
                        if not list_appears:
                            result_list = []
                            select = input("Person's Name(s): ").title().strip()
                            if select in ['B', 'Back']:
                                print("─" * (len_of_text + 2))
                                return
                            elif select in ['E', 'Exit']:
                                print("─" * (len_of_text + 2))
                                exit_()
                        if first_list_appears:
                            if select in ["Retry", "retry"]:
                                break
                        if list_appears:
                            matches = re.search(r'^([a-zA-Z]+[a-zA-Z0-9]*(\s+[a-zA-Z]+[a-zA-Z0-9]*)*|\d+)(\s*,\s*([a-zA-Z]+[a-zA-Z0-9]*(\s+[a-zA-Z]+[a-zA-Z0-9]*)*|\d+))*$', select)
                        else:
                            matches = re.search(r'^([a-zA-z][a-zA-z0-9]*\s*)+(,\s*([a-zA-z][a-zA-z0-9]*\s*)+)*$', select)

                        if matches:
                            if ',' in select:
                                parts = select.split(',')
                                person_list = []
                                for part in parts:
                                    p_clean = part.strip()
                                    if p_clean not in person_list:
                                        person_list.append(p_clean)
                            else:
                                person_list = [select]

                            person_status_dict = person_exists(person_list, persons, result_list)
                            num_person_exists = len(person_status_dict[True])
                            for person in person_status_dict[True]:
                                if person not in person_for_details:
                                    person_for_details.append(person)

                            if select == "All" and list_appears == 0:
                                print("╭" + "─" * 29 + "┐")
                                print("│" + " Proceeding for all persons. " + "│")
                                print("└" + "─" * 29 + "╯")
                                sel = filter_details(person_for_details, persons)
                                if sel == "back":
                                    return
                                else:
                                    detail = 1
                                    break
                            elif not len(person_for_details):
                                length = 17
                                for person in person_status_dict[False]:
                                    length += len(person)
                                    if len(person_status_dict[False]) != 1:
                                        if len(person_status_dict[False]) == 2 and person_status_dict[False][0] == person:
                                            length += len(" and ")
                                        elif len(person_status_dict[False]) > 2:
                                            if person_status_dict[False][len(person_status_dict[False]) - 1] != person:
                                                length += len(", ")
                                            if person_status_dict[False][len(person_status_dict[False]) - 2] == person:
                                                length += len("and ")
                                l = 0 if length > 40 else 40 - length
                                length = max(length, 40)
                                print("╭" + "─" * length + "┐")
                                print("│" + " ⚠️ ", end="")
                                for person in person_status_dict[False]:
                                    print(f"{person}", end='')
                                    if len(person_status_dict[False]) != 1:
                                        if len(person_status_dict[False]) == 2 and person_status_dict[False][0] == person:
                                            print(" and ", end='')
                                        elif len(person_status_dict[False]) > 2:
                                            if person_status_dict[False][len(person_status_dict[False]) - 1] != person:
                                                print(", ", end='')
                                            if person_status_dict[False][len(person_status_dict[False]) - 2] == person:
                                                print("and ", end='')
                                print(" not found. " + " " * l + " │")
                                print("│" + " Type 'l' or 'list' to see all persons. ".ljust(length) + "│")
                                print("│" + " Type 's' or 'search' to search person. ".ljust(length) + "│")
                                print("│" + " Press Enter to retry.".ljust(length) + "│")
                                print("└" + "─" * length + "╯")
                                selection = input(": ").strip().lower()
                                if selection in ['s', 'l', 'search', 'list']:
                                    break
                                else:
                                    list_appears = 0
                            else:
                                length1 = 17
                                if len(person_list) != num_person_exists:
                                    for person in person_status_dict[False]:
                                        length1 += len(person)
                                        if len(person_status_dict[False]) != 1:
                                            if len(person_status_dict[False]) == 2 and person_status_dict[False][0] == person:
                                                length1 += len(" and ")
                                            elif len(person_status_dict[False]) > 2:
                                                if person_status_dict[False][len(person_status_dict[False]) - 1] != person:
                                                    length1 += len(", ")
                                                if person_status_dict[False][len(person_status_dict[False]) - 2] == person:
                                                    length1 += len("and ")
                                length2 = 41
                                for person in person_for_details:
                                    length2 += len(person)
                                    if len(person_for_details) != 1:
                                        if len(person_for_details) == 2 and person_for_details[0] == person:
                                            length2 += len(" and ")
                                        elif len(person_for_details) > 2:
                                            if person_for_details[len(person_for_details) - 1] != person:
                                                length2 += len(", ")
                                            if person_for_details[len(person_for_details) - 2] == person:
                                                length2 += len("and ")
                                l = 0 if length1 >= 40 and length1 >= length2 else max(40, length2) - length1
                                le = 0 if length2 >= 40 and length2 >= length1 else max(40, length1) - length2
                                length = max(length1, 40, length2)
                                print("╭" + "─" * length + "┐")
                                if len(person_list) != num_person_exists:
                                    print("│" + " ⚠️ ", end="")
                                    for person in person_status_dict[False]:
                                        print(f"{person}", end='')
                                        if len(person_status_dict[False]) != 1:
                                            if len(person_status_dict[False]) == 2 and person_status_dict[False][0] == person:
                                                print(" and ", end='')
                                            elif len(person_status_dict[False]) > 2:
                                                if person_status_dict[False][len(person_status_dict[False]) - 1] != person:
                                                    print(", ", end='')
                                                if person_status_dict[False][len(person_status_dict[False]) - 2] == person:
                                                    print("and ", end='')
                                    print(" not found. " + " " * l + " │")
                                if len(person_list) == num_person_exists:
                                    print("│" + " Type 'p' or 'proceed' to proceed with ", end='')
                                    for person in person_for_details:
                                        print(f"{person}", end='')
                                        if len(person_for_details) != 1:
                                            if len(person_for_details) == 2 and person_for_details[0] == person:
                                                print(" and ", end='')
                                            elif len(person_for_details) > 2:
                                                if person_for_details[len(person_for_details) - 1] != person:
                                                    print(", ", end='')
                                                if person_for_details[len(person_for_details) - 2] == person:
                                                    print("and ", end='')
                                    print(". " + " " * le + "│")
                                    print("│" + " To add ".ljust(length) + "│")
                                print("│" + " Type 'l' or 'list' to see all persons. ".ljust(length) + "│")
                                print("│" + " Type 's' or 'search' to search person. ".ljust(length) + "│")
                                if len(person_list) != num_person_exists:
                                    print("│" + " Type 'p' or 'proceed' to proceed with ", end='')
                                    for person in person_for_details:
                                        print(f"{person}", end='')
                                        if len(person_for_details) != 1:
                                            if len(person_for_details) == 2 and person_for_details[0] == person:
                                                print(" and ", end='')
                                            elif len(person_for_details) > 2:
                                                if person_for_details[len(person_for_details) - 1] != person:
                                                    print(", ", end='')
                                                if person_for_details[len(person_for_details) - 2] == person:
                                                    print("and ", end='')
                                    print(". " + " " * le + "│")
                                print("│" + " Press Enter to add more.".ljust(length) + "│")
                                print("└" + "─" * length + "╯")
                                selection = input(": ").strip().lower()
                                if selection in ['s', 'l', 'search', 'list']:
                                    break
                                elif selection in ['p', 'proceed']:
                                    sel = filter_details(person_for_details, persons)
                                    if sel == "back":
                                        return
                                    else:
                                        detail = 1
                                        break
                                else:
                                    list_appears = 0
                        else:
                            print("╭" + "─" * 20 + "┐")
                            print("│" + " ⚠️ Invalid Format!" + "│")
                            print("└" + "─" * 20 + "╯")
                            list_appears = 0
                    if detail:
                        break
                except MemoryError:
                    print(("╭" + "─" * 39 + "┐").center(len_of_text))
                    print((("│" + " ⚠️ Empty Record Details ".center(39)) + "│").center(len_of_text))
                    print(("└" + "─" * 39 + "╯").center(len_of_text))
                    print("Type:")
                    print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
                    while True:
                        select = input(": ").lower().strip()
                        if select in ['1', 'b', 'back']:
                            print("─" * (len_of_text + 2))
                            return
                        elif select in ['2', 'e', 'exit']:
                            print("─" * (len_of_text + 2))
                            exit_()
                        else:
                            print("╭" + "─" * 19 + "┐")
                            print("│" + " ⚠️ Invalid Input!" + " │")
                            print("└" + "─" * 19 + "╯")


def filter_details(names, persons):
    names_details = []
    while True:
        choice = input("Would you like to apply fiters? (yes/no): ").strip().lower()
        if choice in ['2', 'n', 'no']:
            for name in names:
                for person in persons:
                    if person["name"] == name:
                        names_details.append(person)
            for details_item in names_details:
                if not details_item["note"]:
                    details_item["note"] = "N/A"
            print()
            names_details = sorted_list_wrt_date(names_details)
            names_details = output_records_formet(names_details, 3)
            if len(names) == 1:
                rows = ["s.no.", "date", "direction", "mode", "amount", "note"]
            else:
                rows = ["s.no.", "date", "name", "direction", "mode", "amount", "note"]
            head = "Details for "
            for name in names:
                head += f"{name}"
                if len(names) != 1:
                    if len(names) == 2 and names[0] == name:
                        head += " and "
                    elif len(names) > 2:
                        if names[len(names) - 1] != name:
                            head += ", "
                        if names[len(names) - 2] == name:
                            head += "and "
            break
        elif choice in ['1', 'y', 'yes']:
            print("╭" + "─" * 47 + "┐")
            print("│" + "📆 Date Formats".center(45) + " │")
            print("│" + "  DD/MM/YYYY".ljust(25) + "eg. 25/11/2025       " + " │")
            print("│" + "  DD Month YYYY".ljust(25) + "eg. 25 November 2025 " + " │")
            print("│" + "  specific date".ljust(25) + "eg. write in format " + "  │")
            print("│" + "  between two dates".ljust(25) + "eg1. date1 - date2 " + "   │")
            print("│" + "  between two dates".ljust(25) + "eg2. date1 to date2 " + "  │")
            print("│" + " Press Enter to skip. ".ljust(47) + "│")
            print("└" + "─" * 47 + "╯")
            months = [
                "january", "february", "march", "april", "may", "june",
                "july", "august", "september", "october", "november", "december",
                "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"
            ]
            months = sorted(months, key=len, reverse=True)
            months_pattern = "|".join(map(re.escape, months))
            single_date_pattern = rf"\d{{1,2}}(?:/(?:\d{{1,2}}|{months_pattern})/|\s+(?:\d{{1,2}}|{months_pattern})\s+)\d{{4}}"

            month_dict = {
                "january": 1, "jan": 1, "february": 2, "feb": 2,
                "march": 3, "mar": 3, "april": 4, "apr": 4,
                "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
                "august": 8, "aug": 8, "september": 9, "sep": 9,
                "october": 10, "oct": 10, "november": 11, "nov": 11,
                "december": 12, "dec": 12
            }

            while True:
                date_input = input("Date: ").strip().lower()
                if date_input == "":
                    filter_for_date = 0
                    break
                elif re.search(rf"^{single_date_pattern}(?:\s*(?:-|to)\s*{single_date_pattern})?$", date_input, re.I):
                    if '-' in date_input or 'to' in date_input:
                        filter_for_date = 1
                        specific_date = 0
                        if '-' in date_input:
                            date1_str, date2_str = date_input.split('-')
                        else:
                            date1_str, date2_str = date_input.split('to')
                        date1_str, date2_str = date1_str.strip(), date2_str.strip()
                        if '/' in date1_str:
                            day1, month1, year1 = date1_str.split('/')
                        else:
                            day1, month1, year1 = date1_str.split(' ')
                        if '/' in date2_str:
                            day2, month2, year2 = date2_str.split('/')
                        else:
                            day2, month2, year2 = date2_str.split(' ')
                        day1, day2 = int(day1.strip()), int(day2.strip())
                        month1, month2 = month1.strip(), month2.strip()
                        month1 = month_dict[month1] if month1 in month_dict else int(month1)
                        month2 = month_dict[month2] if month2 in month_dict else int(month2)
                        year1, year2 = int(year1.strip()), int(year2.strip())
                        try:
                            date1 = date(year1, month1, day1)
                            date2 = date(year2, month2, day2)
                            break
                        except ValueError:
                            print()
                            print("╭" + "─" * 45 + "┐")
                            print("│" + " ⚠️ That date doesn't exist on the calendar. ".center(45) + "│")
                            print("│" + " Please check the date and try again.".center(45) + "│")
                            print("└" + "─" * 45 + "╯")
                    else:
                        filter_for_date = 1
                        specific_date = 1
                        if '/' in date_input:
                            day, month_v, year_v = date_input.split("/")
                        else:
                            day, month_v, year_v = date_input.split(" ")
                        day = int(day.strip())
                        month_v = month_v.strip()
                        month_num = month_dict[month_v] if month_v in month_dict else int(month_v)
                        year_num = int(year_v.strip())
                        try:
                            date_obj = date(year_num, month_num, day)
                            break
                        except ValueError:
                            print()
                            print("╭" + "─" * 45 + "┐")
                            print("│" + " ⚠️ That date doesn't exist on the calendar. ".center(45) + "│")
                            print("│" + " Please check the date and try again.".center(45) + "│")
                            print("└" + "─" * 45 + "╯")
                else:
                    print()
                    print("╭" + "─" * 60 + "┐")
                    print("│" + "⚠️ Format doesn't match! Please check how you typed it.".center(60) + "│")
                    print("└" + "─" * 60 + "╯")

            while True:
                print()
                print("Press Enter to skip")
                direction = input("Direction (credit/debit): ").strip().lower()
                if direction == "":
                    filter_for_direction = 0
                    break
                filter_for_direction = 1
                if direction in ['1', 'c', 'credit']:
                    direction = "Credit"
                    break
                elif direction in ['2', 'd', 'debit']:
                    direction = "Debit"
                    break
                else:
                    print("╭" + "─" * 19 + "┐")
                    print("│" + " ⚠️ Invalid Input!" + " │")
                    print("└" + "─" * 19 + "╯")

            while True:
                print()
                print("Press Enter to skip")
                mode = input("mode (online/cash): ").strip().lower()
                if mode == "":
                    filter_for_mode = 0
                    break
                filter_for_mode = 1
                if mode in ['1', 'o', 'online']:
                    mode = "Online"
                    break
                elif mode in ['2', 'c', 'cash']:
                    mode = "Cash"
                    break
                else:
                    print("╭" + "─" * 19 + "┐")
                    print("│" + " ⚠️ Invalid Input!" + " │")
                    print("└" + "─" * 19 + "╯")

            for name in names:
                for person in persons:
                    if name == person["name"]:
                        if filter_for_direction and direction != person["direction"]:
                            continue
                        if filter_for_mode and mode != person["mode"]:
                            continue
                        if filter_for_date:
                            person_year, person_month, person_day = person["date"].split("-")
                            person_date = date(int(person_year), int(person_month), int(person_day))
                            if specific_date:
                                if date_obj != person_date:
                                    continue
                            else:
                                if not (date1 <= person_date <= date2):
                                    continue
                        names_details.append(person)

            for details_item in names_details:
                if not details_item["note"]:
                    details_item["note"] = "N/A"
            print()
            names_details = sorted_list_wrt_date(names_details)
            names_details = output_records_formet(names_details, 3)
            rows = ["s.no."]
            if not filter_for_date or not specific_date:
                rows.append("date")
            if len(names) != 1:
                rows.append("name")
            if not filter_for_direction:
                rows.append("direction")
            if not filter_for_mode:
                rows.append("mode")
            rows = rows + ["amount", "note"]
            head = "Details for "
            for name in names:
                head += f"{name}"
                if len(names) != 1:
                    if len(names) == 2 and names[0] == name:
                        head += " and "
                    elif len(names) > 2:
                        if names[len(names) - 1] != name:
                            head += ", "
                        if names[len(names) - 2] == name:
                            head += "and "
            if filter_for_date:
                if specific_date:
                    print("| Date-", output_date(date_obj, 3), end=" |")
                else:
                    print("| Date-", f"{output_date(date1, 3)} to {output_date(date2, 3)}", end=" |")
            if filter_for_direction:
                print("| Direction-", direction, end=' |')
            if filter_for_mode:
                print("| Mode-", mode, end=' |')
            print()
            break
        else:
            print("╭" + "─" * 19 + "┐")
            print("│" + " ⚠️ Invalid Input!" + " │")
            print("└" + "─" * 19 + "╯")

    if names_details:
        measurement = length_list(names_details, rows, head)
        print_list(measurement, names_details, rows, head)
        while True:
            print(("╭" + "─" * 55 + "┐").center(len_of_text))
            print((("│" + " Enter S.No. to view Record Details.".center(55)) + "│").center(len_of_text))
            print((("│" + " Press 'd' or 'detail' for another person's details. ".center(55)) + "│").center(len_of_text))
            print(("└" + "─" * 55 + "╯").center(len_of_text))
            print("Type:")
            print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
            select = input(": ").lower().strip()
            try:
                if select in ['b', 'back']:
                    print("─" * (len_of_text + 2))
                    return "back"
                elif select in ['e', 'exit']:
                    print("─" * (len_of_text + 2))
                    exit_()
                elif select in ["d", "detail"]:
                    print("─" * (len_of_text + 2))
                    return "detail"
                elif 0 < int(select) <= len(names_details):
                    show_person_details(int(select) - 1, names_details)
                else:
                    raise ValueError()
            except ValueError:
                print("╭" + "─" * 19 + "┐")
                print("│" + " ⚠️ Invalid Input!" + " │")
                print("└" + "─" * 19 + "╯")
    else:
        print("╭" + "─" * 31 + "┐")
        print("│" + "     ⚠️ No Record Exists.     " + " │")
        print("└" + "─" * 31 + "╯")
        print(" Press 'd' or 'detail' for another person's details. ")
        print("Type:")
        print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
        while True:
            select = input(": ").lower().strip()
            try:
                if select in ['b', 'back']:
                    print("─" * (len_of_text + 2))
                    return "back"
                elif select in ['e', 'exit']:
                    print("─" * (len_of_text + 2))
                    exit_()
                elif select in ["d", "detail"]:
                    print("─" * (len_of_text + 2))
                    return "detail"
                else:
                    raise ValueError()
            except ValueError:
                print("╭" + "─" * 19 + "┐")
                print("│" + " ⚠️ Invalid Input!" + " │")
                print("└" + "─" * 19 + "╯")


def search(username: str) -> None:
    while True:
        print("─" * (int(len_of_text / 2) - 3) + " SEARCH " + "─" * (int(len_of_text / 2) - 2))
        persons = read_records(username)
        if persons:
            search_result = []
            keyword_list = []
            while True:
                searched_keyword = input("Search Keyword: ").strip().lower()
                if not searched_keyword:
                    print(("╭" + "─" * 40 + "┐").center(len_of_text))
                    print(("│" + "⚠️ Search field can't be empty! ".center(40) + "│").center(len_of_text))
                    print(("│" + " Please enter keyword. ".center(40) + "│").center(len_of_text))
                    print(("└" + "─" * 40 + "╯").center(len_of_text))
                else:
                    break
            if " " in searched_keyword:
                keyword_list = searched_keyword.split()
            keyword_list.insert(0, searched_keyword)

            for keyword in keyword_list:
                months = [
                    "january", "february", "march", "april", "may", "june",
                    "july", "august", "september", "october", "november", "december",
                    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"
                ]
                months = sorted(months, key=len, reverse=True)
                months_pattern = "|".join(map(re.escape, months))
                single_date_pattern = rf"\d{{1,2}}(?:/(?:\d{{1,2}}|{months_pattern})/|\s+(?:\d{{1,2}}|{months_pattern})\s+)\d{{4}}"
                specific_date = 0
                search_for_date = 0

                if re.search(rf"^{single_date_pattern}(?:\s*(?:-|to)\s*{single_date_pattern})?$", keyword, re.I):
                    date_ = keyword
                    month_dict = {
                        "january": 1, "jan": 1, "february": 2, "feb": 2,
                        "march": 3, "mar": 3, "april": 4, "apr": 4,
                        "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
                        "august": 8, "aug": 8, "september": 9, "sep": 9,
                        "october": 10, "oct": 10, "november": 11, "nov": 11,
                        "december": 12, "dec": 12
                    }
                    if '-' in date_ or 'to' in date_:
                        search_for_date = 1
                        specific_date = 0
                        if '-' in date_:
                            date1_s, date2_s = date_.split('-')
                        else:
                            date1_s, date2_s = date_.split('to')
                        date1_s, date2_s = date1_s.strip(), date2_s.strip()
                        if '/' in date1_s:
                            day1, month1, year1 = date1_s.split('/')
                        else:
                            day1, month1, year1 = date1_s.split(' ')
                        if '/' in date2_s:
                            day2, month2, year2 = date2_s.split('/')
                        else:
                            day2, month2, year2 = date2_s.split(' ')
                        day1, day2 = int(day1.strip()), int(day2.strip())
                        month1, month2 = month1.strip(), month2.strip()
                        month1 = month_dict[month1] if month1 in month_dict else int(month1)
                        month2 = month_dict[month2] if month2 in month_dict else int(month2)
                        year1, year2 = int(year1.strip()), int(year2.strip())
                        try:
                            date1 = date(year1, month1, day1)
                            date2 = date(year2, month2, day2)
                        except ValueError:
                            search_for_date = 0
                    else:
                        search_for_date = 1
                        specific_date = 1
                        if '/' in date_:
                            day, month_v, year_v = date_.split("/")
                        else:
                            day, month_v, year_v = date_.split(" ")
                        day = int(day.strip())
                        month_v = month_v.strip()
                        month_num = month_dict[month_v] if month_v in month_dict else int(month_v)
                        year_num = int(year_v.strip())
                        try:
                            date_obj = date(year_num, month_num, day)
                        except ValueError:
                            search_for_date = 0

                amount_searched = keyword
                for term in [',', '.', 'rs', 'rupee', 'rupees', '₹']:
                    amount_searched = amount_searched.replace(term, '').strip()

                pattern = rf"(?:^|(?<=[.!?]\s))[^.!?]*?{re.escape(keyword)}[^.!?]*(?:[.!?]|$)"
                pattern_for_amount = rf"(?:^|(?<=[.!?]\s))[^.!?]*?{re.escape(amount_searched)}[^.!?]*(?:[.!?]|$)"

                for person in persons:
                    if person in search_result:
                        continue
                    if re.search(pattern, person["name"], re.I):
                        search_result.append(person)
                        continue
                    if re.search(pattern, person["note"], re.I):
                        search_result.append(person)
                        continue
                    if re.search(pattern, person["mode"], re.I):
                        search_result.append(person)
                        continue
                    if re.search(pattern, person["direction"], re.I):
                        search_result.append(person)
                        continue
                    if re.search(pattern_for_amount, person["amount"], re.I):
                        search_result.append(person)
                        continue
                    if re.search(pattern, person["date"], re.I):
                        search_result.append(person)
                        continue
                    if search_for_date:
                        person_year, person_month, person_day = person["date"].split("-")
                        person_date = date(int(person_year), int(person_month), int(person_day))
                        if specific_date:
                            if date_obj == person_date:
                                search_result.append(person)
                                continue
                        else:
                            if date1 <= person_date <= date2:
                                search_result.append(person)
                                continue

            search_result = output_records_formet(search_result, 3)
            if search_result:
                for person in search_result:
                    if not person["note"]:
                        person["note"] = "N/A"
                rows = ["s.no.", "date", "name", "mode", "direction", "amount", "note"]
                if len(search_result) == 1:
                    head = f"Searched Result for '{searched_keyword}'"
                else:
                    head = f"Searched Results for '{searched_keyword}'"
                measurement = length_list(search_result, rows, head)
                print_list(measurement, search_result, rows, head)
                while True:
                    print(("╭" + "─" * 45 + "┐").center(len_of_text))
                    print((("│" + "Enter S.No. to view Details.".center(45)) + "│").center(len_of_text))
                    print(("│" + " Type 's' or 'search' to search again. ".center(45) + "│").center(len_of_text))
                    print(("└" + "─" * 45 + "╯").center(len_of_text))
                    print("Type:")
                    print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
                    select = input(": ").lower().strip()
                    try:
                        if select in ['s', 'search']:
                            print("─" * (len_of_text + 2))
                            break
                        if select in ['b', 'back']:
                            print("─" * (len_of_text + 2))
                            return
                        elif select in ['e', 'exit']:
                            print("─" * (len_of_text + 2))
                            exit_()
                        elif 0 < int(select) <= len(search_result):
                            show_person_details(int(select) - 1, search_result)
                        else:
                            raise ValueError
                    except ValueError:
                        print("╭" + "─" * 19 + "┐")
                        print("│" + " ⚠️ Invalid Input!" + " │")
                        print("└" + "─" * 19 + "╯")
            else:
                length = max(len(f" No match found for '{searched_keyword}'") + 10, len(" Type 's' or 'search' to search again. "))
                print(("╭" + "─" * (length + 1) + "┐").center(len_of_text))
                print(("│ " + f" ⚠️ No match found for '{searched_keyword}'".center(length) + "│").center(len_of_text))
                print(("│ " + " Type 's' or 'search' to search again. ".center(length) + "│").center(len_of_text))
                print(("└" + "─" * (length + 1) + "╯").center(len_of_text))
                print("Type:")
                print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
                while True:
                    select = input(": ").lower().strip()
                    if select in ['s', 'search']:
                        print("─" * (len_of_text + 2))
                        break
                    if select in ['b', 'back']:
                        print("─" * (len_of_text + 2))
                        return
                    elif select in ['e', 'exit']:
                        print("─" * (len_of_text + 2))
                        exit_()
                    else:
                        print("╭" + "─" * 19 + "┐")
                        print("│" + " ⚠️ Invalid Input!" + " │")
                        print("└" + "─" * 19 + "╯")
        else:
            print_empty_search()
            return


def profile(username: str, users: list, user: dict) -> None:
    print("─" * (int(len_of_text / 2) - 3) + " PROFILE " + "─" * (int(len_of_text / 2) - 3))
    length = len(f"  {user['username']}  ") + 4
    print()
    print(("╭" + "─" * length + "┐").center(len_of_text))
    print(("│  " + f"  {user['username']}  " + "  │").center(len_of_text))
    print(("└" + "─" * length + "╯").center(len_of_text))
    date_time = datetime.fromisoformat(user["datetime"])
    date_ = date_time.date()
    time_ = date_time.strftime("%I:%M:%S %p")
    print(f"Created on {output_date(date_, 0)}  ".rjust(len_of_text))
    print(f"{time_}  ".rjust(len_of_text))
    gap: int = int((len_of_text - 36) / 3)
    while True:
        print()
        print(" " * gap + "╭" + "─" * 18 + "┐" + " " * gap + "╭" + "─" * 18 + "┐" + " " * gap)
        print(" " * gap + "│ 1. EDIT PROFILE  │" + " " * gap + "│  2. IMPORTANT    │" + " " * gap)
        print(" " * gap + "└" + "─" * 18 + "╯" + " " * gap + "└" + "─" * 18 + "╯" + " " * gap)
        print(" " * gap + "╭" + "─" * 18 + "┐" + " " * gap + "╭" + "─" * 18 + "┐" + " " * gap)
        print(" " * gap + "│    3. MANAGE     │" + " " * gap + "│    4. STATS      │" + " " * gap)
        print(" " * gap + "└" + "─" * 18 + "╯" + " " * gap + "└" + "─" * 18 + "╯" + " " * gap)
        print(("╭" + "─" * 18 + "┐").center(len_of_text))
        print(("│" + "5. LOG OUT".center(18) + "│").center(len_of_text))
        print(("└" + "─" * 18 + "╯").center(len_of_text))
        print("Type:")
        print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program\n")
        while True:
            select = input("Select: ").strip().lower()
            if select in ['1', 'e', 'ep', 'p', "edit", "profile", "edit profile"]:
                select = edit_profile(users, user)
                if select == "back to main":
                    print("─" * (len_of_text + 2))
                    return "back to main"
                if select == "back":
                    return
                else:
                    print("─" * (int(len_of_text / 2) - 3) + " PROFILE " + "─" * (int(len_of_text / 2) - 3))
                    break
            elif select in ['2', 'i', 'imp', "important"]:
                select = important(username)
                if select == "back":
                    return
                else:
                    print("─" * (int(len_of_text / 2) - 3) + " PROFILE " + "─" * (int(len_of_text / 2) - 3))
                    break
            elif select in ['3', 'm', 'manage']:
                select = manage(username)
                if select == "back":
                    return
                else:
                    print("─" * (int(len_of_text / 2) - 3) + " PROFILE " + "─" * (int(len_of_text / 2) - 3))
                    break
            elif select in ['4', 's', 'stats']:
                select = stats(username)
                if select == "back":
                    return
                else:
                    print("─" * (int(len_of_text / 2) - 3) + " PROFILE " + "─" * (int(len_of_text / 2) - 3))
                    break
            elif select in ['5', 'l', 'log out', 'out']:
                select = logout()
                if select == "back to main":
                    print("─" * (len_of_text + 2))
                    return "back to main"
                if select == "back":
                    return
                else:
                    print("─" * (int(len_of_text / 2) - 3) + " PROFILE " + "─" * (int(len_of_text / 2) - 3))
                    break
            elif select in ['b', 'back']:
                print("─" * (len_of_text + 2))
                return
            elif select in ["exit"]:
                print("─" * (len_of_text + 2))
                exit_()
            else:
                print("╭" + "─" * len_of_text + "┐")
                print("│" + "⚠️ Invalid Selection!".center(len_of_text) + "│")
                print("│" + "Enter '1' or 'e' or 'ep' or 'edit profile' to Edit Profile.".center(len_of_text) + "│")
                print("│" + "Enter '2' or 'i' or 'imp' or 'important' for Important.".center(len_of_text) + "│")
                print("│" + "Enter '3' or 'm' or 'manage' for Manage.".center(len_of_text) + "│")
                print("│" + "Enter '4' or 's' or 'stats' for Stats.".center(len_of_text) + "│")
                print("└" + "─" * len_of_text + "╯")


def edit_profile(users, user):
    gap: int = int((len_of_text - 42) / 3)
    print("─" * (len_of_text + 2))
    print()
    print(" " * gap + "╭" + "─" * 21 + "┐" + " " * gap + "╭" + "─" * 21 + "┐" + " " * gap)
    print(" " * gap + "│ 1. CHANGE USERNAME  │" + " " * gap + "│ 2. CHANGE PASSWORD  │" + " " * gap)
    print(" " * gap + "└" + "─" * 21 + "╯" + " " * gap + "└" + "─" * 21 + "╯" + " " * gap)
    print("Type:")
    print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program\n")
    while True:
        select = input("Select: ").strip().lower()
        if select in ['1', 'u', 'username', 'change username']:
            print("─" * (len_of_text + 2))
            if user["lockout_time"]:
                elapsed = time.time() - float(user["lockout_time"])
                if elapsed < 30:
                    remaining = int(30 - elapsed)
                    print("╭" + "─" * len_of_text + "┐")
                    print("│" + (f"🔒 Account locked. Try again in {remaining} seconds.").center(len_of_text - 1) + "│")
                    print("└" + "─" * len_of_text + "╯")
                    print("─" * (len_of_text + 2))
                    return
                else:
                    user["lockout_time"] = ''
                    user["failed_attempts"] = '0'
            print(("TO CHANGE YOUR USERNAME").center(len_of_text))
            while True:
                password: str = hashlib.sha256(pwinput("Confirm Password: ").encode()).hexdigest()
                try:
                    if user["password"] != password:
                        attempts = int(user['failed_attempts']) + 1
                        user['failed_attempts'] = str(attempts)
                        if attempts >= 5:
                            user["lockout_time"] = str(time.time())
                            raise NameError()
                        raise ValueError()
                    user['failed_attempts'] = '0'
                    user['lockout_time'] = ''
                    write_users(users)
                    break
                except ValueError:
                    print("╭" + "─" * 42 + "┐")
                    print("│" + " ⚠️ Incorrect password. Please try again." + " │")
                    print("└" + "─" * 42 + "╯")
                    write_users(users)
                except NameError:
                    print("╭" + "─" * len_of_text + "┐")
                    print("│" + "🔒 Too many failed attempts. Account locked for 30 seconds.".center(len_of_text - 1) + "│")
                    print("└" + "─" * len_of_text + "╯")
                    write_users(users)
                    return "back to main"
            length = len("Current Username: " + user["username"]) + 4
            print("╭" + "─" * length + "┐")
            print("│  " + "Current Username: " + user["username"] + "  │")
            print("└" + "─" * length + "╯")
            while True:
                uf = 0
                change_username = input("New Username: ").strip().lower()
                if change_username != user["username"]:
                    if re.search(r"^[a-z]\w*$", change_username, re.I):
                        for user_ in users:
                            if user_["username"] == change_username:
                                uf = 1
                                break
                        if not uf:
                            break
                        else:
                            print("╭" + "─" * len_of_text + "┐")
                            print("│" + "⚠️ Username already exists. Try something unique.".center(len_of_text) + "│")
                            print("└" + "─" * len_of_text + "╯")
                    else:
                        print("╭" + "─" * len_of_text + "┐")
                        print("│" + "⚠️ Invalid Username!".center(len_of_text) + "│")
                        print("│" + "  Username must start with a letter".ljust(len_of_text) + "│")
                        print("│" + "  Username contain only letters, numbers, and _ Underscores".ljust(len_of_text) + "│")
                        print("│" + "  Not allowed: special characters, and spaces".ljust(len_of_text) + "│")
                        print("└" + "─" * len_of_text + "╯")
                else:
                    print("╭" + "─" * len_of_text + "┐")
                    print("│" + "⚠️ New username must be different from your current one.".center(len_of_text) + "│")
                    print("└" + "─" * len_of_text + "╯")
            length = len("Username: " + change_username) + 4
            print("╭" + "─" * length + "┐")
            print("│  " + "Username: " + change_username + "  │")
            print("└" + "─" * length + "╯")
            while True:
                choose = input("Save Changes? (yes/no):").strip().lower()
                if choose in ['y', 'yes']:
                    update_record = read_records()
                    for person in update_record:
                        if person["username"] == user["username"]:
                            person["username"] = change_username
                    user["username"] = change_username
                    write_users(users)
                    write_records(update_record)
                    print()
                    print(("╭" + "─" * 34 + "┐").center(len_of_text))
                    print(("│" + "✅ Username updated successfully".center(33) + "│").center(len_of_text))
                    print(("└" + "─" * 34 + "╯").center(len_of_text))
                    break
                elif choose in ['n', 'no']:
                    print()
                    print(("╭" + "─" * 30 + "┐").center(len_of_text))
                    print(("│" + "Username unchanged.".center(30) + "│").center(len_of_text))
                    print(("└" + "─" * 30 + "╯").center(len_of_text))
                    break
                else:
                    print("╭" + "─" * 19 + "┐")
                    print("│" + " ⚠️ Invalid Input!" + " │")
                    print("└" + "─" * 19 + "╯")
            print()
            print(" Press 'p' or 'profile' for return to Profile.")
            print("Type:")
            print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
            while True:
                select = input(": ").lower().strip()
                if select in ["p", "profile"]:
                    print("─" * (len_of_text + 2))
                    return "profile"
                if select in ['b', 'back']:
                    print("─" * (len_of_text + 2))
                    return "back"
                elif select in ['e', 'exit']:
                    print("─" * (len_of_text + 2))
                    exit_()
                else:
                    print("╭" + "─" * 19 + "┐")
                    print("│" + " ⚠️ Invalid Input!" + " │")
                    print("└" + "─" * 19 + "╯")
        elif select in ['2', 'p', 'password', 'change password']:
            print("─" * (len_of_text + 2))
            if user["lockout_time"]:
                elapsed = time.time() - float(user["lockout_time"])
                if elapsed < 30:
                    remaining = int(30 - elapsed)
                    print("╭" + "─" * len_of_text + "┐")
                    print("│" + (f"🔒 Account locked. Try again in {remaining} seconds.").center(len_of_text - 1) + "│")
                    print("└" + "─" * len_of_text + "╯")
                    print("─" * (len_of_text + 2))
                    return
                else:
                    user["lockout_time"] = ''
                    user["failed_attempts"] = '0'
            print(("TO CHANGE YOUR PASSWORD").center(len_of_text))
            while True:
                password: str = hashlib.sha256(pwinput("Current Password: ").encode()).hexdigest()
                try:
                    if user["password"] != password:
                        attempts = int(user['failed_attempts']) + 1
                        user['failed_attempts'] = str(attempts)
                        if attempts >= 5:
                            user["lockout_time"] = str(time.time())
                            raise NameError()
                        raise ValueError()
                    user['failed_attempts'] = '0'
                    user['lockout_time'] = ''
                    write_users(users)
                    break
                except ValueError:
                    print("╭" + "─" * 42 + "┐")
                    print("│" + " ⚠️ Incorrect password. Please try again." + " │")
                    print("└" + "─" * 42 + "╯")
                    write_users(users)
                except NameError:
                    print("╭" + "─" * len_of_text + "┐")
                    print("│" + "🔒 Too many failed attempts. Account locked for 30 seconds.".center(len_of_text - 1) + "│")
                    print("└" + "─" * len_of_text + "╯")
                    write_users(users)
                    return "back to main"
            while True:
                while True:
                    created_password: str = pwinput("New password: ")
                    if hashlib.sha256(created_password.encode()).hexdigest() != user["password"]:
                        pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<> ]{8,}$'
                        matches2 = re.search(pattern, created_password)
                        try:
                            if not matches2:
                                raise ValueError()
                            break
                        except ValueError:
                            print("╭" + "─" * len_of_text + "┐")
                            print("│" + "⚠️ Weak password!".center(len_of_text) + "│")
                            print("│" + " Needs 8+ characters, and".ljust(len_of_text) + "│")
                            print("│" + " Need at least a letter, a number, and a special character.".ljust(len_of_text) + "│")
                            print("└" + "─" * len_of_text + "╯")
                    else:
                        print("╭" + "─" * len_of_text + "┐")
                        print("│" + "⚠️ New username must be different from your current one.".center(len_of_text) + "│")
                        print("└" + "─" * len_of_text + "╯")
                confirm_password: str = pwinput("Confirm new password: ")
                try:
                    if created_password != confirm_password:
                        raise ValueError()
                    break
                except ValueError:
                    print("╭" + "─" * len_of_text + "┐")
                    print("│" + "⚠️ Passwords don't match. Please re-enter your password.".center(len_of_text) + "│")
                    print("└" + "─" * len_of_text + "╯")
            created_password = hashlib.sha256(created_password.encode()).hexdigest()
            while True:
                choose = input("Save Changes? (yes/no):").strip().lower()
                if choose in ['y', 'yes']:
                    user["password"] = created_password
                    write_users(users)
                    print()
                    print(("╭" + "─" * 34 + "┐").center(len_of_text))
                    print(("│" + "✅ Password updated successfully".center(33) + "│").center(len_of_text))
                    print(("└" + "─" * 34 + "╯").center(len_of_text))
                    break
                elif choose in ['n', 'no']:
                    print()
                    print(("╭" + "─" * 30 + "┐").center(len_of_text))
                    print(("│" + "Password change cancelled.".center(30) + "│").center(len_of_text))
                    print(("└" + "─" * 30 + "╯").center(len_of_text))
                    break
                else:
                    print("╭" + "─" * 19 + "┐")
                    print("│" + " ⚠️ Invalid Input!" + " │")
                    print("└" + "─" * 19 + "╯")
            print()
            print(" Press 'p' or 'profile' for return to Profile.")
            print("Type:")
            print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
            while True:
                select = input(": ").lower().strip()
                if select in ["p", "profile"]:
                    print("─" * (len_of_text + 2))
                    return "profile"
                if select in ['b', 'back']:
                    print("─" * (len_of_text + 2))
                    return "back"
                elif select in ['e', 'exit']:
                    print("─" * (len_of_text + 2))
                    exit_()
                else:
                    print("╭" + "─" * 19 + "┐")
                    print("│" + " ⚠️ Invalid Input!" + " │")
                    print("└" + "─" * 19 + "╯")
        elif select in ['b', 'back']:
            print("─" * (len_of_text + 2))
            return "back"
        elif select in ['e', 'exit']:
            print("─" * (len_of_text + 2))
            exit_()
        else:
            print("╭" + "─" * len_of_text + "┐")
            print("│" + "⚠️ Invalid Selection!".center(len_of_text) + "│")
            print("│" + "Enter '1' or 'u' or 'username' or 'change username' to Change Username.".center(len_of_text) + "│")
            print("│" + "Enter '2' or 'p' or 'password' or 'change password' to Change Password.".center(len_of_text) + "│")
            print("└" + "─" * len_of_text + "╯")


def important(username):
    persons = read_records(username)
    if persons:
        imp_result = []
        for person in persons:
            if person['imp'] == '★':
                imp_result.append(person)
        imp_result = sorted_list_wrt_date(imp_result)
        imp_result = output_records_formet(imp_result, 3)
        if imp_result:
            rows = ["s.no.", "date", "name", "direction", "amount"]
            head = "★ IMPORTANT RECORD  "
            measurement = length_list(imp_result, rows, head)
            print_list(measurement, imp_result, rows, head)
            while True:
                print(("╭" + "─" * 55 + "┐").center(len_of_text))
                print((("│" + "Enter S.No. to view Record Details.".center(55)) + "│").center(len_of_text))
                print((("│" + " Press 'p' or 'profile' for return to Profile. ".center(55)) + "│").center(len_of_text))
                print(("└" + "─" * 55 + "╯").center(len_of_text))
                print("Type:")
                print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
                select = input(": ").lower().strip()
                try:
                    if select in ["p", "profile"]:
                        print("─" * (len_of_text + 2))
                        return "profile"
                    if select in ['b', 'back']:
                        print("─" * (len_of_text + 2))
                        return "back"
                    elif select in ['e', 'exit']:
                        print("─" * (len_of_text + 2))
                        exit_()
                    elif 0 < int(select) <= len(imp_result):
                        show_person_details(int(select) - 1, imp_result)
                    else:
                        raise ValueError
                except ValueError:
                    print("╭" + "─" * 19 + "┐")
                    print("│" + " ⚠️ Invalid Input!" + " │")
                    print("└" + "─" * 19 + "╯")
        else:
            return print_empty_imp()
    else:
        return print_empty_imp()


def manage(username):
    gap: int = int((len_of_text - 38) / 3)
    persons = read_records(username)
    if persons:
        while True:
            print("─" * (len_of_text + 2))
            print()
            print(" " * gap + "╭" + "─" * 19 + "┐" + " " * gap + "╭" + "─" * 19 + "┐" + " " * gap)
            print(" " * gap + "│ 1. RENAME PERSON  │" + " " * gap + "│   2. RESET DATA   │" + " " * gap)
            print(" " * gap + "└" + "─" * 19 + "╯" + " " * gap + "└" + "─" * 19 + "╯" + " " * gap)
            print("Type:")
            print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program\n")
            while True:
                select = input("Select: ").strip().lower()
                if select in ['1', 'p', 'rename', 'rename person']:
                    list_appears = 0
                    result_list = []
                    while True:
                        name = input("Person's Name: ").strip().title()
                        if list_appears:
                            try:
                                p_f = 0
                                idx = int(name)
                                for i, person in enumerate(result_list):
                                    if idx == i + 1:
                                        p_f = 1
                                        name = person
                                        break
                                if p_f:
                                    break
                            except ValueError:
                                pass
                        person_found = 0
                        for person in persons:
                            if person["name"] == name:
                                person_found = 1
                                break
                        if person_found:
                            break
                        length = max(17 + len(f"{name}"), 40)
                        print("╭" + "─" * length + "┐")
                        print("│" + f" ⚠️ {name} not found. ".center(length) + "│")
                        print("│" + " Type 'l' or 'list' to see all persons. ".ljust(length) + "│")
                        print("│" + " Type 's' or 'search' to search person. ".ljust(length) + "│")
                        print("│" + " Press Enter to retry.".ljust(length) + "│")
                        print("└" + "─" * length + "╯")
                        selection = input(": ").lower().strip()
                        if selection in ['l', 'list']:
                            result_list = []
                            for person in sorted(persons, key=lambda s: s["name"]):
                                if person["name"] not in result_list:
                                    result_list.append(person["name"])
                            length = len("PERSON'S LIST")
                            for person in result_list:
                                if length < len(person):
                                    length = len(person)
                            length += 6
                            print()
                            print(("╭" + "─" * length + "┐").ljust(len_of_text))
                            print((("│" + "PERSON'S LIST".center(length)).ljust(length) + "│").ljust(len_of_text))
                            for i, person in enumerate(result_list):
                                print((("│" + f" {i+1}. {person}").ljust(length) + " │").ljust(len_of_text))
                            print(("└" + "─" * length + "╯").ljust(len_of_text))
                            print(" Enter S.No. or full name from list.")
                            print()
                            list_appears = 1
                        elif selection in ['s', 'search']:
                            keyword = input("Search Keyword: ").strip().lower()
                            result_list = []
                            for person in sorted(persons, key=lambda s: s["name"]):
                                if re.search(rf'\b{re.escape(keyword)}', person["name"], re.I) and person["name"] not in result_list:
                                    result_list.append(person["name"])
                            if len(result_list):
                                length = len(f"SEARCH RESULT FOR {keyword}")
                                for person in result_list:
                                    if length < len(person):
                                        length = len(person)
                                length += 6
                                print()
                                print(("╭" + "─" * length + "┐").ljust(len_of_text))
                                print((("│" + f"Search Result for '{keyword}'".center(length)).ljust(length) + "│").ljust(len_of_text))
                                for i, person in enumerate(result_list):
                                    print((("│" + f" {i+1}. {person}").ljust(length) + " │").ljust(len_of_text))
                                print(("└" + "─" * length + "╯").ljust(len_of_text))
                                print(" Enter S.No. or full name from list.")
                                print()
                                list_appears = 1
                            else:
                                length = len(f" No match found for '{keyword}'") + 1
                                print()
                                print("╭" + "─" * length + "┐")
                                print("│" + f" No match found for '{keyword}'" + " │")
                                print("└" + "─" * length + "╯")
                                print()
                                list_appears = 0
                    l = len("Person Name: " + name) + 4
                    print("╭" + "─" * l + "┐")
                    print("│" + " Person's Name: " + name + " │")
                    print("└" + "─" * l + "╯")
                    while True:
                        pf = 0
                        new_name = input("Rename to: ").strip().title()
                        if new_name != name:
                            if re.search(r'^([a-z][a-z0-9]* *)+$', new_name, re.I):
                                for person in persons:
                                    if person["name"] == new_name:
                                        pf = 1
                                        break
                                if not pf:
                                    break
                                else:
                                    print("╭" + "─" * 50 + "┐")
                                    print("│" + "⚠️ Person already exists. Try something unique.".center(50) + "│")
                                    print("└" + "─" * 50 + "╯")
                            else:
                                print("╭" + "─" * 50 + "┐")
                                print("│" + "⚠️ Invalid name!".center(50) + "│")
                                print("│" + " Use only letters, numbers, and spaces.".ljust(49) + " │")
                                print("│" + " Each part of the name must start with a letter.".ljust(49) + " │")
                                print("└" + "─" * 50 + "╯")
                        else:
                            print("╭" + "─" * len_of_text + "┐")
                            print("│" + "⚠️ New name must be different from your current one.".center(len_of_text) + "│")
                            print("└" + "─" * len_of_text + "╯")
                    update_persons = read_records()
                    for person in update_persons:
                        if person["username"] == username and person["name"] == name:
                            person["name"] = new_name
                    write_records(update_persons)
                    length = len(f" ✅ Name changed from {name} to {new_name} successfully. ") + 8
                    print()
                    print(("╭" + "─" * length + "┐").center(len_of_text))
                    if length % 2:
                        print(("│" + f" ✅ Name changed from {name} to {new_name} successfully. ".center(length - 1) + "│").center(len_of_text - 2))
                    else:
                        print(("│" + f" ✅ Name changed from {name} to {new_name} successfully. ".center(length - 1) + "│").center(len_of_text))
                    print(("└" + "─" * length + "╯").center(len_of_text))
                    print()
                    print(" Press 'p' or 'profile' for return to Profile.")
                    print("Type:")
                    print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
                    while True:
                        select = input(": ").lower().strip()
                        if select in ["p", "profile"]:
                            print("─" * (len_of_text + 2))
                            return "profile"
                        if select in ['b', 'back']:
                            print("─" * (len_of_text + 2))
                            return "back"
                        elif select in ['e', 'exit']:
                            print("─" * (len_of_text + 2))
                            exit_()
                        else:
                            print("╭" + "─" * 19 + "┐")
                            print("│" + " ⚠️ Invalid Input!" + " │")
                            print("└" + "─" * 19 + "╯")
                elif select in ['2', 'd', 'reset', 'reset data']:
                    while True:
                        delete = input(" ⚠️ Delete all data? This can not be undone. (yes/no): ").strip().lower()
                        if delete == 'yes':
                            record_to_write = []
                            update_persons = read_records()
                            for person in update_persons:
                                if person["username"] != username:
                                    record_to_write.append(person)
                            write_records(record_to_write)
                            print()
                            print(("╭" + "─" * 34 + "┐").center(len_of_text))
                            print(("│" + "✅ Data cleared successfully!".center(33) + "│").center(len_of_text))
                            print(("└" + "─" * 34 + "╯").center(len_of_text))
                            break
                        elif delete == 'no':
                            print()
                            print(("╭" + "─" * 40 + "┐").center(len_of_text))
                            print(("│" + "Reset Cancelled. Your data is safe.".center(40) + "│").center(len_of_text))
                            print(("└" + "─" * 40 + "╯").center(len_of_text))
                            break
                        else:
                            print("╭" + "─" * 19 + "┐")
                            print("│" + " ⚠️ Invalid Input!" + " │")
                            print("└" + "─" * 19 + "╯")
                    print()
                    print(" Press 'p' or 'profile' for return to Profile.")
                    print("Type:")
                    print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
                    while True:
                        select = input(": ").lower().strip()
                        if select in ["p", "profile"]:
                            print("─" * (len_of_text + 2))
                            return "profile"
                        if select in ['b', 'back']:
                            print("─" * (len_of_text + 2))
                            return "back"
                        elif select in ['e', 'exit']:
                            print("─" * (len_of_text + 2))
                            exit_()
                        else:
                            print("╭" + "─" * 19 + "┐")
                            print("│" + " ⚠️ Invalid Input!" + " │")
                            print("└" + "─" * 19 + "╯")
                elif select in ['e', 'exit']:
                    print("─" * (len_of_text + 2))
                    exit_()
                elif select in ['b', 'back']:
                    print("─" * (len_of_text + 2))
                    return "back"
                else:
                    print("╭" + "─" * len_of_text + "┐")
                    print("│" + "⚠️ Invalid Selection!".center(len_of_text) + "│")
                    print("│" + "Enter '1' or 'p' or 'rename' or 'rename person' to Rename Person.".center(len_of_text) + "│")
                    print("│" + "Enter '2' or 'd' or 'reset' or 'reset data' to Reset Data.".center(len_of_text) + "│")
                    print("└" + "─" * len_of_text + "╯")
    else:
        return print_empty_manage()


def stats(username):
    persons = read_records(username)
    if persons:
        givee, takee = 0, 0
        give, take = 0, 0
        lent, repaid = 0, 0
        borrowed, received = 0, 0
        cash_transaction = 0
        online_transaction = 0
        most_active_person = []
        highest_debit = []
        highest_credit = []
        first_transaction = {}
        total_num_of_transactions = 0

        for person in persons:
            person_amount = int(person["amount"])
            total_num_of_transactions += 1
            if person["direction"] == "Debit":
                if not highest_debit:
                    highest_debit.append(person)
                else:
                    high_debit = int(highest_debit[0]["amount"])
                    if high_debit < person_amount:
                        highest_debit = [person]
                    elif high_debit == person_amount:
                        highest_debit.append(person)
                givee += 1
                if take == 0:
                    give += person_amount
                    lent += person_amount
                else:
                    if person_amount <= take:
                        take -= person_amount
                        repaid += person_amount
                    else:
                        give += person_amount - take
                        repaid += take
                        lent += person_amount - take
                        take = 0
            else:
                if not highest_credit:
                    highest_credit.append(person)
                else:
                    high_credit = int(highest_credit[0]["amount"])
                    if high_credit < person_amount:
                        highest_credit = [person]
                    elif high_credit == person_amount:
                        highest_credit.append(person)
                takee += 1
                if give == 0:
                    take += person_amount
                    borrowed += person_amount
                else:
                    if person_amount <= give:
                        give -= person_amount
                        received += person_amount
                    else:
                        take += person_amount - give
                        received += give
                        borrowed += person_amount - give
                        give = 0

            if person["mode"] == "Cash":
                cash_transaction += 1
            else:
                online_transaction += 1

            if not first_transaction:
                first_transaction = person
            else:
                yf, mf, df = first_transaction["date"].split('-')
                yp, mp, dp = person["date"].split('-')
                if date(int(yf), int(mf), int(df)) > date(int(yp), int(mp), int(dp)):
                    first_transaction = person

            if not most_active_person:
                most_active_person.append({"name": person["name"], "transaction": 1})
            else:
                person_found = 0
                for active_person in most_active_person:
                    if person["name"] == active_person["name"]:
                        active_person["transaction"] = int(active_person["transaction"]) + 1
                        person_found = 1
                        break
                if not person_found:
                    most_active_person.append({"name": person["name"], "transaction": 1})

        take = borrowed + received
        give = lent + repaid
        average_debit = int(give / givee) if givee > 0 else 0
        average_credit = int(take / takee) if takee > 0 else 0

        persons_total = []
        for person in persons:
            person_amount = int(person["amount"])
            if persons_total:
                person_found = 0
                for person_total in persons_total:
                    if person_total["name"] == person["name"]:
                        person_found = 1
                        if person["direction"] == "Debit":
                            if person_total["take"] == 0:
                                person_total["give"] += person_amount
                                person_total["lent"] += person_amount
                            else:
                                if person_amount <= person_total["take"]:
                                    person_total["take"] -= person_amount
                                    person_total["repaid"] += person_amount
                                else:
                                    person_total["give"] += person_amount - person_total["take"]
                                    person_total["repaid"] += person_total["take"]
                                    person_total["lent"] += person_amount - person_total["take"]
                                    person_total["take"] = 0
                        if person["direction"] == "Credit":
                            if person_total["give"] == 0:
                                person_total["take"] += person_amount
                                person_total["borrowed"] += person_amount
                            else:
                                if person_amount <= person_total["give"]:
                                    person_total["give"] -= person_amount
                                    person_total["received"] += person_amount
                                else:
                                    person_total["take"] += person_amount - person_total["give"]
                                    person_total["received"] += person_total["give"]
                                    person_total["borrowed"] += person_amount - person_total["give"]
                                    person_total["give"] = 0
                        break
                if not person_found:
                    take_ = 0
                    give_ = 0
                    borrowed_ = 0
                    received_ = 0
                    repaid_ = 0
                    lent_ = 0
                    if person["direction"] == "Debit":
                        give_ += person_amount
                        lent_ += person_amount
                    if person["direction"] == "Credit":
                        take_ += person_amount
                        borrowed_ += person_amount
                    persons_total.append({
                        "name": person["name"], "lent": lent_, "repaid": repaid_,
                        "borrowed": borrowed_, "received": received_, "give": give_, "take": take_
                    })
            else:
                take_ = 0
                give_ = 0
                borrowed_ = 0
                received_ = 0
                repaid_ = 0
                lent_ = 0
                if person["direction"] == "Debit":
                    give_ += person_amount
                    lent_ += person_amount
                if person["direction"] == "Credit":
                    take_ += person_amount
                    borrowed_ += person_amount
                persons_total = [{
                    "name": person["name"], "lent": lent_, "repaid": repaid_,
                    "borrowed": borrowed_, "received": received_, "give": give_, "take": take_
                }]

        most_active = []
        for active_person in most_active_person:
            if not most_active:
                most_active.append(active_person)
            else:
                mostactive = int(most_active[0]["transaction"])
                activeperson = int(active_person["transaction"])
                if mostactive < activeperson:
                    most_active = [active_person]
                elif mostactive == activeperson:
                    most_active.append(active_person)

        top_lender_person = []
        top_borrower_person = []
        settlement = 0
        recovery = 0
        repayment = 0
        for person in persons_total:
            if not top_lender_person:
                top_lender_person.append(person)
            else:
                if int(top_lender_person[0]["lent"]) < int(person["lent"]):
                    top_lender_person = [person]
                elif int(top_lender_person[0]["lent"]) == int(person["lent"]):
                    top_lender_person.append(person)
            if not top_borrower_person:
                top_borrower_person.append(person)
            else:
                if int(top_borrower_person[0]["borrowed"]) < int(person["borrowed"]):
                    top_borrower_person = [person]
                elif int(top_borrower_person[0]["borrowed"]) == int(person["borrowed"]):
                    top_borrower_person.append(person)
            if person["lent"] + person["repaid"] < person["borrowed"] + person["received"]:
                repayment += 1
            elif person["lent"] + person["repaid"] > person["borrowed"] + person["received"]:
                recovery += 1
            else:
                settlement += 1

        total = settlement + repayment + recovery
        settlement_rate = (settlement / total) * 100 if total > 0 else 0
        pending_recovery = (recovery / total) * 100 if total > 0 else 0
        pending_repayment = (repayment / total) * 100 if total > 0 else 0
        total_payment_mode = online_transaction + cash_transaction
        online_percent = (online_transaction / total_payment_mode) * 100 if total_payment_mode > 0 else 0
        cash_percent = (cash_transaction / total_payment_mode) * 100 if total_payment_mode > 0 else 0

        name_date_credit = ", by ".join(f"{record['name']} on {output_date(str(record['date']), 0)}" for record in highest_credit)
        name_date_debit = ", by ".join(f"{record['name']} on {output_date(str(record['date']), 0)}" for record in highest_debit)
        lender_name = ", ".join(f"{lender_p['name']}" for lender_p in top_lender_person)
        borrower_name = ", ".join(f"{borrower_p['name']}" for borrower_p in top_borrower_person)
        active_name = ", ".join(f"{act_p['name']}" for act_p in most_active)
        first_row = len("  Online Transactions:  ")

        length = first_row + max(
            len(f"{output_amount(give)}  "),
            len(f"{output_amount(lent)}  "),
            len(f"{output_amount(take)}  "),
            len(f"{output_amount(borrowed)}  "),
            len(f"{output_amount(repaid)}  "),
            len(f"{output_amount(received)}  "),
            len(f"{cash_percent:.2f} %  ({cash_transaction} of {cash_transaction+online_transaction})  "),
            len(f"{online_percent:.2f} %  ({online_transaction} of {cash_transaction+online_transaction})  "),
            len(f"{total_num_of_transactions}  "),
            len(f"{output_amount(int(first_transaction['amount']))} to {first_transaction['name']} on {output_date(first_transaction['date'], 0)}  "),
            len(f"{pending_repayment:.2f} %  "),
            len(f"{pending_recovery:.2f} %  "),
            len(f"{settlement_rate:.2f} %  "),
            len(f"{output_amount(int(highest_credit[0]['amount']))} by {name_date_credit}  "),
            len(f"{output_amount(int(highest_debit[0]['amount']))} by {name_date_debit}  "),
            len(f"{lender_name} with {output_amount(int(top_lender_person[0]['lent']))}  "),
            len(f"{borrower_name} with {output_amount(int(top_borrower_person[0]['borrowed']))}  "),
            len(f"{active_name} with {int(most_active[0]['transaction'])} transaction  "),
        )
        if give > take:
            length = max(length, first_row + len(f"  ◈  You are owed {output_amount(int(give - take))}.  "))
        elif take > give:
            length = max(length, first_row + len(f"  ◈  You owe {output_amount(int(take-give))} overall.  "))
        else:
            length = max(length, first_row + len("  ✓  You're all settled up.  "))

        print("╭────────────────┐".center(length + 2).center(len_of_text))
        if length % 2:
            print(("╭" + "─" * (int((length - 18) / 2) + 1) + "┤ ALL-TIME STATS ├" + "─" * (int((length - 18) / 2)) + "┐").center(len_of_text))
        else:
            print(("╭" + "─" * (int((length - 18) / 2)) + "┤ ALL-TIME STATS ├" + "─" * (int((length - 18) / 2)) + "┐").center(len_of_text))
        print(("│" + "└────────────────╯".center(length) + "│").center(len_of_text))
        print(("│" + "   ╭────────┐".ljust(length) + "│").center(len_of_text))
        print(("├" + ("───┤ TOTALS ├" + "─" * (length - 13)).ljust(length) + "┤").center(len_of_text))
        print(("│" + "   └────────╯".ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Total Debit:".ljust(first_row) + f"{output_amount(give)}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("      Lent:".ljust(first_row) + f"{output_amount(lent)}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("      Repaid:".ljust(first_row) + f"{output_amount(repaid)}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Total Credit:".ljust(first_row) + f"{output_amount(take)}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("      Borrowed:".ljust(first_row) + f"{output_amount(borrowed)}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("      Received:".ljust(first_row) + f"{output_amount(received)}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + "   ╭──────────────┐".ljust(length) + "│").center(len_of_text))
        print(("├" + ("───┤ PAYMENT MODE ├" + "─" * (length - 19)).ljust(length) + "┤").center(len_of_text))
        print(("│" + "   └──────────────╯".ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Online Transactions:".ljust(first_row) + f"{online_percent:.2f} %  ({online_transaction} of {cash_transaction+online_transaction})  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Cash Transactions:".ljust(first_row) + f"{cash_percent:.2f} %  ({cash_transaction} of {cash_transaction+online_transaction})  ").ljust(length) + "│").center(len_of_text))
        print(("│" + "   ╭──────────┐".ljust(length) + "│").center(len_of_text))
        print(("├" + ("───┤ AVERAGES ├" + "─" * (length - 15)).ljust(length) + "┤").center(len_of_text))
        print(("│" + "   └──────────╯".ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Average Credit:".ljust(first_row) + f"{output_amount(average_credit)}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Average Debit:".ljust(first_row) + f"{output_amount(average_debit)}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + "   ╭──────────────┐".ljust(length) + "│").center(len_of_text))
        print(("├" + ("───┤ TOP CONTACTS ├" + "─" * (length - 19)).ljust(length) + "┤").center(len_of_text))
        print(("│" + "   └──────────────╯".ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Top Lender:".ljust(first_row) + f"{lender_name} with {output_amount(int(top_lender_person[0]['lent']))}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Top Borrower:".ljust(first_row) + f"{borrower_name} with {output_amount(int(top_borrower_person[0]['borrowed']))}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Most Active Contact:".ljust(first_row) + f"{active_name} with {int(most_active[0]['transaction'])} transaction  ").ljust(length) + "│").center(len_of_text))
        print(("│" + "   ╭───────────────┐".ljust(length) + "│").center(len_of_text))
        print(("├" + ("───┤ PEAK ACTIVITY ├" + "─" * (length - 20)).ljust(length) + "┤").center(len_of_text))
        print(("│" + "   └───────────────╯".ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Highest Credit:".ljust(first_row) + f"{output_amount(int(highest_credit[0]['amount']))} by {name_date_credit}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Highest Debit:".ljust(first_row) + f"{output_amount(int(highest_debit[0]['amount']))} by {name_date_debit}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + "   ╭──────────────────┐".ljust(length) + "│").center(len_of_text))
        print(("├" + ("───┤ BALANCE OVERVIEW ├" + "─" * (length - 23)).ljust(length) + "┤").center(len_of_text))
        print(("│" + "   └──────────────────╯".ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Settlement Rate:".ljust(first_row) + f"{settlement_rate:.2f} %  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Contacts Owing You:".ljust(first_row) + f"{pending_recovery:.2f} %  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Contacts You Owe:".ljust(first_row) + f"{pending_repayment:.2f} %  ").ljust(length) + "│").center(len_of_text))
        print(("│" + "   ╭─────────┐".ljust(length) + "│").center(len_of_text))
        print(("├" + ("───┤ HISTORY ├" + "─" * (length - 14)).ljust(length) + "┤").center(len_of_text))
        print(("│" + "   └─────────╯".ljust(length) + "│").center(len_of_text))
        if first_transaction["direction"] == "Credit":
            print(("│" + ("  First Transaction:".ljust(first_row) + f"{output_amount(int(first_transaction['amount']))} by {first_transaction['name']} on {output_date(first_transaction['date'], 0)}  ").ljust(length) + "│").center(len_of_text))
        else:
            print(("│" + ("  First Transaction:".ljust(first_row) + f"{output_amount(int(first_transaction['amount']))} to {first_transaction['name']} on {output_date(first_transaction['date'], 0)}  ").ljust(length) + "│").center(len_of_text))
        print(("│" + ("  Total Transactions:".ljust(first_row) + f"{total_num_of_transactions}  ").ljust(length) + "│").center(len_of_text))
        print(("├" + "─" * length + "┤").center(len_of_text))
        if give > take:
            print(("│" + f"  ◈  You are owed {output_amount(int(give - take))}.  ".center(length) + "│").center(len_of_text))
        elif take > give:
            print(("│" + f"  ◈  You owe {output_amount(int(take-give))} overall.  ".center(length) + "│").center(len_of_text))
        else:
            print(("│" + "  ✓  You're all settled up.  ".center(length) + "│").center(len_of_text))
        print(("└" + "─" * length + "╯").center(len_of_text))
        print()
        print(" Press 'p' or 'profile' for return to Profile.")
        print("Type:")
        print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
        while True:
            select = input(": ").lower().strip()
            if select in ["p", "profile"]:
                print("─" * (len_of_text + 2))
                return "profile"
            if select in ['b', 'back']:
                print("─" * (len_of_text + 2))
                return "back"
            elif select in ['e', 'exit']:
                print("─" * (len_of_text + 2))
                exit_()
            else:
                print("╭" + "─" * 19 + "┐")
                print("│" + " ⚠️ Invalid Input!" + " │")
                print("└" + "─" * 19 + "╯")
    else:
        return print_empty_stats()


def logout():
    while True:
        select = input("  Are you sure you want to logout? (yes/no): ")
        if select in ["yes"]:
            print()
            print(("╭" + "─" * 34 + "┐").center(len_of_text))
            print(("│" + "✅ Logged out successfully".center(33) + "│").center(len_of_text))
            print(("└" + "─" * 34 + "╯").center(len_of_text))
            return "back to main"
        if select in ["no"]:
            print()
            print(("╭" + "─" * 30 + "┐").center(len_of_text))
            print(("│" + "Logout cancelled.".center(30) + "│").center(len_of_text))
            print(("└" + "─" * 30 + "╯").center(len_of_text))
            print()
            print(" Press 'p' or 'profile' for return to Profile.")
            print("Type:")
            print("    back - previous (home)" + " " * (len_of_text - 45) + "exit - quit program")
            while True:
                select = input(": ").lower().strip()
                if select in ["p", "profile"]:
                    print("─" * (len_of_text + 2))
                    return "profile"
                if select in ['b', 'back']:
                    print("─" * (len_of_text + 2))
                    return "back"
                elif select in ['e', 'exit']:
                    print("─" * (len_of_text + 2))
                    exit_()
                else:
                    print("╭" + "─" * 19 + "┐")
                    print("│" + " ⚠️ Invalid Input!" + " │")
                    print("└" + "─" * 19 + "╯")
        else:
            print("╭" + "─" * 19 + "┐")
            print("│" + " ⚠️ Invalid Input!" + " │")
            print("└" + "─" * 19 + "╯")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("╭" + "─" * len_of_text + "┐")
        print("│" + "Program interrupted. Thank you for using LedgerMate. Goodbye!".center(len_of_text) + "│")
        print("└" + "─" * len_of_text + "╯")