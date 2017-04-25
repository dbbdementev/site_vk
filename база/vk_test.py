import sqlite3
import random


def black_list(user_id):
    con = sqlite3.connect('black_list.db')
    cur = con.cursor()
    cur.execute("SELECT id_users_black FROM black_users WHERE id_users_black={id}".format(id=user_id))
    arr = cur.fetchall()
    cur.close()
    con.close()
    return arr



if 101 in black_list(101):
    print('kjkj')

