import datetime
import time
import os #Darbas su directions ir file'ais # Naudojamas USER Efficiency pagerinimui kuomet mes istriname is terminalo perditine medziaga
import binascii #Binarinis kodavimas PLACIAU: https://docs.python.org/3/library/binascii.html
import hashlib #hash slaptazodziu generacija saugumui
import getpass  # Slepiame slaptazodzius
import random #daily recommendations

def clear_screen():
    #Terminal/User interface / Isvalo
    os.system('cls' if os.name == 'nt' else 'clear')

def hash_password(password):
    #Hash slaptazodziu generavimas
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    #Hash slaptazodziu patirikinimas su konsoleje/Terminale ivestu
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def get_valid_input(prompt, error_message, condition, cast_type=lambda x: x):
    while True:
        user_input = input(prompt)
        if condition(user_input):
            return cast_type(user_input)
        else:
            print(error_message)

def main_menu():
    clear_screen()
    print("Welcome to the FitnessTracker app!")
    while True:
        print("\n1. Login\n2. Sign up\n3. Exit")
        choice = input("Enter your choice: ").strip().lower()
        if choice == '1':
            login()
        elif choice == '2':
            signup()
        elif choice == '3':
            print("Thank you for using FitnessTracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def login():
    clear_screen()
    print("Login to your account")
    username = input("Enter your username: ")
    provided_password = getpass.getpass("Enter your password: ")
    try:
        with open(f"{username}_task.txt", 'r') as file:
            saved_password = file.readline().strip()
            if verify_password(saved_password, provided_password):
                log_activity(f"User {username} logged in successfully.")
                user_menu(username)
            else:
                print("Incorrect username or password, try again.")
                log_activity(f"Failed login attempt for {username}.")
                time.sleep(2)
    except FileNotFoundError:
        print("File not found. Please check the username and try again.")
        log_activity(f"Failed login for {username}: File not found.")
        time.sleep(2)
    except Exception as e:
        print(f"An error occurred: {e}")
        log_activity(f"Error during login for {username}: {e}")
        time.sleep(2)

def user_menu(username):
    while True:
        clear_screen()
        print(f"Welcome, {username}! What would you like to do today?")
        options = {
            '1': ("View personal data", view_data),
            '2': ("Add new task", task_information),
            '3': ("Update current task", task_update),
            '4': ("View task status", task_update_viewer),
            '5': ("Your daily recommendations", daily_recommendations),
            '6': ("Gym+ locations", gym_locations),
            '7': ("Meal suggestions", meal_suggestions),
            'quit': ("Exit the program", None)
        }
        for key, value in options.items():
            print(f"{key}. {value[0]}")
        choice = input("\nPlease select an option or type 'quit' to exit: ").strip().lower()
        if choice in options:
            if choice == 'quit':
                break
            action = options[choice][1]
            if action == meal_suggestions or action == gym_locations or action == daily_recommendations: #5/2/2024 00:31 Pridedam action = daily_recommeendation, tam, kad programa nemestu klaidos "An error occurred: daily_recommendations() takes 0 positional arguments but 1 was given
                action()
            else:
                action(username)  
        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)


def view_data(username):
    #FIXED personal data
    clear_screen()
    password = getpass.getpass("Please enter your password to access this data: ")
    try:
        filename = f"{username}_task.txt"
        with open(filename, 'r') as file:
            stored_password = file.readline().strip()  # Read the stored hashed password from the file
            if verify_password(stored_password, password):
                log_activity(f"User {username} successfully accessed personal data.")
                print("Personal Information:")
                for line in file:
                    if "Name:" in line or "Address:" in line or "Age:" in line: #Patikriname .txt file ir 
                        print(line.strip())  # Pateikiame tik  #"Name:" in line or "Address:" in line or "Age:" in line:, visa kita ismeta #
            else:
                print("Incorrect password. Access denied.")
                log_activity(f"User {username} failed to access personal data due to incorrect password.")
            input("\nPress Enter to return to the menu...")
    except FileNotFoundError:
        print(f"Error: File not found - {filename}. Please ensure the file exists.")
        log_activity(f"User {username} failed to access personal data because the file was not found.")
        time.sleep(2)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        log_activity(f"Error occurred while {username} was trying to access personal data: {e}")
        time.sleep(2)



def user_information(username, hashed_password):
    # Surenkame naudotoju informacija username ir hashintus slaptazodzius naudodami metoda get_valid_input
    # - - - 
    clear_screen()
    print("Please enter your personal details:")
    try:
        name = get_valid_input("Enter your name please: ", "Please enter a valid name (letters and spaces only): ",
                               lambda x: all(c.isalpha() or c.isspace() for c in x))
        address = input("Enter your current address: ")
        age = get_valid_input("Enter your age: ", "Please enter a valid age (numeric only): ",
                              lambda x: x.isdigit(), int)
        
        # Iraisome i naujai sukuriama .txt file
        with open(f"{username}_task.txt", 'w') as file:
            file.write(f"{hashed_password}\nName: {name}\nAddress: {address}\nAge: {age}\n")
        print("Profile created successfully!")
        time.sleep(2)
    except Exception as e:
        print(f"Failed to save user information: {e}")
        time.sleep(2)

def signup():
    clear_screen()
    print("Sign up for a new account")
    username = input("Choose a username: ")
    password = getpass.getpass("Choose a password: ")  # Ssu import getpass pasiemame slaptazodi
    hashed_password = hash_password(password)  # Hashiname slaptazodi per kita metoda
    user_information(username, hashed_password)  # Pass the username and hashed password for storing user info
    print("\nProceeding to login...")
    time.sleep(2)
    login()



