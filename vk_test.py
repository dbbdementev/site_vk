import sqlite3
import random


def access_sqlite3(code):
    if code:
        con = sqlite3.connect('test.db')
        cur = con.cursor()
        id=random.randint(1,2)
        cur.execute("SELECT text FROM anecdote WHERE id={id}".format(id=id))
        arr = cur.fetchall()
        cur.close()
        con.close()
        return arr
    else:
        print('не понял')



def input_anecdote():
    code = input('напиши код:')
    print(access_sqlite3(code)[0][0])
    input_anecdote()



input_anecdote()

