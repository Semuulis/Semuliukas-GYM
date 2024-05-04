import datetime
import time
import os #Darbas su directions ir file'ais # Naudojamas USER Efficiency pagerinimui kuomet mes istriname is terminalo perditine medziaga
import binascii #Binarinis kodavimas PLACIAU: https://docs.python.org/3/library/binascii.html
import hashlib #hash slaptazodziu generacija saugumui
import getpass  # Slepiame slaptazodzius
import random #daily recommendations

# Abstract base class
class Menu:
    def display(self):
        raise NotImplementedError("Subclasses must implement this method")

class MainMenu(Menu):
    def display(self):
        clear_screen()
        print("Welcome to the FitnessTracker app!")
        while True:
            print("\n1. Login\n2. Sign up\n3. Exit")
            choice = input("Enter your choice: ").strip().lower()
            if choice == '1':
                UserLogin().execute()
            elif choice == '2':
                UserSignup().execute()
            elif choice == '3':
                print("Thank you for using FitnessTracker. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

class UserMenu(Menu):
    def __init__(self, username):
        self.username = username

    def display(self):
        while True:  #Menu FXIED
            clear_screen()
            print(f"Welcome, {self.username}! What would you like to do today?")
            options = {
                '1': ("View personal data", ViewData(self.username)),
                '2': ("Add new task", TaskInformation(self.username)),
                '3': ("Update current task", TaskUpdate(self.username)),
                '4': ("View task status", TaskUpdateViewer(self.username)),
                '5': ("Your daily recommendations", DailyRecommendations()),
                '6': ("Gym+ locations", GymLocations()),
                '7': ("Meal suggestions", MealSuggestions()),
                'quit': ("Exit the program", None)  # exit
            }
            for key, value in options.items():
                print(f"{key}. {value[0]}")
            choice = input("\nPlease select an option or type 'quit' to exit: ").strip().lower()
            if choice == 'quit':
                break  # double menu
            if choice in options and options[choice][1] is not None:
                options[choice][1].execute()


# base class
class Command:
    def execute(self):
        raise NotImplementedError("Subclasses must implement this method")

# c m
class UserLogin(Command):
    def execute(self):
        clear_screen()
        print("Login to your account")
        username = input("Enter your username: ")
        provided_password = getpass.getpass("Enter your password: ")
        try:
            with open(f"{username}_task.txt", 'r') as file:
                saved_password = file.readline().strip()
                if verify_password(saved_password, provided_password):
                    Logger().log(f"User {username} logged in successfully.")
                    UserMenu(username).display()
                else:
                    print("Incorrect username or password, try again.")
                    Logger().log(f"Failed login attempt for {username}.")
                    time.sleep(2)
        except FileNotFoundError:
            print("File not found. Please check the username and try again.")
            Logger().log(f"Failed login for {username}: File not found.")
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred: {e}")
            Logger().log(f"Error during login for {username}: {e}")
            time.sleep(2)

class UserSignup(Command):
    def execute(self):
        clear_screen()
        print("Sign up for a new account")
        username = input("Choose a username: ")
        password = getpass.getpass("Choose a password: ")
        hashed_password = hash_password(password)
        UserInformation(username, hashed_password).execute()
        print("\nProceeding to login...")
        time.sleep(2)
        UserLogin().execute()

class ViewData(Command):
    def __init__(self, username):
        self.username = username

    def execute(self):
        clear_screen()
        password = getpass.getpass("Please enter your password to access this data: ")
        try:
            filename = f"{self.username}_task.txt"
            with open(filename, 'r') as file:
                stored_password = file.readline().strip()
                if verify_password(stored_password, password):
                    Logger().log(f"User {self.username} successfully accessed personal data.")
                    print("Personal Information:")
                    for line in file:
                        if "Name:" in line or "Address:" in line or "Age:" in line:
                            print(line.strip())
                else:
                    print("Incorrect password. Access denied.")
                    Logger().log(f"User {self.username} failed to access personal data due to incorrect password.")
                input("\nPress Enter to return to the menu...")
        except FileNotFoundError:
            print(f"Error: File not found - {filename}. Please ensure the file exists.")
            Logger().log(f"User {self.username} failed to access personal data because the file was not found.")
            time.sleep(2)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            Logger().log(f"Error occurred while {self.username} was trying to access personal data: {e}")
            time.sleep(2)

# Uf
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password
class UserInformation(Command):
    def __init__(self, username, hashed_password):
        self.username = username
        self.hashed_password = hashed_password

    def execute(self):
        clear_screen()
        print("Please enter your personal details:")
        try:
            name = get_valid_input("Enter your name please: ", "Please enter a valid name (letters and spaces only): ",
                                   lambda x: all(c.isalpha() or c.isspace() for c in x))
            address = input("Enter your current address: ")
            age = get_valid_input("Enter your age: ", "Please enter a valid age (numeric only): ",
                                  lambda x: x.isdigit(), int)
            
            # data storing
            with open(f"{self.username}_task.txt", 'w') as file:
                file.write(f"{self.hashed_password}\nName: {name}\nAddress: {address}\nAge: {age}\n")
            print("Profile created successfully!")
            time.sleep(2)
        except Exception as e:
            print(f"Failed to save user information: {e}")
            time.sleep(2)

def get_valid_input(prompt, error_message, condition, cast_type=lambda x: x):
    while True:
        user_input = input(prompt)
        if condition(user_input):
            return cast_type(user_input)
        else:
            print(error_message)

# Singleton
class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.file_path = "activity_log.txt"
        return cls._instance

    def log(self, message):
        with open(self.file_path, "a") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{timestamp} - {message}\n")

class TaskInformation(Command):
    def __init__(self, username):
        self.username = username

    def execute(self):
        clear_screen()
        try:
            num_tasks = int(input("How many tasks do you want to add? "))
            with open(f"{self.username}_task.txt", 'a') as file:
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

class TaskUpdate(Command):
    def __init__(self, username):
        self.username = username

    def execute(self):
        clear_screen()
        try:
            with open(f"{self.username}_task.txt", 'a') as file:
                completed_task = input("Enter the completed tasks: ")
                ongoing_task = input("Enter the ongoing tasks: ")
                not_started_task = input("Enter the tasks not yet started: ")
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"Update Time: {current_time}\nCOMPLETED TASK: {completed_task}\nONGOING TASK: {ongoing_task}\nNOT YET STARTED: {not_started_task}\n")
                Logger().log(f"Tasks updated by {self.username}.")
            print("Tasks updated successfully!")
        except Exception as e:
            print(f"Failed to update tasks: {e}")
            Logger().log(f"Task update failure for {self.username}: {e}")
        input("Press Enter to return to the menu...")

