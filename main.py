from S7comm import s7

a = s7()
print(a.connect("192.168.88.14"))
print(a.wirte_int(DBNum=667, Addres=102, Data=0))
print(a.read_int(DBNum=667, Addres=102))
