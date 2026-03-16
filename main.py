from dbfread import DBF

table = DBF('DATA/basa.dbf', encoding='cp1251')
print(table.field_names)
for i in list(table)[:5]:
    print(i)

print(len(table))