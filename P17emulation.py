import os, pty
from serial import Serial
import threading

from PyCRC.CRC16 import CRC16
from PyCRC.CRC16DNP import CRC16DNP
from PyCRC.CRC16Kermit import CRC16Kermit
from PyCRC.CRC16SICK import CRC16SICK
from PyCRC.CRC32 import CRC32
from PyCRC.CRCCCITT import CRCCCITT

##################################################################
# add CRC to Set response
##################################################################
def addcrcset(content):
                    
        temp = bytearray(b'^') + bytearray(bytes(content))   ### !
        
        temp_number = CRCCCITT().calculate(bytes(temp))
        
        temp.append((temp_number & 0xff00)>>8)
        temp.append((temp_number & 0x00ff)>>0)
        temp += bytearray(b'\r')
     
        return bytes(temp)

##################################################################
# add CRC to Query response
##################################################################
def addcrc(content, length):
       
        length +=3
        number = len(content) + 3
        
        if (number != length): 
          print ("Length mismatch:", number, " should be:", length)
        else:
        
# Length must be constant 3 chars        
          if   number > 99:
            size = bytes(str(number),"utf-8")
          elif number > 9:
            size = b'0' +  bytes(str(number),"utf-8")
          else :
            size = b'00' +  bytes(str(number),"utf-8")
                        
          temp = bytearray(b'^D') + bytearray(bytes(size)) + bytearray(bytes(content))  

          temp_number = CRCCCITT().calculate(bytes(temp))
        
          temp.append((temp_number & 0xff00)>>8)
          temp.append((temp_number & 0x00ff)>>0)
          temp += bytearray(b'\r')
     
          return bytes(temp)

##################################################################
# detect and dispatch command
##################################################################
def listener(port):
    #continuously listen to commands on the master device
    while 1:
        res = b""
        while not res.endswith(b"\r"):
            #keep reading one byte at a time until we have a full line
            res += os.read(port, 1)
        print("\ncommand: %s" % res)

        request = res[1:2]  
        length  = int(res[2:5])                         # len with delimiter
        content = res[5:(5+int(length))]
        delimiter = res[(5+int(length)-1):5+int(length)]
                
