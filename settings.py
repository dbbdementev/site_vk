import sqlite3


def register_group(group_id):
    con = sqlite3.connect('mysite/main.db')
    cur = con.cursor()
    cur.execute("""SELECT confirmation_token FROM groups WHERE group_id=?""", (group_id,))
    result = cur.fetchone()
    cur.close()
    con.close()
    return str(result[0])


def main_groups(key):
    con = sqlite3.connect('mysite/main.db')
    cur = con.cursor()
    cur.execute("""SELECT token,acces_commands,group_link FROM groups WHERE key=?""", (key,))
    result = cur.fetchone()
    cur.close()
    con.close()
    return result
