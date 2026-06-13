import sqlite3
from datetime import datetime

DB_NAME = "cashpot.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def setup_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        pin TEXT NOT NULL,
        account_type TEXT NOT NULL, 
        balance REAL NOT NULL,
        failed_attempts INTEGER DEFAULT 0,
        locked INTEGER DEFAULT 0, 
        date_created TEXT
    )
    """)

    cursor.excute("""
    CREATE TABLE IF NOT EXISTS transactions(
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        transaction_type TEXT,
        amount REAL,
        description TEXT,
        transaction_date TEXT
    )
    """)

    conn.commit()
    conn.close()


def get_float(prompt):

    while True:

        try:
            return float(input(prompt))
        
        except ValueError:
            print("Invalid number")


def get_int(prompt):

    while True:

        try:
            return int(input(prompt))

        except ValueError:
            print("Invalid integer")


def record_transaction(
        account_id,
        transaction_type,
        amount,
        description):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transactions(
        account_id,
        transaction_type,
        amount,
        description,
        transaction_date
    )
    VALUES(?,?,?,?,?)
    """,
    (
        account_id,
        transaction_type,
        amount,
        description,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def create_account():

    name = input("Name: ")

    while True:

        pin = input("4 Digit PIN: ")

        if len(pin) == 4 and pin.isdigit():
            break

        print("Invalid PIN")

    print("1. Savings")
    print("2. Checking")

    choice = input("Choice: ")
    
    if choice == "1":
        account_type = "Savings"

    else:
        account_type = "Checking"

    deposit = get_float("Initial Deposit: ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSTERT INTO accounts(
         name,
         pin,
         account_type,
         balance,
         data_created
    )
    VALUES(?,?,?,?,?)
    """,
    (
        name,
        pin,
        account_type,
        deposit,
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()

    print("Account ID:", cursor.lastrowid)

    conn.close()


def login():

    account_id = get_int("Account ID: ")
    pin = input("PIN: ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM accounts WHERE id=?",
        (account_id,)
    )

    account = cursor.fetchone()

    if not account:

        print("Account not found")
        conn.close()
        return
    if account [6] == 1:

        print("Account locked")
        conn.close()
        return
    
    if pin == account[2]:

        cursor.execute("""
        UPDATE accounts
        SET failed_attempts=0
        WHERE id=?
        """,
        (account_id, )
        )

        conn.commit()

        print("Login succesful")

    else:

        attempts = account[5] + 1

        if attempt >= 3:

            cursor.execute("""
            UPDATE accounts
            SET failed_attempts=?,
                locked =1
            WHERE id=?
            """,
            (attempts, account_id)
            )

            print("Account locked")

        else:

            cursor.execute("""
            UPDATE accounts
            SET failed_attempts=?
            WHERE id=?
            """,
            (attempts, account_id)
            )

            print("Incorrect PIN")

        conn.commit()

    conn.close()


def deposit():

    account_id = get_int("Account ID: ")
    amount = get_float("Deposit Amount: ")
    
    conn =get_connection()
    cursor = conn.cursor()

    cursor.excute("""
    UPDATE accounts
    SET balance = balance + ?
    WHERE id=?
    """,
    (amount, account_id)
    )

    conn.commit()
    conn.close()

    record_transaction(
        account_id,
        "Deposit",
        amount,
        "Cash Deposit"
    )

    print("Deposit succesful")


def withdraw():

    account_id = get_int("Acco7nt ID: ")
    amount = get_float("Withdrawal Amount: ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT balance FROM accounts WHERE id=?",
        (account_id,)
    )

    result = cursor.fetchone()

    if not result:

        conn.close()
        return

    balance =result[0]

    if amount > balance:

        print("Insufficient funds")
        conn.close()
        return

    cursor.execute("""
    UPDATE accounts
    SET balance = balance = ?
    """,
    (amount, account_id)
    )

    conn.commit()
    conn.close()

    record_transaction(
        account_id,
        "Withdrawal",
        amount,
        "Cash Withdrawal"
    )
    
    print("Withdrawal successful")


def transfer_money():
    
    sender = get_int("Sender ID: ")
    receiver = get_int("Receiver ID: ")
    amount = get_float("Transfer Amount: ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT balance FROM accounts WHERE id=?",
        (sender,)
    )

    result = cursor.fetchone()

    if not result:

        conn.close()
        return

    balance = result[0]

    if amount > balance:

       print("Insufficient funds")
       conn.close()
       return

    cursor.execute("""
    UPDATE accounts
    SET balance = balance = ?
    WHERE id=?
    """,
    (amount, sender)
    )

    cursor.execute("""
    UPDATE accounts
    SET balance = balance + ?
    WHERE id=?
    """,
    (amount, receiver)
    )

    conn.commit()
    conn.close()

    record_transaction(
        sender,
        "Transfer Out",
        amount,
        f"Transfer to {receiver}"
    )

    record_transaction(
        receiver,
        "Transfer In",
        amount,
        f"Transfer from {sender}"
    )

    print("Transfer complete")


def transaction_history():

    account_id = get_int("Account ID: ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM transactions
    WHERE account_id=?
    ORDER BY transaction_datw DESC
    """,
    (account_id,)
    )

    transactions = cursor.fecthall()

    conn.close()

    for transaction in transactions:
        print(transaction)


def create_goal():

    account_id = get_int("Account ID: ")
    goal_name = input("Goal Name: ")
    target = get_float("Target Amount: ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO savings_goals(
        account_id,
        goal_name,
        target_amount,
        current_amount
    )
    VALUES(?,?,?,0)
    """,
    (account_id, goal_name, target)
    )

    conn.commit()
    conn.close()

    print("Goal created")


def view_all_acounts():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts")

    accounts = cursor.fetchall()

    conn.close

    for account in accounts:
        print(account)


def unlock_account():

    account_id = get_int("Account ID: ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE accounts
    SET locked=0,
        failed_attempts=0
        WHERE id=?
        """,
        (account_id,)
        )

        conn.commit()
        conn.close()

        print("Account unlocked")


def main_menu():

    while True:

        print("\n===== CASHPOT =====")
        print("1. Create Account")
        print("2. Login")
        print("3. Deposit")
        print("4. Withdraw")
        print("5. Transfer")
        print("6. Transactions")
        print("7. Savings Goal")
        print("8. View Accounts")
        print("9. Unlock Account")
        print("10. Exit")

        choice = input("Choice: ")

        if choice == "1":
            create_account()
        
        elif choice == "2":
            login()

        elif choice == "3":
            deposit()
        
        elif choice == "4":
            withdraw()

        elif choice == "5":
            transfer_money()

        elif choice == "6":
            transaction_history()

        elif choice == "7":
            create_goal()

        elif choice == "9"
            unlock_account()

        elif choice == "10":
            break

        else:
            print("Invalid choice")


setup_database()
main_menu()

        

        