#        print ("*request:", request)        
#        print ("*length:", int(length))
#        print ("*content:", content)
#        print ("*delimiter:", delimiter)
#        print(addcrc(content))
#        print(request,"*",length,"*",content[0:2],"*", delimiter)

        if (request == b"P"):
          if   (content[0:2] == b'PI'   and length ==  3)  : os.write(port, addcrc(b"17", 5-3)) # Protocol 17
          #^P003PI<cr>
          
          elif (content[0:2] == b'ID'   and length ==  3)  :   
            temp = bytearray(b'0123456789')                  # expects 1..20 numbers
            inum = len(temp)  
                                              
            if (inum <= 20):
              if (len(temp)>9):					
                temp = bytearray(bytes(str(inum),"utf-8")) + temp
              else:
                temp = bytearray(b'0') + bytearray(bytes(str(inum),"utf-8")) + temp 
            os.write(port, addcrc(bytes(temp), inum+2))
          #^P003ID<cr>
          
          elif (content[0:3] == b'VFW'  and length ==  4)  : os.write(port, addcrc(b"VERFW:00001.00", 17-3)) 
          #^P004VFW<cr>
          elif (content[0:4] == b'VFW2' and length ==  5)  : os.write(port, addcrc(b"VERFW2:00001.00", 17-3)) 
          #^P005VFW2<cr>
          elif (content[0:2] == b'MD'   and length ==  3)  : os.write(port, addcrc(b"AAA,BBBBBB,CC,D,E,FFFF,GGGG,HH,III", 37-3)) 
          #^P003MD<cr>
          elif (content[0:4] == b'PIRI' and length ==  5)  : os.write(port, addcrc(b"AAAA,BBB,CCCC,DDDD,EEEE,FFFF,GGGG,H,II,J,K", 45-3)) 
          #^P005PIRI<cr>
          elif (content[0:2] == b'GS'  and length ==  3)  : 
            os.write(port, addcrc(b"AAAA,BBBB,CCCC,DDDD,EEEE,FFF,+GGGGG,HHHH,IIII,JJJJ,KKKK,LLLL,MMMM,OOOO,PPPP,QQQQ,RRRR,SSSS,TTTT,UUUU,VVV,WWW,XXX,Y", 112-3)) 
          #^P003GS
          elif (content[0:2] == b'PS'  and length ==  3)  : 
            os.write(port, addcrc(b"AAAAA,BBBBB,+CCCCC,+DDDDD,+EEEEE,+FFFFF,GGGGG,HHHHH,IIIII,JJJJJJ,KKKKK,LLLLL,MMMMM,NNNNN,OOOOOO,PPP,Q,R,S,T,U,V",115-3))
          #^P003PS<cr>
          elif (content[0:3] == b'MOD'  and length ==  4)  : os.write(port, addcrc(b"XX", 5-3)) 
          #^P004MOD<cr>
          elif (content[0:2] == b'WS'   and length ==  3)  : os.write(port, addcrc(b"A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V", 40-3)) 
          #^P003WS<cr>
          elif (content[0:4] == b'FLAG' and length ==  5)  : os.write(port, addcrc(b"A,B,C,D,E",12-3)) 
          #^P005FLAG<cr>
          elif (content[0:1] == b'T'    and length ==  2)  : os.write(port, addcrc(b"YYYYMMDDHHFFSS",17-3)) 
          #^P002T<cr>
          elif (content[0:2] == b'ET'   and length ==  3)  : os.write(port, addcrc(b"NNNNNNNN",11-3)) 
          #^P003ET<cr>
        
          elif (content[0:2] == b'EY'   and length == 10)  : os.write(port, addcrc(b"NNNNNNNN",11-3)) 
          #^P010EYyyyynnn<cr>
          elif (content[0:2] == b'EM'   and length == 12)  : os.write(port, addcrc(b"NNNNNNN",10-3)) 
          #^P012EMyyyymmnnn<cr>
          elif (content[0:2] == b'ED'   and length == 14)  : os.write(port, addcrc(b"NNNNNN",9-3)) 
          #^P014EDyyyymmddnnn<cr>
          elif (content[0:2] == b'EH'   and length == 16)  : os.write(port, addcrc(b"NNNNN",8-3)) 
          #^P016EHyyyymmddhhnnn<cr>

          elif (content[0:3] == b'GOV'  and length ==  4)  : os.write(port, addcrc(b"AAAA,BBBB,CCCC,DDDD",22-3)) 
          #^P004GOV<cr>
          elif (content[0:3] == b'GOF'  and length ==  4)  : os.write(port, addcrc(b"AAAA,BBBB,CCCC,DDDD",22-3)) 
          #^P004GOF<cr>
          elif (content[0:4] == b'OPMP' and length ==  5)  : os.write(port, addcrc(b"AAAAAA",9-3)) # length D012 ???
          #^P005OPMP<cr>
          elif (content[0:4] == b'GPMP' and length ==  5)  : os.write(port, addcrc(b"AAAAAA",9-3)) # length D012 ???
          #^P005GPMP<cr>
        
          elif (content[0:5] == b'MPPTV'and length ==  6)  : os.write(port, addcrc(b"AAAA,BBBB",12-3)) 
          #^P006MPPTV<cr>
          elif (content[0:2] == b'SV'   and length ==  3)  : os.write(port, addcrc(b"AAAA,BBBB",12-3)) 
          #^P003SV<cr>
          elif (content[0:3] == b'LST'  and length ==  4)  : os.write(port, addcrc(b"AA",5-3)) 
          #^P004LST<cr>
          elif (content[0:2] == b'DI'   and length ==  3)  : 
            os.write(port, addcrc(b"AAAA,BBBB,CCCC,DDDD,EEEE,FFFF,GGGG,HHHH,IIII,JJ,KKKK,LLLL,MMMM,NNN,OOOO,PPPP,QQQQ,RRRR,SSSS,TTTT,UUUU,VVVV,WWWW,XXX,YYYY",123-3)) 
          #^P003DI<cr>

          elif (content[0:4] == b'BATS' and length ==  5)  : 
            os.write(port, addcrc(b"AAAA,BBBB,CCCC,DDDD,EEE,FFFF,GGGG,HHHH,IIII,JJJJ,K,LLLL,MMNNOOPPQQRR,S,TTTT,UUU,VVVV,WWWW",92-3)) 
          #^P005BATS<cr>
          elif (content[0:2] == b'DM'   and length ==  3)  : os.write(port, addcrc(b"AAA",6-3)) 
          #^P003DM<cr>
          elif (content[0:3] == b'MAR'  and length ==  4)  : 
            os.write(port, addcrc(b"AAAA,BBBB,CCCC,DDDD,EEEE,FFFF,GGGG,HHHH,IIII,JJJJ,KKKK,LLLL,MMMM,NNNN,OOOO,PPPP,QQQQ,RRRR,SSSS,TTTT,UUUU,VVVV,WWWWWW,XXXXXX",\
            126-3)) 
          #^P004MAR<cr>
          elif (content[0:3] == b'CFS'  and length ==  4)  : os.write(port, addcrc(b"AA,BB",8-3)) 
          #^P004CFS<cr>

          elif (content[0:3] == b'HFS'  and length ==  6)  : 
            temp = bytearray(b',AA,BBCCDDEEFFGG,HH,IIII,JJJJ,KKKKK,LLLLL,MMMM,NNNN,OOOO,PPPP,QQQQ,+RRRRR,SSSS,TTTT,UUUU,VVVV,WWWW,XXXX,YYYY,ZZZ,aaa,bbb,ccc')
            temp = bytearray(bytes(content[3:5])) + temp
            os.write(port, addcrc(bytes(temp),129-3))
          #^P006HFSnn<cr>
          
          elif (content[0:4] == b'HECS' and length ==  5)  : os.write(port, addcrc(b"AA,B,C,D,E,F,G,H,I",19-3)) 
          #^P005HECS<cr>
          elif (content[0:5] == b'GLTHV'and length ==  6)  : os.write(port, addcrc(b"AAAA",7-3)) 
          #^P006GLTHV<cr>
          elif (content[0:3] == b'FET'  and length ==  4)  : os.write(port, addcrc(b"YYYYMMDDHH",13-3)) # length D004 ???
          #^P004FET<cr>
        
          elif (content[0:2] == b'FT'   and length ==  3)  : os.write(port, addcrc(b"AAA",6-3)) 
          #^P003FT<cr>
          elif (content[0:4] == b'ACCT' and length ==  5)  : os.write(port, addcrc(b"AAAA,BBBB,CCCC,DDDD",22-3)) 
          #^P005ACCT<cr>
          elif (content[0:4] == b'ACLT' and length ==  5)  : os.write(port, addcrc(b"AAAA,BBBB",12-3)) 
          #^P005ACLT<cr>
          elif (content[0:5] == b'FPADJ'and length ==  6)  : os.write(port, addcrc(b"A,BBBB,C,DDDD,E,FFFF,G,HHHH",30-3))  # length D006 ???
          #^P006FPADJ<cr>        

          elif (content[0:4] == b'FPPF' and length ==  6)  : os.write(port, addcrc(b"nnn",6-3)) 
          #^P006FPPF<cr>
          elif (content[0:4] == b'AAPF' and length ==  5)  : os.write(port, addcrc(b"a,bbb,ccc",12-3)) 
          #^P005AAPF<cr>
             
          elif (content[0:6] == b'EMINFO'and length == 7)  : os.write(port, addcrc(b"1,10000,00049,00111,00000,1",30-3)) 
          #^P007EMINFO\r

          else:
              os.write(port, b"Unknown Query Comand\r")
              
