import random
import pickle
import mysql.connector

# Connect to the database
conn = mysql.connector.connect(
    host='localhost',      # Your MySQL server host
    user='root',  # Your MySQL username
    password='root',  # Your MySQL password
)

cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS crypto_backend")
cursor.execute("USE crypto_backend")

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    full_name VARCHAR(255),
    phone_number VARCHAR(15),
    email VARCHAR(255),
    transaction_method VARCHAR(50),
    transaction_details VARCHAR(255),
    portfolio VARCHAR(500),
    crypto_count INT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    crypto_name VARCHAR(255),
    transaction_type VARCHAR(10),
    amount FLOAT,
    price FLOAT(10, 2),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    complaint_text VARCHAR(1000),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS inbox (
    inbox_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    response_text VARCHAR(1000),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS cryptos (
    crypto_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    price FLOAT(10, 2)
)
''')

# Sample top 50 cryptos (add more as needed)
top_cryptos = [
    ('Bitcoin', 30000),
    ('Ethereum', 2000),
    ('Ripple', 0.5),
    ('Litecoin', 150),
    ('Cardano', 1.2),
]

# Insert sample cryptos if the table is empty
cursor.executemany('INSERT IGNORE INTO cryptos (name, price) VALUES (%s, %s)', top_cryptos)
conn.commit()

def main_menu():
    print("1. Login as User")
    print("2. Create New User")
    print("3. Login as Admin")
    print("4. exit")
    choice = input("Choose an option: ")
    if choice == '1':
        print("******************************************************************************************************************")
        user_login()
    elif choice == '2':
        print("******************************************************************************************************************")
        create_user()
    elif choice == '3':
        print("******************************************************************************************************************")
        admin_login()
    elif choice == '4':
        exit()
    else:
        print("Invalid option. Please try again.")
        print("******************************************************************************************************************")
        main_menu()
def file_complaint(user_id):
    complaint = input("Enter your complaint: ")
    cursor.execute("INSERT INTO complaints (user_id, complaint_text) VALUES (%s, %s)", (user_id, complaint))
    conn.commit()
    print("Complaint filed successfully.")
    print("******************************************************************************************************************")

def user_login():
    login_input = input("Enter username, phone number, or email: ")
    password = input("Enter password: ")
    
    # Query to find the user based on the input (username, phone number, or email)
    cursor.execute('''
        SELECT * FROM users WHERE (username=%s OR phone_number=%s OR email=%s) AND password=%s
    ''', (login_input, login_input, login_input, password))
    
    user = cursor.fetchone()
    
    if user:
        print("******************************************************************************************************************")
        print("Welcome " + user[1] + "!")  # Display the username stored in the database
        check_inbox(user)
        user_menu(user)
    else:
        print("Invalid credentials.")
        print("******************************************************************************************************************")
        main_menu()

def create_user():
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    full_name = input("Enter your full name: ")
    phone_number = input("Enter your phone number: ")
    email = input("Enter your email address: ")
    
    # Choose transaction method
    print("Choose a transaction method:")
    print("1. UPI")
    print("2. Bank Transfer")
    method_choice = input("Enter 1 or 2: ")
    
    if method_choice == '1':
        transaction_method = 'UPI'
        upi_id = input("Enter your UPI ID: ")
        transaction_details = upi_id
    elif method_choice == '2':
        transaction_method = 'Bank Transfer'
        bank_account = input("Enter your bank account number: ")
        ifsc_code = input("Enter your bank IFSC code: ")
        transaction_details = "Account: ",bank_account," IFSC: ",ifsc_code
    else:
        print("Invalid choice. Please try again.")
        create_user()  # Restart the registration if invalid choice
        return
    
    # Insert the new user into the database
    cursor.execute('''
        INSERT INTO users (username, password, full_name, phone_number, email, transaction_method, transaction_details, portfolio, crypto_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, '[]', 0)
    ''', (username, password, full_name, phone_number, email, transaction_method, transaction_details))
    
    conn.commit()
    print("User created successfully!")
    print("******************************************************************************************************************")
    main_menu()

def file():
    # Open the file to read existing price history
    with open("C:\\Users\\Imran\\Desktop\\price history\\Price__History.dat", "rb") as file:
        price_dict = pickle.load(file)
    
    # Fetching crypto data from the database
    cursor.execute("SELECT name, price FROM cryptos")
    cryptos = cursor.fetchall()

    # Updating the price history for each crypto
    for crypto in cryptos:
        crypto_name = crypto[0]
        price = float(crypto[1])
        
        # If crypto_name is not in the dictionary, initialize it with an empty list
        if crypto_name not in price_dict:
            price_dict[crypto_name] = []

        # Append the new price to the existing list
        price_dict[crypto_name].append(price)
        if len(price_dict[crypto_name])> 7 :
            price_dict[crypto_name].pop(0)

    # Save the updated price history back to the file
    with open("C:\\Users\\Imran\\Desktop\\price history\\Price__History.dat", "wb") as file:
        pickle.dump(price_dict, file)
                        
def update_crypto_prices():
    cursor.execute("SELECT crypto_id, price FROM cryptos")
    cryptos = cursor.fetchall()

    for crypto in cryptos:
        crypto_id = crypto[0]
        old_price = float(crypto[1])
        # Calculate the new price within ±5%
        price_change = old_price * random.uniform(-0.05, 0.05)  # Random change between -5% and +5%
        new_price = round(old_price + price_change, 2)

        # Update the price in the database
        cursor.execute("UPDATE cryptos SET price=%s WHERE crypto_id=%s", (new_price, crypto_id))
    
    conn.commit()

def user_menu(user):
    user_id = user[0]
    while True:
        print("\nUser Menu:")
        print("1. Discover New Crypto")
        print("2. Buy Crypto")
        print("3. Sell Crypto")
        print("4. View Portfolio")
        print("5. Register a Complaint")
        print("6. Inbox")
        print("7. View Transaction History")
        print("8. Edit Profile") 
        print("9. Logout")
        choice = input("Choose an option: ")
        
        if choice == '1':
            print("******************************************************************************************************************")
            discover_new_crypto()
        elif choice == '2':
            print("******************************************************************************************************************")
            buy_crypto(user_id)
        elif choice == '3':
            print("******************************************************************************************************************")
            sell_crypto(user_id)
        elif choice == '4':
            print("******************************************************************************************************************")
            view_portfolio(user_id)
        elif choice == '5':
            print("******************************************************************************************************************")
            file_complaint(user_id)
        elif choice == '6':
            print("******************************************************************************************************************")
            view_inbox(user_id)
        elif choice == '7':
            print("******************************************************************************************************************")
            view_transaction_history(user_id)
        elif choice == '8':
            print("******************************************************************************************************************")
            edit_profile(user_id)  
        elif choice == '9':
            print("Logging out...")
            print("******************************************************************************************************************")
            main_menu()
        else:
            print("Invalid option. Please try again.")


def view_portfolio(user_id):
    # Retrieve the user's portfolio
    cursor.execute("SELECT portfolio FROM users WHERE user_id=%s", (user_id,))
    portfolio = cursor.fetchone()[0]

    if portfolio == '[]':
        print("Your portfolio is empty.")
        print("******************************************************************************************************************")
        return

    portfolio_list = eval(portfolio)  # Convert portfolio from string to list

    # Ask if the user wants to filter and sort the portfolio
    filter_choice = input("Do you want to filter for a specific crypto? (y/n): ")
    
    if filter_choice.lower() == 'y':
        crypto_name = input("Enter the name of the crypto to filter by: ")
        
        # Filter the portfolio for the specific crypto
        filtered_portfolio = [crypto for crypto in portfolio_list if crypto_name in crypto]
        
        if not filtered_portfolio:
            print("No holdings found for ",crypto_name,".")
            print("******************************************************************************************************************")
            return
        
        sort_choice = input("Do you want to sort by bought price or current price? (b/c): ")
        
        if sort_choice.lower() == 'b':
            # Sort by bought price using a function
            sorted_portfolio = sort_by_bought_price(filtered_portfolio)
        elif sort_choice.lower() == 'c':
            # Sort by current price using a function
            sorted_portfolio = sort_by_current_price(filtered_portfolio)
        
        # Display the filtered and sorted portfolio
        print("\nFiltered Portfolio for ",crypto_name,":")
        for crypto_data in sorted_portfolio:
            display_crypto_info(crypto_data)
    else:
        # View the entire portfolio
        print("\nYour Full Portfolio:")
        for crypto_data in portfolio_list:
            display_crypto_info(crypto_data)
    
    print("******************************************************************************************************************")

def check_inbox(user):
    user_id = user[0]
    cursor.execute("SELECT COUNT(response_text) FROM inbox WHERE user_id = %s",(user_id,))
    # Fetch the result from the query
    result = cursor.fetchone()
    # Check if there are unread messages
    if result[0] > 0:
        print("You have a message, please view your inbox.")
        
        
def display_crypto_info(crypto_data):
    for crypto_name, details in crypto_data.items():
        amount_bought = details['amount']
        bought_price = details['bought_price']
        
        # Get the current price of the crypto
        cursor.execute("SELECT price FROM cryptos WHERE name=%s", (crypto_name,))
        current_price = float(cursor.fetchone()[0])

        # Calculate total value, profit/loss, and percentage difference
        current_value = current_price * amount_bought
        total_bought_value = bought_price * amount_bought
        profit_loss = current_value - total_bought_value
        percentage_diff = (profit_loss / total_bought_value) * 100

        # Determine profit or loss
        status = "Profit" if profit_loss > 0 else "Loss"

        # Display the information
        print()
        print("Crypto: ",crypto_name)
        print("Amount: ",amount_bought)
        print("Bought Price: $",bought_price)
        print("Current Price: $",current_price)
        print("Current Value: $",round(current_value, 2))
        print(status," : ",round(profit_loss, 2)," ( ",round(percentage_diff, 2),"%)")
        print()

def sort_by_bought_price(portfolio):
    
    return sorted(portfolio, key=get_bought_price)

def get_bought_price(crypto_data):
    
    for details in crypto_data.values():
        return details['bought_price']

def sort_by_current_price(portfolio):
    
    # Fetch the current price for each crypto and sort
    for crypto_data in portfolio:
        for crypto_name in crypto_data.keys():
            cursor.execute("SELECT price FROM cryptos WHERE name=%s", (crypto_name,))
            current_price = float(cursor.fetchone()[0])
            crypto_data[crypto_name]['current_price'] = current_price
    return sorted(portfolio, key=get_current_price)

def get_current_price(crypto_data):
    
    for details in crypto_data.values():
        return details['current_price']

def buy_crypto(user_id):
    crypto_name = input("Enter the name of the crypto you want to buy: ")
    amount = float(input("Enter the amount you want to buy: "))
    
    cursor.execute("SELECT price FROM cryptos WHERE name=%s", (crypto_name,))
    crypto = cursor.fetchone()
    
    if crypto:
        price = float(crypto[0])
        total_cost = price * amount
        
        cursor.execute("SELECT portfolio FROM users WHERE user_id=%s", (user_id,))
        portfolio = cursor.fetchone()[0]

        if portfolio == '[]':
            portfolio_list = []
        else:
            portfolio_list = eval(portfolio)  # Convert portfolio from string to list
        
        # Check if the crypto already exists in the portfolio
        found = False
        for item in portfolio_list:
            if crypto_name in item:
                item[crypto_name]['amount'] += amount
                found = True
                break
        
        if not found:
            # Add the crypto with the bought price to the portfolio
            portfolio_list.append({crypto_name: {'amount': amount, 'bought_price': price}})

        # Save the updated portfolio back to the database
        buy = "bought"
        cursor.execute("INSERT INTO transactions (user_id, crypto_name, transaction_type, amount, price) VALUES (%s, %s, %s, %s, %s)", (user_id, crypto_name, buy, amount, total_cost))
        cursor.execute("UPDATE users SET portfolio=%s, crypto_count=crypto_count + %s WHERE user_id=%s", (str(portfolio_list), amount, user_id))
        conn.commit()
        print("Bought ",amount," of ",crypto_name," for $",round(total_cost, 2),".")
    else:
        print("Crypto not found.")
    print("******************************************************************************************************************")

def sell_crypto(user_id):
    # Retrieve the user's portfolio
    cursor.execute("SELECT portfolio FROM users WHERE user_id=%s", (user_id,))
    portfolio = cursor.fetchone()[0]

    if portfolio == '[]':
        print("Your portfolio is empty.")
        print("******************************************************************************************************************")
        return

    portfolio_list = eval(portfolio)  # Convert portfolio from string to list

    # Ask the user which crypto they want to sell
    crypto_name = input("Enter the name of the cryptocurrency you want to sell: ")

    # Check if the user holds the specified cryptocurrency
    crypto_found = False
    for crypto_data in portfolio_list:
        if crypto_name in crypto_data:
            crypto_found = True
            amount_owned = crypto_data[crypto_name]['amount']
            bought_price = crypto_data[crypto_name]['bought_price']
            break

    if not crypto_found:
        print("You do not own any ",crypto_name,".")
        print("******************************************************************************************************************")
        return
   
    # Ask if they want to sell all or a specific amount
    a="You own "+str(amount_owned)+" of "+crypto_name+". Do you want to sell all of it? (y/n): "
    sell_choice = input(a)
    
    if sell_choice.lower() == 'y':
        amount_to_sell = amount_owned  # Selling all the amount
    else:
        while True:
            try:
                amount_to_sell = float(input("How much do you want to sell? "))
                if amount_to_sell <= 0:
                    print("Amount must be greater than zero.")
                elif amount_to_sell > amount_owned:
                    print("You only own ",amount_owned," of ",crypto_name,".Please enter a valid amount.")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    # Fetch the current price of the cryptocurrency
    cursor.execute("SELECT price FROM cryptos WHERE name=%s", (crypto_name,))
    current_price = float(cursor.fetchone()[0])

    # Calculate the profit/loss from the sale
    total_sold_value = amount_to_sell * current_price
    total_bought_value = amount_to_sell * bought_price
    profit_loss = total_sold_value - total_bought_value

    # Update the portfolio
    for crypto_data in portfolio_list:
        if crypto_name in crypto_data:
            if amount_to_sell == amount_owned:
                portfolio_list.remove(crypto_data)  # Remove the entire crypto from the portfolio
            else:
                crypto_data[crypto_name]['amount'] -= amount_to_sell  # Subtract the sold amount
            break

    # Update the portfolio in the database
    cursor.execute("UPDATE users SET portfolio=%s WHERE user_id=%s", (str(portfolio_list), user_id))
    conn.commit()

    # Display the sale information
    print("\nYou sold ",amount_to_sell," of ",crypto_name," at $",current_price," per unit.")
    print("Total sold value: $",round(total_sold_value, 2))
    if profit_loss > 0:
        print("Profit: $",round(profit_loss, 2))
    else:
        print(f"Loss: $",round(abs(profit_loss), 2))
    print("******************************************************************************************************************")


def view_transaction_history(user_id):
    cursor.execute("SELECT transaction_type, crypto_name, amount, price FROM transactions WHERE user_id=%s", (user_id,))
    transactions = cursor.fetchall()
    
    if transactions:
        print("\nTransaction History:")
        for transaction in transactions:
            print(transaction[0].capitalize()," - ",transaction[2]," of ",transaction[1]," at $",transaction[3])
        print()
        print("******************************************************************************************************************")
        # Ask if the user wants to export the transaction history
        export_choice = input("\nDo you want to export your transaction history to a text file? (y/n): ")
        if export_choice.lower() == 'y':
            export_transaction_history(user_id, transactions)
    else:
        print("No transaction history available.")
    print()
    print("******************************************************************************************************************")

def export_transaction_history(user_id, transactions):
    # Get the user's username for file naming
    cursor.execute("SELECT username FROM users WHERE user_id=%s", (user_id,))
    username = cursor.fetchone()[0]

    # Define the file name (no need for os module)
    file_name = f"C:\\Users\\Imran\\Desktop\\exports\\{username}_transaction_history.txt"

    # Write transaction history to the file
    with open(file_name, 'w') as file:
        file.write("Transaction History for "+username+":\n")
        file.write("====================================\n")
        for transaction in transactions:
            transaction_type = transaction[0].capitalize()
            crypto_name = transaction[1]
            amount = transaction[2]
            price = transaction[3]
            file.write(transaction_type+" - "+str(amount)+" of "+crypto_name+" at $"+str(price)+"\n")
        file.write("====================================\n")
    
    print("Transaction history exported to ",file_name," in the documents folder.")

def discover_new_crypto():
    print("\nAvailable Cryptos:")
    cursor.execute("SELECT * FROM cryptos")
    for row in cursor.fetchall():
        print(row[1] + ": $" + str(row[2]))
    print("******************************************************************************************************************")
    
    def input_for_price_history():
        user_input=input("would you like to see the price history(y/n): ")
        if user_input=="y":
            price_history()
            print("******************************************************************************************************************")
        elif user_input=="n":
            print("******************************************************************************************************************")
        else:
            print("invalid option")
            print("******************************************************************************************************************")
            input_for_price_history()
            
    input_for_price_history()

def price_history():
    user_input = input("Enter the Name of the Crypto: ")
    print()

    try:
        # Load price history from file
        with open("C:\\Users\\Imran\\Desktop\\price history\\Price__History.dat", "rb") as file:
            price_dict = pickle.load(file)

        # Check if the user_input exists in the dictionary
        if user_input not in price_dict:
            print("No price history found for '", user_input, "'.")
            return

        price_list = price_dict[user_input]

        # Display the price history
        print("The price history of ", user_input, " is:")
        formatted_prices = " | ".join("$" + str(price) for price in price_list)
        print(formatted_prices)

        # Calculate sum and average price
        sum_price = sum(price_list)
        if len(price_list) > 0:
            avg_price = sum_price / len(price_list)
        else:
            print("No prices available to calculate an average.")
            return

        # Compare current price to average
        current_price = price_list[0]
        if current_price > avg_price:
            print("\nThe price of ", user_input, " has increased compared to its average.")
        elif current_price < avg_price:
            print("\nThe price of ", user_input, " has decreased compared to its average.")
        else:
            print("\nThe price of ", user_input, " has remained constant compared to its average.")

    except FileNotFoundError:
        print("Price history file not found.")
    except Exception as e:
        print("An error occurred: ", e)

    print()

    
def edit_profile(user_id):
    new_username = input("Enter new username: ")
    new_password = input("Enter new password: ")
    full_name = input("Enter your full name: ")
    phone_number = input("Enter your phone number: ")
    email = input("Enter your email address: ")
    cursor.execute("UPDATE users SET username=%s, password=%s, full_name=%s, phone_number=%s, email=%s WHERE user_id=%s", (new_username, new_password, full_name, phone_number, email, user_id,))
    conn.commit()
    print("Profile updated successfully.")
    print("******************************************************************************************************************")

def admin_login():
    admin_password = input("Enter admin password: ")
    if admin_password == "admin123":  # Simple admin password check
        print("Welcome Admin!")
        print("******************************************************************************************************************")
        admin_menu()
    else:
        print("Invalid admin password.")
        print("******************************************************************************************************************")
        main_menu()
    
def admin_menu():
    while True:
        print("\nAdmin Menu:")
        print("1. View Users")
        print("2. Search User by Username")
        print("3. View and Respond to Complaints")
        print("4. Logout")
        choice = input("Choose an option: ")
        
        if choice == '1':
            print("******************************************************************************************************************")
            view_users()
        elif choice == '2':
            print("******************************************************************************************************************")
            search_user_by_username()
        elif choice == '3':
            print("******************************************************************************************************************")
            view_complaints()
        elif choice == '4':
            print("******************************************************************************************************************")
            main_menu()
        else:
            print("Invalid option. Please try again.")


def view_complaints():
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()
    
    if complaints:
        for complaint in complaints:
            complaint_id = complaint[0]
            user_id = complaint[1]
            complaint_text = complaint[2]
            print("Complaint from User ",user_id," : ",complaint_text)
            
            response = input("Enter your response: ")
            cursor.execute("INSERT INTO inbox (user_id, response_text) VALUES (%s, %s)", (user_id, response))
            cursor.execute("DELETE FROM complaints WHERE complaint_id=%s", (complaint_id,))
            conn.commit()
            print("Response sent and complaint resolved.")
            print("******************************************************************************************************************")
    else:
        print("No complaints to display.")
        print("******************************************************************************************************************")
def view_inbox(user_id):
    cursor.execute("SELECT response_text FROM inbox WHERE user_id=%s", (user_id,))
    responses = cursor.fetchall()
    
    if responses:
        for response in responses:
            print("Admin Response: ",response[0])
        cursor.execute("DELETE FROM inbox WHERE user_id=%s", (user_id,))  # Clear inbox after viewing
        conn.commit()
        print("******************************************************************************************************************")
    else:
        print("Your inbox is empty.")
        print("******************************************************************************************************************")

def view_users():
    print("\nRegistered Users:")
    cursor.execute("SELECT * FROM users")
    for user in cursor.fetchall():
        print(user)
    print("******************************************************************************************************************")
    
def search_user_by_username():
    username = input("Enter the username of the user you want to search for: ")
    
    # Query to find the user by username
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    
    if user:
        print("******************************************************************************************************************")
        print("User Details:")
        print("User ID: ",user[0])
        print("Username: ",user[1])
        print("Full Name: ",user[3])
        print("Phone Number: ",user[4])
        print("Email: ",user[5])
        print("Transaction Method: ",user[6])
        print("Transaction Details: ",user[7])
        print("Portfolio: ",user[8])
        print("Crypto Count: ",user[9])
        print("******************************************************************************************************************")
    else:
        print("No user found with the username:", username)
        print("******************************************************************************************************************")


print("******************************************* Welcome to Cryoto Manager ********************************************")
update_crypto_prices()# Update prices on startup
file()
main_menu()
conn.close()# Close the database connection