class TaskUpdateViewer(Command):
    def __init__(self, username):
        self.username = username

    def execute(self):
        clear_screen()
        try:
            with open(f"{self.username}_task.txt", 'r') as file:
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

class DailyRecommendations(Command):
    def execute(self):
        clear_screen()
        try:
            with open("Daily_recommendations/daily.txt", 'r') as file:
                recommendations = file.readlines()
            print("Daily Recommendation for your workout:")
            print(random.choice(recommendations).strip())
        except FileNotFoundError:
            print("Recommendations file not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        input("Press Enter to return to the menu...")

class GymLocations(Command):
    def execute(self):
        clear_screen()
        locations = {
            '1': 'Location_gyms/Vilnius_gyms.txt',
            '2': 'Location_gyms/Kaunas_gyms.txt',
            '3': 'Location_gyms/Klaipeda_gyms.txt',
            '4': 'Location_gyms/Lithuania_all_gyms.txt'
        }
        print("Choose a location:\n1 - Vilnius\n2 - Kaunas\n3 - Klaipeda\n4 - All Lithuania")
        choice = input("Enter your choice: ")
        filename = locations.get(choice)

        if filename:
            try:
                with open(filename, 'r') as file:
                    city = next(file).strip()
                    print(f"Gyms in {city}:")
                    for index, address in enumerate(file, 1):
                        print(f"{index}. {address.strip()}")
            except FileNotFoundError:
                print("Information for this location is not available.")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Invalid choice.")
        input("Press Enter to return to the menu...")

class MealSuggestions(Command):
    def execute(self):
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

if __name__ == '__main__':
    MainMenu().display()
