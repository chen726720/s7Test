import socket
from struct import pack, unpack


class cBytes(bytes):

    def __add__(self, other):

        if type(other) is bytes or type(other) is cBytes:
            return cBytes(super().__add__(other))

        elif type(other) is int:
            return self + other.to_bytes(
                other.bit_length() // 8 + 1 if other == 0 or other.bit_length() % 8 != 0 else other.bit_length() // 8,
                'big')

    def toFloat(self):
        return unpack('f', self)

    def toString(self):
        return self[2:self[1]].decode('gbk')

    def toInt(self):
        return int.from_bytes(self, "big")

    @staticmethod
    def from_string(strText:str, length:int):
        ret = strText.encode('gbk')
        if len(ret) > length-2:
            ret = ret[:length-2]
        ret = cBytes.from_int(len(ret), 1) + ret
        ret = cBytes.from_int(length, 1) + ret
        return ret

    @staticmethod
    def from_int(value: int, length: int = 0):
        if length == 0:
            return value.to_bytes(
                value.bit_length() // 8 + 1 if value == 0 or value.bit_length() % 8 != 0 else value.bit_length() // 8,
                'big')
        else:
            ret = 0
            for _ in range(length):
                ret += value & (0xff << _ * 8)
            return ret.to_bytes(length, 'big')


class Item:
    DBNum = 0
    Address = 0
    Length = 0
    Area = 0
    bit = False
    mode = False
    retMode = False
    retValue = cBytes()
    value = cBytes()