# - - - - - - - -               

        elif (request == b"S"):
          if   (content[0:3] == b'LON'   and length == 5)  : os.write(port, addcrcset(b"1")) 
          #^S005LONn<cr>
          elif (content[0:1] == b'P'     and length == 4)  : os.write(port, addcrcset(b"1")) 
          #^S004Pmn<cr>
          elif (content[0:3] == b'DAT'   and length ==16)  : os.write(port, addcrcset(b"1")) 
          #^S016DATyymmddhhffss<cr>
          elif (content[0:4] == b'GOHV'  and length == 9)  : os.write(port, addcrcset(b"1")) 
          #^S009GOHVnnnn<cr>
          
          elif (content[0:4] == b'GOLV'  and length == 9)  : os.write(port, addcrcset(b"1")) 
          #^S009GOLVnnnn<cr>
          elif (content[0:4] == b'GOHF'  and length == 9)  : os.write(port, addcrcset(b"1")) 
          #^S009GOHFnnnn<cr>
          elif (content[0:4] == b'GOLF'  and length == 9)  : os.write(port, addcrcset(b"1")) 
          #^S009GOLFnnnn<cr>
          elif (content[0:4] == b'OPMP'  and length ==11)  : os.write(port, addcrcset(b"1")) 
          #^S011OPMPnnnnnn<cr>
          
          elif (content[0:4] == b'GPMP'  and length ==11)  : os.write(port, addcrcset(b"1")) 
          #^S011GPMPnnnnnn<cr>
          elif (content[0:4] == b'SIHV'  and length == 9)  : os.write(port, addcrcset(b"1")) 
          #^S009SIHVnnnn<cr>
          elif (content[0:4] == b'SILV'  and length == 9)  : os.write(port, addcrcset(b"1")) 
          #^S009SILVnnnn<cr>
          elif (content[0:6] == b'MPPTHV'and length ==11)  : os.write(port, addcrcset(b"1")) 
          #^S011MPPTHVnnnn<cr>
          
          elif (content[0:6] == b'MPPTLV'and length ==11)  : os.write(port, addcrcset(b"1")) 
          #^S011MPPTLVnnnn<cr>
          elif (content[0:3] == b'LST'   and length == 6)  : os.write(port, addcrcset(b"1")) 
          #^S006LSTnn<cr>
          elif (content[0:5] == b'MCHGC' and length ==10)  : os.write(port, addcrcset(b"1")) 
          #^S010MCHGCnnnn<cr>
          elif (content[0:5] == b'MCHGV' and length ==15)  : os.write(port, addcrcset(b"1")) 
          #^S015MCHGVmmmm,nnnn<cr>
          
          elif (content[0:5] == b'GLTHV' and length ==10)  : os.write(port, addcrcset(b"1")) 
          #^S010GLTHVnnnn<cr>
          elif (content[0:5] == b'BATDV' and length ==25)  : os.write(port, addcrcset(b"1")) 
          #^S025BATDVaaaa,bbbb,cccc,dddd<cr>
          elif (content[0:3] == b'SEP'   and length == 6)  : os.write(port, addcrcset(b"1")) 
          #^S006SEPnn<cr>
          elif (content[0:2] == b'ED'    and length == 5)  : os.write(port, addcrcset(b"1")) 
          #^S005EDmn<cr>

          elif (content[0:3] == b'BCA'   and length ==17)  : os.write(port, addcrcset(b"1")) 
          #^S017BCAaaaa,bbb,cccc<cr>
          elif (content[0:2] == b'DM'    and length == 6)  : os.write(port, addcrcset(b"1")) 
          #^S006DMnnn<cr>
          elif (content[0:2] == b'PF'    and length == 3)  : os.write(port, addcrcset(b"1")) 
          #^S003PF<cr>
          elif (content[0:3] == b'F50'   and length == 4)  : os.write(port, addcrcset(b"1")) 
          #^S004F50<cr>

          elif (content[0:3] == b'F60'   and length == 4)  : os.write(port, addcrcset(b"1")) 
          #^S004F60<cr>
          elif (content[0:1] == b'V'     and length == 6)  : os.write(port, addcrcset(b"1")) 
          #^S006Vnnnn<cr>
          elif (content[0:2] == b'FT'    and length == 6)  : os.write(port, addcrcset(b"1")) 
          #^S006FTnnn<cr>
          elif (content[0:4] == b'ACCT'  and length ==14)  : os.write(port, addcrcset(b"1")) 
          #^S014ACCTaaaa,bbbb,cccc,dddd<cr>

          elif (content[0:4] == b'ACLT'  and length ==14)  : os.write(port, addcrcset(b"1")) 
          #^S014ACLTaaaa,bbbb<cr>
          elif (content[0:2] == b'BT'    and length == 4)  : os.write(port, addcrcset(b"1")) 
          #^S004BTn<cr>
          elif (content[0:3] == b'BIT'   and length ==16)  : os.write(port, addcrcset(b"1")) 
          #^S016BITyymmddhhffss<cr>
          elif (content[0:3] == b'BST'   and length == 9)  : os.write(port, addcrcset(b"1")) 
          #^S009BST<cr>

          elif (content[0:4] == b'ACCB'  and length ==16)  : os.write(port, addcrcset(b"1")) 
          #^S016ACCBa,bbbb<cr>
          elif (content[0:3] == b'BTS'   and length == 7)  : os.write(port, addcrcset(b"1")) 
          #^S007BTSnnn<cr>
          elif (content[0:6] == b'MUCHGC'and length ==11)  : os.write(port, addcrcset(b"1")) 
          #^S011MUCHGCnnnn<cr>
          elif (content[0:5] == b'FPADJ' and length ==12)  : os.write(port, addcrcset(b"1")) 
          #^S012FPADJm,nnnn<cr>

          elif (content[0:4] == b'BDCM'  and length == 9)  : os.write(port, addcrcset(b"1")) 
          #^S009BDCMnnnn<cr>
          elif (content[0:4] == b'FPPF'  and length == 8)  : os.write(port, addcrcset(b"1")) 
          #^S008FPPFnnn<cr>
          elif (content[0:4] == b'PALE'  and length == 6)  : os.write(port, addcrcset(b"1")) 
          #^S006PALEn<cr>
          elif (content[0:6] == b'FPRADJ'and length ==12)  : os.write(port, addcrcset(b"1")) 
          #^S012FPRADJm,nnnn<cr>

          elif (content[0:6] == b'FPSADJ'and length ==12)  : os.write(port, addcrcset(b"1")) 
          #^S012FPSADJm,nnnn<cr>
          elif (content[0:6] == b'FPTADJ'and length ==12)  : os.write(port, addcrcset(b"1")) 
          #^S012FPTADJm,nnnn<cr>
          elif (content[0:4] == b'AAPF'  and length ==14)  : os.write(port, addcrcset(b"1")) 
          #^S014AAPFa,bbb,ccc<cr>

          elif (content[0:7] == b'REMINFO'and length ==27)  : os.write(port, addcrcset(b"1")) 
          #^S027REMINFO00000,00000,1,00142<cr>
          elif (content[0:7] == b'SEMINFO'and length ==27)  : os.write(port, addcrcset(b"1")) 
          #^S027SEMINFO00000,00000,1,00142<cr>
          elif (content[0:7] == b'TEMINFO'and length ==27)  : os.write(port, addcrcset(b"1")) 
          #^S027TEMINFO00000,00000,1,00142<cr>
                                                                                                                                                             
          else:
              os.write(port, b"Unknown Set Comand\r")         

        elif (request == b"D"):
          if   (content[0:3] == b'BMS'   and length == 54)  : 
