import sqlite3


with open('data/email/UK.txt') as f:
    text = f.readlines()

con = sqlite3.connect('data/email/email.db')
cur = con.cursor()
for n, elem in enumerate(text):
    try:
        email, pas = elem.split(':')
        cur.execute('''INSERT INTO emails(email, password) VALUES (?, ?)''', (email, pas[:-2]))
        if n % 5 == 0:
            con.commit()
    except Exception as e:
        print(e)
        print(elem)
        with open('email_fail.txt', 'a', encoding='utf8') as f:
            f.write(str(elem) + '\n')

# a = cur.execute('''SELECT * FROM emails WHERE id < 100''').fetchall()
# print(a)

con.commit()
con.close()

print('Done')