import subprocess,re,sys
def lines(pdf,p):
    out=subprocess.run(['pdftotext','-bbox-layout','-f',str(p),'-l',str(p),pdf,'-'],capture_output=True,text=True).stdout
    res=[]
    for m in re.finditer(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>',out,re.S):
        words=re.findall(r'>([^<]+)</word>',m.group(5))
        res.append((round(float(m.group(2)),1),' '.join(words)[:34]))
    return res
orig,page,new=sys.argv[1:4]
a=lines(orig,int(page));b=lines(new,1 if len(sys.argv)<5 else int(sys.argv[4]))
for i in range(max(len(a),len(b))):
    x=a[i] if i<len(a) else ('','');y=b[i] if i<len(b) else ('','')
    print(f"{x[0]!s:>6} {x[1]:34} | {y[0]!s:>6} {y[1]}")
