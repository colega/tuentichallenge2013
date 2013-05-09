import shutil

packet = '''GET /adminpanel.php HTTP/1.1
Host: contest.tuenti.net
Connection: keep-alive
Cache-Control: max-age=0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31
Accept-Encoding: gzip,deflate,sdch
Accept-Language: en-US,en;q=0.8
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3
Cookie: adminsession=true'''

print len(packet)

i = 0;
allbinary = ''
for char in packet:
    binary = bin(ord(char))[2:]
    while len(binary) < 8:
        binary = '0' + binary
    allbinary += binary
    for bit in binary:
        shutil.copyfile('./router/'+bit+'.bmp', './frames/'+str(i)+'.bmp')
        i+=1
        print i, 'of', len(packet)*8
print 'done'