def task_information(username):
   # Nauju uzduociu pridejimas 
    clear_screen()
    try:
        num_tasks = int(input("How many tasks do you want to add? "))
        with open(f"{username}_task.txt", 'a') as file:
            for i in range(1, num_tasks + 1):
                task = input(f"Enter task {i}: ")
                target = input(f"Enter target for task {i}: ")
                file.write(f"TASK {i}: {task}\nTARGET {i}: {target}\n")
        print(f"{num_tasks} tasks added successfully!")
    except ValueError:
        print("Invalid number of tasks.")
    except Exception as e:
        print(f"Failed to add tasks: {e}")
    input("Press Enter to return to the menu...")

def task_update(username):
    #Atnaujinimas metodui task_information
    clear_screen()
    try:
        with open(f"{username}_task.txt", 'a') as file:
            completed_task = input("Enter the completed tasks: ")
            ongoing_task = input("Enter the ongoing tasks: ")
            not_started_task = input("Enter the tasks not yet started: ")
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"Update Time: {current_time}\n") # Kada paskutini karta buvo pakeista
            file.write(f"COMPLETED TASK: {completed_task}\nONGOING TASK: {ongoing_task}\nNOT YET STARTED: {not_started_task}\n")
            log_activity(f"Tasks updated by {username}.")
        print("Tasks updated successfully!")
    except Exception as e:
        print(f"Failed to update tasks: {e}")
        log_activity(f"Task update failure for {username}: {e}")
    input("Press Enter to return to the menu...")

def task_update_viewer(username):
    # 5/2/2024 20:41 Bug FIXED excluding personal data
    clear_screen()
    try:
        with open(f"{username}_task.txt", 'r') as file:
            print("Task Updates:")
            task_data = []
            start_reading = False
            for line in file:
                if "TASK" in line or "TARGET" in line or "Update Time" in line:
                    start_reading = True
                if start_reading:
                    task_data.append(line)
            print("".join(task_data))
    except FileNotFoundError:
        print("No task file found. Perhaps no tasks have been added yet.")
    except Exception as e:
        print(f"An error occurred while reading task data: {e}")
    input("Press Enter to return to the menu...")



# 29/04/2024 Daily recommendations // Prototype
def daily_recommendations():
    #5/2/2024 daily_recommendations randomizacija, kuomet is rekomendacijos pagal amziu, pereiname i zaismingesne versija, kuomet is listo skaitome 15 sugeneruotu rekomendaciju ir su biblioteka random issirenkame viena is ju kiekvieena karta vartotojas issaukia daily_recommendations
    clear_screen()
    try:
        with open("Daily_recommendations\daily.txt", 'r') as file:
            recommendations = file.readlines()  #listas
        print("Daily Recommendation for your workout:")
        print(random.choice(recommendations).strip())  #randomizeris (import random)
    except FileNotFoundError:
        print("Recommendations file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    input("Press Enter to return to the menu...")


def gym_locations():
    # 05/1/2024 23:12 Skaitymas adressu is file'u, BUG FIXXED kur printinamas ne pavadinimas miesto, o  .txt file'as
    clear_screen()     
    locations = {
        '1': 'Location gyms\\Vilnius_gyms.txt',
        '2': 'Location gyms\\Kaunas_gyms.txt',
        '3': 'Location gyms\\Klaipeda_gyms.txt',
        '4': 'Location gyms\\Lithuania_all_gyms.txt'
    }
    print("Choose a location:\n1 - Vilnius\n2 - Kaunas\n3 - Klaipeda\n4 - All Lithuania")
    choice = input("Enter your choice: ")
    filename = locations.get(choice)
    
    if filename:
        try:
            with open(filename, 'r') as file:
                city = next(file).strip()  # Read the first line as city name
                print(f"Gyms in {city}:")
                # Read the rest of the file for addresses and enumerate them
                for index, address in enumerate(file, 1):
                    print(f"{index}. {address.strip()}")
        except FileNotFoundError:
            print("Information for this location is not available.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Invalid choice.")
    
    input("Press Enter to return to the menu...")
def meal_suggestions():
    # Maisto patarimai dienos metu su datetime biblioteka
    clear_screen()
    current_hour = datetime.datetime.now().hour
    print("Meal Suggestions:")
    if current_hour < 7:
        print("Early Breakfast suggestion: Smoothie with spinach, banana, and protein powder.")
    elif 7 <= current_hour < 10:
        print("Breakfast suggestion: Avocado toast with poached eggs and a side of fruit.")
    elif 10 <= current_hour < 12:
        print("Mid-morning snack suggestion: Mixed nuts and a piece of fruit.")
    elif 12 <= current_hour < 14:
        print("Lunch suggestion: Quinoa salad with roasted vegetables and a balsamic vinaigrette.")
    elif 14 <= current_hour < 16:
        print("Afternoon snack suggestion: Hummus with carrot sticks and whole grain crackers.")
    elif 16 <= current_hour < 18:
        print("Pre-dinner snack suggestion: Sliced apples with almond butter.")
    elif 18 <= current_hour < 20:
        print("Dinner suggestion: Grilled salmon with asparagus and wild rice.")
    elif 20 <= current_hour < 22:
        print("Evening snack suggestion: Cottage cheese with pineapple chunks.")
    else:
        print("Late-night snack suggestion: Greek yogurt with granola.")
    
    input("Press Enter to return to the menu...")

def log_activity(message):
    #activity loginimas
    with open("activity_log.txt", "a") as log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - {message}\n")

if __name__ == '__main__':
    main_menu()
