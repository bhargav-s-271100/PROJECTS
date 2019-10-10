import ATMInternalCode
c=input("Enter ur username : ")
d=input("Enter ur password : ")
def verify(a,b,c,d):
    j=0
    for i in a:
        if i==c:
            if d==b[j]:
                print("Credentials verified ")
                return j
            else:
                print("Wrong Password ")
                exit(0)
        else:
            j+=1
    print("Invalid Username ")
    exit(0)
def mini_statement(e,g,a):
    print(format("MY BANK ATM SERVICES",'^50'))
    print("Account Holder's Name : ",a[e])
    print("Account Balance : ",g[e])
def pass_change(e,b):
    b[e]=input("Enter your new password : ")
    print("Password changed")
    b=[ ]
def deposit(e,g):
    x=int(input("Enter the amount to be deposited : "))
    m=int(g[e])
    m+=x
    print("Account Balance = ",m)
def withdrawl(e,g):
    x=int(input("Enter the amount to be withdrawn : "))
    m=int(g[e])
    if m>(x+1000) :
        m-=x
        print("Account Balance = ",m)
e=verify(a,b,c,d)
o=input("Enter 0 for ministatement or Enter 1 for password change or Enter 2 for withdrawl or Enter 3 for deposit : ")
if o=='0':
    mini_statement(e,g,a)
elif o=='1':
    pass_change(e,b)
elif o=='2' :
    withdrawl(e,g)
elif o=='3' :
    deposit(e,g)








