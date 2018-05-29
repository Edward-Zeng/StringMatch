#coding=utf-8

from Levenshtein import StringMatcher

class StringMatch(StringMatcher.StringMatcher):
    Weight_e = {}
    Weight_d = {}
    Weight_i = {}

    def __init__(self,*args):
        self._DisCara = True
        self._AdaptCara = True
        if len(args)!=0:
            StringMatch.InitWeight(*args)
        else:
            StringMatch.InitWeight()
            self.ManualWeight()
            self.UpdateWeight()

    def UpdateWeight(self,*args):
        if self._DisCara == True:
            for a in [chr(it) for it in range(ord('a'), ord('z') + 1)]:
                StringMatch.AlterWeight_e(a, a.capitalize(), 2)
            if self._AdaptCara == True:
                self.ManualWeight()
            else:
                if len(args)!=0:
                    StringMatch.InitWeight(*args)
        else:
            for a in [chr(it) for it in range(ord('a'), ord('z') + 1)]:
                StringMatch.AlterWeight_e(a, a.capitalize(), 0.1)
            if self._AdaptCara == True:
                self.ManualWeight()
            else:
                if len(args)!=0:
                    StringMatch.InitWeight(args)
        para = 1
        while para!=0:
            para = 0
            for ax in [chr(it) for it in range(128)]:
                for bx in [chr(ik) for ik in range(ord(ax),128)]:
                    for cx in [chr(il) for il in range(128)]:
                        if self.GetWeight_e(ax,bx) > self.GetWeight_e(ax,cx) + self.GetWeight_e(bx,cx):
                            para = 1
                            self.AlterWeight(ax,bx,(self.GetWeight_e(ax,cx) + self.GetWeight_e(bx,cx)))
                            continue
                        elif self.GetWeight_e(ax,bx) > self.GetWeight_d(ax) + self.GetWeight_i(bx) or self.GetWeight_e(ax,bx) > self.GetWeight_d(ax) + self.GetWeight_i(bx):
                            para = 1
                            self.AlterWeight(ax,bx,(self.GetWeight_d(ax) + self.GetWeight_i(bx)))
                            continue
                        else:
                            continue

    def AlterWeight(self,*args):
        target = ''
        if len(args)==2 and type(float(args[1]))==type(1.1) and len(args[0])==1:
            target = 'o'
        elif len(args)==3 and type(float(args[2]))==type(1.1) and len(args[0])==1 and len(args[1])==1:
            target = 'Exchange'
        else:
            target = args[0]
        if target=='Exchange':
            StringMatch.AlterWeight_e(*args)
        elif target=='Delete':
            StringMatch.AlterWeight_d(*args)
        elif target=='Insert':
            StringMatch.AlterWeight_i(*args)
        elif target=='o':
            StringMatch.AlterWeight_i(*args)
            StringMatch.AlterWeight_d(*args)
        else:
            raise 'Target parameter out of range'

    def GetWeight_e(self,str1,str2):
        return StringMatch.Weight_e[str1][str2]

    def GetWeight_d(self,str):
        return StringMatch.Weight_d[str]

    def GetWeight_i(self,str):
        return StringMatch.Weight_i[str]

    def Set_DisCaractor(self):
        if self._DisCara == True:
            print('Parameter _DisCara is already set TRUE.')
        else:
            self._DisCara = True
            self.UpdateWeight()

    def Deset_DisCarator(self):
        if self._DisCara == False:
            print('Parameter _DisCara is already set FALSE.')
        else:
            self._DisCara = False
            self.UpdateWeight()

    def SetAdapCara(self):
        if self._AdaptCara == True:
            print('Parameter _AdaptCara is already set TRUE.')
        else:
            self._DisCara = True
            self.UpdateWeight()

    def DesetAdapCara(self):
        if self._AdaptCara == False:
            print('Parameter _AdaptCara is already set FALSE.')
        else:
            self._DisCara = False
            self.UpdateWeight()

    def ManualWeight(self):
        StringMatch.AlterWeight_e('o', '0', 0.4)
        StringMatch.AlterWeight_e('B', '8', 0.4)
        StringMatch.AlterWeight_e('O', '0', 0.4)
        StringMatch.AlterWeight_e('q', '9', 0.8)
        StringMatch.AlterWeight_e('b', '6', 0.8)
        StringMatch.AlterWeight_e('4', '9', 1.6)
        StringMatch.AlterWeight_e('I', '1', 0.4)
        StringMatch.AlterWeight_e('I', 'l', 0.4)
        StringMatch.AlterWeight_e('1', 'l', 0.4)
        StringMatch.AlterWeight_e('7', 'T', 0.4)
        StringMatch.AlterWeight_e('Q', 'O', 0.8)
        StringMatch.AlterWeight_e('2', 'z', 0.8)

    def distance(self,str1,str2):
        if not (isinstance(str1,str) and isinstance(str2,str)):
            raise "The inputs should be string object !"
        aint = len(str1)
        bint = len(str2)
        disMatrix = [[0 for b in range(0,aint+1)] for a in range(0,bint+1)]
        try:
            for i in range(0,bint+1):
                for j in range(0,aint+1):
                    if (i==0 and j ==0):
                        disMatrix[i][j] = 0
                    elif i==0:
                        disMatrix[i][j] = self.GetWeight_d(str1[j-1])+disMatrix[i][j-1]
                    elif j==0:
                        disMatrix[i][j] = self.GetWeight_i(str2[i-1])+disMatrix[i-1][j]
                    else:
                        temp1 = self.GetWeight_d(str1[j-1])+disMatrix[i][j-1]
                        temp2 = self.GetWeight_i(str2[i-1])+disMatrix[i-1][j]
                        if str1[j-1]==str2[i-1]:
                            temp3 = disMatrix[i-1][j-1]
                        else:
                            temp3 = self.GetWeight_e(str1[j-1],str2[i-1])+disMatrix[i-1][j-1]
                        disMatrix[i][j] = min([temp1,temp2,temp3])
            return disMatrix[bint][aint]
        except Exception:
            return super.distance(str1,str2)

    def FuzzyMatch(self,strtemp,temp,ini=1):
        if not ((isinstance(temp,list) or isinstance(temp,tuple)) and isinstance(strtemp, str)):
            raise 'input error'
        else:
            aslist = {}
            for astemp in temp:
                aslist[astemp] = self.distance(strtemp,astemp)
            bslist = sorted(aslist.items(), key = lambda x:x[1],reverse = False)
            cslist = {}
            for i in range(ini):
                cslist[bslist[i][0]] = bslist[i][1]
        del aslist
        del bslist
        return cslist


    @classmethod
    def InitWeight(cls,*args):
        ln_temp = args
        if len(ln_temp)==0:
            xe = 2
            xi = xd = 1
        elif len(ln_temp)==1:
            xe = xi = xd = ln_temp[0]
        elif len(ln_temp)==2:
            xe = ln_temp[1]
            xi = xd = ln_temp[0]
        elif len(ln_temp)==3:
            xe = ln_temp[2]
            xi = ln_temp[1]
            xd = ln_temp[0]
        else:
            raise 'Too Many input parameters!'
        try:
            xe = float(xe)
            xi = float(xi)
            xd = float(xd)
        except Exception:
            raise 'The parameters should be number type'
        alchar = []
        for i in range(128):
            alchar.append(chr(i))
        for i in alchar:
            cls.Weight_e[i] = {}
            for j in alchar:
                if i==j:
                    cls.Weight_e[i][j] = 0
                else:
                    cls.Weight_e[i][j] = xe
            cls.Weight_d[i] = xd
            cls.Weight_i[i] = xi

    @classmethod
    def AdaptAlterWeight(cls):
        alchar = []
        for i in range(128):
            alchar.append(chr(i))

    @classmethod
    def AlterWeight_e(cls,str1=' ',str2=' ',x=2):
        if (len(str1)!=1 | len(str2)!=1):
            raise 'Input should be one character'
        if float(x):
            x=float(x)
            if type(x)!=type(1.1):
                raise 'The last input parameter should be a Number !'
        cls.Weight_e[str1][str2] = x
        cls.Weight_e[str2][str1] = x

    @classmethod
    def AlterWeight_i(cls,str,x):
        if len(str)!=1:
            raise 'Input should be one character'
        if float(x):
            x = float(x)
            if type(x)!=type(1.1):
                raise 'The last input parameter should be a Number !'
        cls.Weight_i[str] = x

    @classmethod
    def AlterWeight_d(cls,str,x):
        if len(str)!=1:
            raise 'Input should be one character'
        if float(x):
            x = float(x)
            if type(x)!=type(1.1):
                raise 'The last input parameter should be a Number !'
        cls.Weight_d[str] = x

def main():
    Api = StringMatch()
   # Api.UpdateWeight()
    lt1 = 'wdfolisghoi'
    lt2 = [
        'ajgoirw',
        'jiejfgoih',
        'ncidnjih',
        'wdfoIisghoi',
        'wdfolisghoi',
        'adfolisghoi',
        'wdfklisghoi',
    ]
    ll = Api.FuzzyMatch(lt1,lt2,2)
    #print('Weight_E:%s;\n Weight_i:%s;\n Weight_d:%s'%(StringMatch.Weight_e,StringMatch.Weight_i,StringMatch.Weight_d))
    print(ll)

if __name__ == '__main__':
    main()