class s7:
    connOK = False

    def __init__(self, outTime: int = 2):
        self.client = socket.socket()
        self.client.settimeout(outTime)

    def connect(self, Host: str, Port: int = 102) -> bool:
        '''
        连接至PLC
        :param Host: PLC IP地址
        :param Port: plc 端口默认102
        :return: bool类型 表示是否成功
        '''
        if self.connOK:
            return True
        if self.client.connect_ex((Host, Port)) == 0:
            if self.__cr():
                self.connOK = self.__job()
        return self.connOK

    def close(self):
        self.client.close()

    def wirteItem(self, DBNum: int, Addres: int, Length: int, Data: bytes, Area: int = 0x84):
        '''
        向plc写入数据
        :param DBNum: 要写入的DB块地址
        :param Addres: 要写入的起始地址
        :param Length: 要写入的长度
        :param Data: 要写入的数据
        :param Area: 要写入的位置 默认为写入DB块的变量
        :return: bool 类型表示写入是否成功
        '''
        item = Item()
        item.DBNum = DBNum
        item.Address = Addres
        item.Length = Length
        item.Area = Area
        item.mode = True
        item.value = Data
        if self.connOK:
            return self.ItemToBytes(item)

    def wirte_int(self, DBNum: int, Addres: int, Data: int, Area: int = 0x84):
        '''
                向plc写入数据
                :param DBNum: 要写入的DB块地址
                :param Addres: 要写入的起始地址
                :param Length: 要写入的长度
                :param Data: 要写入的数据
                :param Area: 要写入的位置 默认为写入DB块的变量
                :return: bool 类型表示写入是否成功
                '''
        item = Item()
        item.DBNum = DBNum
        item.Address = Addres
        item.Length = 2
        item.Area = Area
        item.mode = True
        item.value = cBytes.from_int(Data, 2)
        if self.connOK:
            return self.ItemToBytes(item)

    def wirte_dint(self, DBNum: int, Addres: int, Data: int, Area: int = 0x84):
        '''
                        向plc写入数据
                        :param DBNum: 要写入的DB块地址
                        :param Addres: 要写入的起始地址
                        :param Data: 要写入的数据
                        :param Area: 要写入的位置 默认为写入DB块的变量
                        :return: bool 类型表示写入是否成功
                        '''
        item = Item()
        item.DBNum = DBNum
        item.Address = Addres
        item.Length = 4
        item.Area = Area
        item.mode = True
        item.value = cBytes.from_int(Data, 4)
        if self.connOK:
            return self.ItemToBytes(item)

    def wirte_float(self, DBNum: int, Addres: int, Data: float, Area: int = 0x84):
        '''
                                向plc写入数据
                                :param DBNum: 要写入的DB块地址
                                :param Addres: 要写入的起始地址
                                :param Data: 要写入的数据
                                :param Area: 要写入的位置 默认为写入DB块的变量
                                :return: bool 类型表示写入是否成功
                                '''
        item = Item()
        item.DBNum = DBNum
        item.Address = Addres
        item.Length = 4
        item.Area = Area
        item.mode = True
        item.value = pack("f", Data)[::-1]
        if self.connOK:
            return self.ItemToBytes(item)

    def wirte_string(self, DBNum: int, Addres: int, Length: int, Data: str, Area: int = 0x84):
        '''
        向plc写入数据
        :param DBNum: 要写入的DB块地址
        :param Addres: 要写入的起始地址
        :param Length: 要写入的长度
        :param Data: 要写入的数据
        :param Area: 要写入的位置 默认为写入DB块的变量
        :return: bool 类型表示写入是否成功
        '''
        item = Item()
        item.DBNum = DBNum
        item.Address = Addres
        item.Length = Length
        item.Area = Area
        item.mode = True
        item.value = cBytes.from_string(Data, Length)
        if self.connOK:
            return self.ItemToBytes(item)

    def readItem(self, DBNum: int, Addres: int, Length: int, Area: int = 0x84):
        '''
        从plc读取变量
        :param DBNum:DB块编号
        :param Addres: 要读取的起始地址
        :param Length: 要读取的长度 单位 字节
        :param Area: 要读取的区域 默认为DB块
        :return: cBytes 返回的数据
        '''
        item = Item()
        item.DBNum = DBNum
        item.Address = Addres
        item.Length = Length
        item.Area = Area
        if self.connOK:
            return self.ItemToBytes(item)
        return item.retValue

    def read_int(self, DBNum: int, Addres: int, Area: int = 0x84):
        '''
        从plc读取变量
        :param DBNum:DB块编号
        :param Addres: 要读取的起始地址
        :param Length: 要读取的长度 单位 字节
        :param Area: 要读取的区域 默认为DB块
        :return: cBytes 返回的数据
        '''
        item = Item()
        item.DBNum = DBNum
        item.Address = Addres
        item.Length = 2
        item.Area = Area
        if self.connOK:
            return self.ItemToBytes(item).toInt()

    def read_dint(self, DBNum: int, Addres: int, Area: int = 0x84):
        '''
        从plc读取变量
        :param DBNum:DB块编号
        :param Addres: 要读取的起始地址
        :param Area: 要读取的区域 默认为DB块
        :return: cBytes 返回的数据
        '''
        item = Item()
        item.DBNum = DBNum
        item.Address = Addres
        item.Length = 4
        item.Area = Area
        if self.connOK:
            return self.ItemToBytes(item).toInt()

    def read_float(self, DBNum: int, Addres: int, Area: int = 0x84):
        '''
                从plc读取变量
                :param DBNum:DB块编号
                :param Addres: 要读取的起始地址
                :param Area: 要读取的区域 默认为DB块
                :return: cBytes 返回的数据
                '''
        item = Item()
        item.DBNum = DBNum
        item.Address = Addres
        item.Length = 4
        item.Area = Area
        if self.connOK:
            return self.ItemToBytes(item).toFloat()

    def read_string(self, DBNum: int, Addres: int, Length: int, Area: int = 0x84):
        '''
        从plc读取变量
        :param DBNum:DB块编号
        :param Addres: 要读取的起始地址
        :param Length: 要读取的长度 单位 字节
        :param Area: 要读取的区域 默认为DB块
        :return: cBytes 返回的数据
        '''
        item = Item()
        item.DBNum = DBNum
        item.Address = Addres
        item.Length = Length
        item.Area = Area
        if self.connOK:
            return self.ItemToBytes(item).toString()
        return item.retValue

    def ItemToBytes(self, item):
        data = cBytes()
        data += 0x02f080
        data += self.__s7Header(len(item.value))
        data += int(0x05 if item.mode else 0x04)
        data += 0x01120a10
        data += 1 if item.bit else 2
        data += cBytes.from_int(1 if item.bit else item.Length, 2)
        data += cBytes.from_int(item.DBNum, 2)
        data += cBytes.from_int(item.Area, 1)
        data += cBytes.from_int(item.Address << 3, 3)
        if item.mode:
            data += cBytes.from_int(3 if item.bit else 4, 2)
            data += cBytes.from_int(1 if item.bit else len(item.value) << 3, 2)
            data += item.value
        data = self.__S7TPKT(len(data) + 4) + data
        self.client.send(data)
        readData = self.client.recv(2048)
        if readData[19] == 0x05:
            item.retMode = readData[21] == 0xff
            return item.retMode
        if readData[17] == 0x00:
            if readData[22] != 0x03:
                readLen = cBytes(readData[23:25]).toInt() >> 3
                item.retValue = readData[25:readLen + 25]
            else:
                item.retValue = readData[25:26]
        return cBytes(item.retValue)

    def __cr(self) -> bool:
        self.client.send(b'\x03\x00\x00\x16\x11\xe0\x00\x00\x00\x01\x00\xc1\x02\x10\x00\xc2\x02\x03\x01\xc0\x01\x0a')
        ret = self.client.recv(2048)
        return len(ret) >= 5 and ret[5] == 0xd0

    def __job(self) -> bool:
        self.client.send(
            b'\x03\x00\x00\x19\x02\xf0\x80\x32\x01\x00\x00\xcc\xc1\x00\x08\x00\x00\xf0\x00\x00\x01\x00\x01\x03\xc0')
        ret = self.client.recv(2048)
        return len(ret) >= 5 and ret[5] == 0xf0

    def __s7Header(self, length: int):
        ret = cBytes()
        ret += 0x32010000
        ret += cBytes.from_int(length + 39 if length > 0 else 35, 2)
        ret += cBytes.from_int(0x000e, 2)
        ret += cBytes.from_int(length + 4 if length > 0 else length, 2)

        return ret

    def __S7TPKT(self, length: int, version: int = 3, reserved: int = 0):
        ret = cBytes()
        ret += version
        ret += reserved
        ret += cBytes.from_int(length, 2)
        return ret


