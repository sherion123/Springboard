# Project 1: Banking System Project
This project is meant to practice OOP in Python by designing a mini-banking system.
When code is executed, users are able to create an account, show account stats, deposit a balance, withdraw a balance, and exit the program.

# Features
- Account creation via command 'create'
- Issue checkbook if account type is a "checking" account and checkbook has not yet been initally issued.
- Deposit/withdraw money via command 'deposit' and 'withdraw'
- Display transaction history via command 'show'
- Log activity and write into log file (bank_log.txt)

# Files
- Project 1.py: Contains the main code
- oop_banking: This is the file that the main code reads in and writes into. Essentially, this is the dataset that contains all the records in the banking system. If there are no accounts created yet initially, this will initialize as an empty list,
- bank_log: This is where all the logging history is stored.
- UML Class Diagram as requested in project outline.

# Instructions
1. Execute the Project1.py script.
2. Once executed, you should see the following within the terminal. Type any of the following command 'create', 'deposit', 'withdraw', 'show', 'exit'
   
   ![image](https://github.com/user-attachments/assets/b8833830-677b-414e-9009-89512fe11428)

3. To create an account that does not yet exit, choose 'create'. An account number will be assigned automatically. Fill out information prompted until account has been successfully created. "Account created" message should be shown.
4. For every other commands deposit, withdraw and show, the command prompt will ask for the Account number before you can execute the task.
