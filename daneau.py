import fdb,csv,re
from math import sqrt
import datetime
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
current_time1 = datetime.datetime.now()

root = Tk()
root.baselink = tkFileDialog.askopenfilename(initialdir = "/",title = "Select FDB",filetypes = (("firebird base","*.fdb"),("all files","*.*")))
root.csvlink = tkFileDialog.askopenfilename(initialdir = "/",title = "Select CSV",filetypes = (("CSV","*.csv"),("all files","*.*")))
print root.baselink
#root.baselink=r'C:/Users/Dell/Desktop/BDOTtst.FDB'
#root.csvlink=r"P:/dt/sdrpk.csv"
tol=0.01
con = fdb.connect(
    host='localhost', database=root.baselink,
    user='sysdba', password='masterkey'
  )

n=0
inele = open(root.csvlink,"r")
rows=csv.DictReader(inele, delimiter=",")
for row in rows:
        n+=1
        cursel = con.cursor()
        curupd = con.cursor()
        curope = con.cursor()
        curuser1 = con.cursor()
        curuser2 = con.cursor()

        typlinii=str(row.get("typlinii"))
        WKT=str(row.get("wkt"))
        KERG=str(row.get("operat"))
        datamod=str(row.get("datamod"))
        datamod=re.sub("; ",".", datamod)
        usermod=str(row.get("usermod"))
        usermod=usermod.strip("'")
        datautw=str(row.get("datautw"))
        datautw=re.sub("; ",".",datautw)
        userutw=str(row.get("userutw"))
        userutw=userutw.strip("'")
        WKT=WKT.split(",")
        frstWKT=WKT[0].split(" ")
        scndWKT=WKT[1].split(" ")
        frstWKTx=round(float(frstWKT[2]),2)
        frstWKTy=round(float(frstWKT[1].strip("(")),2)
        frstwsp=[frstWKTy,frstWKTx]
        scndWKTx=round(float(scndWKT[1].strip(")")),2)
        scndWKTy=round(float(scndWKT[0]),2)
        scndwsp=[scndWKTy,scndWKTx]
        Xmax=max(frstWKTx,scndWKTx)+tol
        Ymax=max(scndWKTy,frstWKTy)+tol
        Xmin=min(frstWKTx,scndWKTx)-tol
        Ymin=min(scndWKTy,frstWKTy)-tol

        def roundTime(dt=None, dateDelta=datetime.timedelta(minutes=1)):
            """Round a datetime object to a multiple of a timedelta
            dt : datetime.datetime object, default now.
            dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
            Author: Thierry Husson 2012 - Use it as you want but don't blame me.
                    Stijn Nevens 2014 - Changed to use only datetime objects as variables
            """
            roundTo = dateDelta.total_seconds()

            if dt == None : dt = datetime.datetime.now()
            seconds = (dt - dt.min).seconds
            # // is a floor division, not a comment on following line:
            rounding = (seconds+roundTo/2) // roundTo * roundTo
            return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

        try:
            modDate=datetime.datetime.strptime(datamod, "%Y.%m.%d.%H.%M.%S")
        except:
             modDate=str(roundTime(datetime.datetime.now(),datetime.timedelta(minutes=15)))
             modDate=datetime.datetime.strptime(modDate, "%Y-%m-%d %H:%M:%S")
        try:
            createDate=datetime.datetime.strptime(datautw, "%Y.%m.%d.%H.%M.%S")
        except:
             createDate=str(roundTime(datetime.datetime.now(),datetime.timedelta(minutes=15)))
             createDate=datetime.datetime.strptime(createDate, "%Y-%m-%d %H:%M:%S")
        curope.execute("select UID from EW_OPERATY where NUMER="+"'"+KERG+"'")
        operat=curope.fetchone()
        if operat is None:
            operat="0"
        else:
            operat=str(operat[0])
        curuser1.execute("SELECT ID from EW_USERS where EWNAME='"+userutw+"'")
        userCreate=curuser1.fetchone()
        if userCreate is None:
            userCreate="0"
        else:
            userCreate=str(userCreate[0])
        curuser2.execute("SELECT ID from EW_USERS where EWNAME='"+usermod+"'")
        userMod=curuser2.fetchone()
        if userMod is None:
            userMod="0"
        else:
            userMod=str(userMod[0])
        SELECT= "select P0_X, P0_Y, P1_X, P1_Y, UID, OPERAT, TYP_LINII, STAN_ZMIANY CREATE_TS from EW_POLYLINE where XMAX<="+str(Xmax)+"AND YMAX<="+str(Ymax)+"AND XMIN>="+str(Xmin)+"AND YMIN>="+str(Ymin)+" AND STAN_ZMIANY=0"
        cursel.execute(SELECT)
        for selMinMax in cursel:
            #print selMinMax
            P0X=selMinMax[0]
            P0Y=selMinMax[1]
            if selMinMax[2] is None:
                P1X=selMinMax[0]
            else:
                P1X=selMinMax[2]
            if selMinMax[2] is None:
                P1Y=selMinMax[1]
            else:
                P1Y=selMinMax[3]
            begdl=sqrt((P0X-frstWKTx)**2+(P0Y-frstWKTy)**2)
            enddl=sqrt((P1X-scndWKTx)**2+(P1Y-scndWKTy)**2)
            if begdl<tol and enddl<tol:
                curupd.execute("update EW_POLYLINE SET OPERAT="+operat.strip("'")+",USER_CREATE="+userCreate.strip("'")+",USER_MODIFY="+userMod.strip("'")+",CREATE_TS='"+str(createDate)+"',MODIFY_TS='"+str(modDate)+"' where EW_POLYLINE.UID="+str(selMinMax[4]))
            else:
                begdl=sqrt((P0X-scndWKTx)**2+(P0Y-scndWKTy)**2)
                enddl=sqrt((P1X-frstWKTx)**2+(P1Y-frstWKTy)**2)
                if begdl<tol and enddl<tol:
                  curupd.execute("update EW_POLYLINE SET OPERAT="+operat.strip("'")+",USER_CREATE="+userCreate.strip("'")+",USER_MODIFY="+userMod.strip("'")+",CREATE_TS='"+str(createDate)+"',MODIFY_TS='"+str(modDate)+"' where EW_POLYLINE.UID="+str(selMinMax[4]))
        if n % 50 == 0:
            con.commit()
            current_time2 = datetime.datetime.now()
            print n
            print ("%s seconds"%(current_time2 - current_time1))
con.commit()
current_time2 = datetime.datetime.now()
print ("koniec %s seconds"%(current_time2 - current_time1))
raw_input()