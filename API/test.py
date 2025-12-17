def tach_chuoi_db_table(input_string):
    if not input_string or "-" not in input_string:
        return None, None
        
    parts = input_string.split('-', 1)
    
    db_name = parts[0]
    table_name = parts[1]
    return db_name, table_name
hn="Lmd-aa"
hn1,hn2=tach_chuoi_db_table(hn)
print(hn1)
print(hn2)