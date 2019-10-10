print(format("WELCOME TO MY BANK ATM SERVICES",'^50'))
print(format("-",'-<50'))
a=['0']
b=['0']
g=['0']
while(1):
    if(input("Enter 1 to enter account details or 0 to exit : ")=='1') :
        a.append(input("Enter the account holders' names : "))
        b.append(input("Enter their corresponding password : "))
        g.append(input("Enter the corresponding account balance : "))
    else :
        break