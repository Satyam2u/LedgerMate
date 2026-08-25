# LEDGERMATE

#### Video Demo: https://youtu.be/p-r6kwY5CAI

#### Description:

LedgerMate is a command-line program for keeping track of informal money
transactions between the user and the people around them — the kind of
"can you send it back whenever" loans that are easy to make and easy to
lose track of. Instead of relying on memory or a scattered set of chat
messages, LedgerMate keeps every transaction in one place and can tell
you, for any person, exactly where things stand: whether you owe them,
whether they owe you, or whether you're settled up.

I built this as my CS50P final project. I only used what the course
covers — functions, loops, conditionals, file I/O, regular expressions,
exceptions, and `pytest` — plus one small external package (`pwinput`)
to hide password input on the terminal, since that isn't something
CS50P teaches directly.

## How it works

When you run the program you land on a start screen with three options:
sign up, sign in, or exit. Signing up asks for a username and a
password; signing in asks for the same and checks them against what's
stored. Once signed in, you reach the main menu, which is where all of
the actual ledger features live: recording a transaction, viewing your
history, looking at your balance with a specific person, searching, and
managing your profile.

Every transaction is either a **Credit** or a **Debit**, from the
user's point of view:

- **Debit** — money the user handed out. This covers both lending money
  to someone and paying back money the user had previously borrowed.
- **Credit** — money the user took in. This covers both borrowing money
  from someone and being repaid for money the user had lent.

This two-way split keeps the data model simple while still being able
to answer the question that actually matters: for any person, is the
running total of Debits bigger than the running total of Credits, or
the other way around? The difference between the two is the net
balance, and its sign tells you who owes whom.

## Major features

- **Accounts.** Multiple people can use the same copy of LedgerMate,
  each with their own username and password. Passwords are never
  stored in plain text — they're hashed with `hashlib.sha256` before
  being written to disk, and login checks compare hashes, not raw
  text. After five wrong password attempts in a row, the account is
  locked for five minutes, and the lockout is stored on disk so it
  survives closing and reopening the program.
- **Record.** Add a new transaction: direction (credit/debit), the
  other person's name, an amount, a payment mode (online/cash), an
  optional note, and a date (either "today" or a specific past date).
  The program shows a short summary before saving so you can back out
  if something looks wrong.
- **History.** Lists every transaction the signed-in user has recorded,
  most recent first.
- **Details.** Pick a person from a list of everyone you've recorded a
  transaction with, and see every transaction with them plus the net
  balance — who owes whom, and how much.
- **Search.** Look up transactions by typing a keyword that's matched
  against the person's name or the note.
- **Profile.** View your username, change your username, or change
  your password. Both changes require re-entering your current
  password first.

## Files

- **`project.py`** — the entire program. `main()` shows the welcome
  screen and routes between signing up, signing in, and exiting.
  Everything else is broken into small, single-purpose functions
  rather than one giant block of code — validation functions,
  file-reading/writing functions, and the functions behind each menu
  option are all kept separate so each one is easy to follow (and
  easy to test).
- **`test_project.py`** — `pytest` tests for the pure logic functions:
  username/password/amount validation, date parsing, balance
  calculation, and password hashing.
- **`requirements.txt`** — lists `pwinput`, the only third-party
  package the project depends on.
- **`users.csv`** / **`records.csv`** — created automatically the
  first time the program needs them. They aren't included in the
  submission so the project starts from a clean state.

## Important functions

- `validate_username` / `validate_password` / `validate_amount` /
  `parse_date` — each one checks a single piece of user input and
  either returns a clean value or signals that the input was invalid
  (`validate_amount` and `parse_date` raise `ValueError` with a
  message that gets shown back to the user). Keeping these separate
  from `input()` calls is what makes them testable without having to
  fake terminal input.
- `hash_password` / `verify_password` — wrap `hashlib.sha256` so the
  rest of the program never has to think about raw password bytes.
- `calculate_balance` — takes a list of a person's transactions and
  returns a single signed integer: positive means they owe the user,
  negative means the user owes them.
- `load_users` / `save_users` / `load_records` / `append_record` —
  the only functions that touch the CSV files directly, so the file
  format only has to be dealt with in one place.

## Design decisions

**Why CSV instead of a database.** CS50P doesn't require SQL for this
project, and a plain CSV file is easy to inspect, easy to reason
about, and enough for a single-user-at-a-time terminal app. Each row
in `records.csv` is one transaction; each row in `users.csv` is one
account.

**Why a signed net balance instead of separate "lent/repaid/borrowed"
totals.** An earlier version of this project tried to track lent,
repaid, borrowed, and received as four separate running totals, and
it made the balance logic much harder to get right without actually
changing the final answer — the net balance always works out to
total Debits minus total Credits no matter how you slice it up. This
version keeps the simpler calculation and shows the full transaction
list underneath it, so nothing is lost — you can still see the whole
history line by line.

**Why the password lockout is stored on disk.** Keeping the failed
attempt count only in memory would mean restarting the program resets
it, which defeats the point of a lockout.

**Why `pwinput` instead of plain `input()`.** Typing a password in
plain view on screen isn't great practice, even for a local CLI tool.
`pwinput` masks it with asterisks while it's typed.

## Installing and running

```bash
pip install -r requirements.txt
python project.py
```

## Running the tests

```bash
pip install pytest
pytest
```