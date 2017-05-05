import sqlite3
import datetime
from difflib import SequenceMatcher


# добавление в черный список
def record_black_users(user_id, token):
    con = sqlite3.connect('mysite/main.db', isolation_level=None)
    cur = con.cursor()
    recording_date = datetime.datetime.today()
    cur.execute(
        "SELECT black_user_id,quantity,warning,group_id FROM black_users WHERE black_user_id=? AND group_id IN (SELECT group_id FROM groups WHERE token=?)",
        (user_id, token))
    result = cur.fetchall()
    if result:
        if result[0][2] == 0:
            warning = 1
            cur.execute(
                "UPDATE black_users SET warning=? WHERE black_user_id=? AND group_id IN (SELECT group_id FROM groups WHERE token=?)",
                (warning, user_id, token))
            return 'Вам 1 предупреждение.'
        if result[0][2] == 1:
            warning = 2
            cur.execute(
                "UPDATE black_users SET warning=? WHERE black_user_id=? AND group_id IN (SELECT group_id FROM groups WHERE token=?)",
                (warning, user_id, token))
            return 'Вам 2 предупреждение.'
        if result[0][2] == 2:
            warning = 0
            quantity = result[0][1] + 1
            expiration_date = recording_date + datetime.timedelta(hours=quantity)
            cur.execute(
                "UPDATE black_users SET recording_date=?,expiration_date=?,quantity=?,warning=? WHERE black_user_id=? AND group_id IN (SELECT group_id FROM groups WHERE token=?)",
                (recording_date, expiration_date, quantity, warning, user_id, token))
            return 'Вы добавлены в черный список.'
        cur.close()
        con.close()
    else:
        quantity = 0
        warning = 1
        expiration_date = recording_date
        cur.execute("SELECT group_id FROM groups WHERE token=?", (token,))
        group_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO black_users(black_user_id,recording_date,expiration_date,quantity,warning,group_id) VALUES (?,?,?,?,?,?)",
            (user_id, recording_date, expiration_date, quantity, warning, group_id))
        return 'Вам 1 предупреждение.'
    cur.close()
    con.close()


# определение запрещенных слов
def words_black(text):
    words = text.lower().split(' ')
    words_list = ['блять', 'сиськи', 'пизда', 'нахуй', 'хуй', 'писю', 'пенис', 'ебланка', 'голой', 'трахну', 'член',
                  'пошлую', 'ебланище', 'пизда', 'гавно', 'срать', 'долбаеб', 'вагина', 'сукина', 'дебил', 'киску',
                  'выебу', 'суки', 'пиздуй', 'попа', 'спидом', 'мразь', 'кит', 'шмара', 'вирус', 'минет', 'хуя', 'ебал',
                  'мразь', 'шлюха', 'пошленькая', 'интим', 'шкура', 'пиздень', 'сосешь', 'схуяли', 'жопа', 'педофила',
                  'пидор', 'урод', 'дебил', 'даун', 'тити', 'титюльки', 'транс', 'трахнуть', 'шавуха', 'грудь', 'гей',
                  'куни', 'пидаром', 'девственницу', 'куратор', 'умрешь', 'кишки', 'вырежу', 'губой', 'ебаный', 'лох',
                  'вирт', 'ебальник', 'хрен', 'отсосать', 'ебемся', 'секс', 'онанизм', 'дурак', 'дурачок']
    for i in words:
        for w in words_list:
            name = SequenceMatcher(lambda x: x in ' ', i, w).ratio()
            if name > 0.8:
                return True
    return False