#          print (res[8:56]) 
          #^D054BMS0479,008,0,0000,0,0,0532,0532,1480,0,0,0450,0148\x91E\r
#          txt = (str(res[8:56]),"utf-8").split(",")
            print ("BMS_Voltage        ",res[ 8:12])
            print ("Battery_percent    ",res[13:16])
            print ("Charge/Discharge   ",res[17:18])
            print ("Current            ",res[19:23])
            print ("BMS_warning_code   ",res[24:25])
            print ("BMS_force_charge   ",res[26:27])
            print ("BMS_cv_voltage     ",res[28:32])
            print ("BMS_float_voltage  ",res[33:37])
            print ("BMS_MaxChgCurrent  ",res[38:42])
            print ("BMS_BatStopDisFlag ",res[43:44])
            print ("BMS_BatStopChaFlag ",res[45:46])
            print ("BMS_CutOffVoltage  ",res[47:51])
            print ("BMS_MaxDisChgCurr  ",res[52:56])

        else:
            os.write(port, b"Unknown Request Method\r") 

##################################################################
# test generator
##################################################################
def test_serial():
    """Start the testing"""
    master,slave = pty.openpty() #open the pseudoterminal
    s_name = os.ttyname(slave) #translate the slave fd to a filename

    #create a separate thread that listens on the master device for commands
    thread = threading.Thread(target=listener, args=[master])
    thread.start()

    #open a pySerial connection to the slave
    ser = Serial(s_name, 2400, timeout=1)
    
    ser.write(b'^P003ID\r') #write the first command
    res = b""
    while not res.endswith(b'\r'):
        #read the response
        res +=ser.read()
    print("response: %s" % res)

    
    ser.write(b'^S027REMINFO00000,00000,1,00142\r') #write a second command
    res = b""
    while not res.endswith(b'\r'):
        #read the response
        res +=ser.read()
    print("response: %s" % res)


    ser.write(b'^P006HFS12\r') #write a second command
    res = b""
    while not res.endswith(b'\r'):
        #read the response
        res +=ser.read()
    print("response: %s" % res)
    
    
    ser.write(b'^D054BMS0479,008,0,0000,0,0,0532,0532,1480,0,0,0450,0148\x91E\r') #write a second command
    
    ser.write(b'^P007EMINFO\r') #write a second command
    res = b""
    while not res.endswith(b'\r'):
        #read the response
        res +=ser.read()
    print("response: %s" % res)


if __name__=='__main__':
    test_serial()
