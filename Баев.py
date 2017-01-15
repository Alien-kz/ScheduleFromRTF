#!/usr/bin/python
# -*- coding: utf-8 -*-

import re       #regex
import os.path  #fileexists
import sys      #fileexists
from datetime import datetime, timedelta
import locale   #month, day in text mode

class lesson():
    def __init__(self, date, timestart, timeend, group, room, subject):
        self.datetime = datetime.strptime(date + " " + timestart, "%d.%m.%Y %H:%M")
        self.timestart = timestart
        self.timeend = timeend
        self.group = group
        self.room = room
        self.subject = subject
    def __lt__(self, other):
        return self.datetime < other.datetime

program = os.path.basename(sys.argv[0]).decode("cp1251")
teacher = program[0:-3]
#teacher = u"Баев"
print teacher

#file structure: \{ date \} {\t time \} \{ room subject teacher subgroup \}
filenames = [          
                        u"М-11.rtf", u"М-21.rtf",
			u"ВМ-11.rtf", u"ВМ-21.rtf", 
			u"Э-11.rtf", u"Э-21.rtf", u"Э-31.rtf",
			u"Ф-11.rtf", u"Ф-21.rtf", u"Ф-31.rtf",
			u"Г-11.rtf", u"Г-21.rtf", u"Г-31.rtf", ]

thesubgroup=re.compile("-\d\d\(")
theroom=re.compile(" (\d\d\d) ")
thedate=re.compile("\d\d\.\d\d\.\d\d\d\d")
thetime=re.compile("\d\d:\d\d")
thetext=re.compile("(\\\\\'[0-9a-f][0-9a-f])+")

cellstart=re.compile("\{")
cellend=re.compile("\}")

schedule = []
firstdate = datetime(2100, 01, 01)
for filename in filenames:
    print u"Файл: ", filename

    if not os.path.exists(filename):
        continue    
    f = open(filename)

    fulltext = ""
    for line in f:
        fulltext = fulltext + line
    f.close()
    
    fulltext = re.sub("\n|\r", '', fulltext)
    fulltext = re.sub("\line", "\}\{", fulltext)

    searchstart = 30000
    searchend = 30000
    lasttime = ""
    endtime = ""
    currentdate = ""

    while 1:
# find block started by { and finished by }        
        searchstartObject=cellstart.search(fulltext, searchend)
        if searchstartObject:
            searchstart = searchstartObject.start()
        else:
            break
        searchendObject=cellend.search(fulltext, searchstart)
        if searchendObject:
            searchend = searchendObject.start()
        else:
            break

# check block is date dd.dd
        date=thedate.search(fulltext, searchstart, searchend)
        time=thetime.search(fulltext, searchstart, searchend)
        if date:
            currentdate = date.group()
            currentdatetime = datetime.strptime(currentdate, "%d.%m.%Y")
            if firstdate > currentdatetime:
                firstdate = currentdatetime
# check block is time tt:tt
        elif time:
            lasttime = time.group()
            endtimeObject = thetime.search(fulltext, time.end(), time.end() + 10)
            if endtimeObject:
                endtime = endtimeObject.group()
            else:
                print "bad data in time " + currentdate + ' ' + lasttime
        else:
# check block is another text        
            # try to find: 1) room " ddd " 2) subgroup "-dd("
            roomObject=theroom.search(fulltext, searchstart, searchend)
            if roomObject:
                room=roomObject.group()
            subgroup=""
            subgroupObject=thesubgroup.search(fulltext, searchend+1)
            if subgroupObject:
                subgroup="(" + fulltext[subgroupObject.end()] + ")"
            group=filename[0:-4]# + subgroup
                
            # try to find cp1251 text-code \'dd
            wordinblock = ""
            for subjectName in thetext.finditer(fulltext, searchstart, searchend):
                #temp is string "\'CA\'EE\'E4"
                temp = subjectName.group()
                #lst is integer array { 202, 238, 228 }
                charCodes = []
                for i in range(2,len(temp),4):
                    num = int(temp[i:i+2], 16)
                    charCodes.append(num)
                #text is char unicode array "Код"
                text = bytearray(charCodes).decode("cp1251")
                #if text is teacher
                if text == teacher:
                    print lasttime, "-", endtime, ":", group, room, lastwordinblock
                    #add lesson to list (previos block is subject)
                    schedule.append(lesson(currentdate, lasttime, endtime, group, room, lastwordinblock))

                if wordinblock == "":
                    wordinblock = text
                else:
                    wordinblock = wordinblock + " " + text
            lastwordinblock = wordinblock

# day and month in locale
locale.setlocale(locale.LC_ALL, '')

# output txt
print '\nmake ' + teacher + '.txt'
f = open(teacher + '.txt', 'w')
for i in range(7):
    stringDate = firstdate.strftime("%d %b (%A)")
    print stringDate
    f.write(stringDate + "\n")
    for theLesson in sorted(schedule):
        if firstdate.date() == theLesson.datetime.date():
            text = theLesson.timestart + '-' + \
                   theLesson.timeend + "\t" + \
                   theLesson.group + "\t" + \
                   theLesson.room + "\t" + \
                   theLesson.subject
            f.write(text.encode("cp1251") + "\n")
            print text
    print
    f.write('\n')
    firstdate = firstdate + timedelta(days=1)
f.close()

# output csv
print '\n\nmake ' + teacher + '.csv\n'
csv = open(teacher + '.csv', 'w')
dlm = ", "
csv.write('Subject' + dlm + \
          'Start Date' + dlm + \
          'Start Time' + dlm + \
          'End Date' + dlm + \
          'End Time' + dlm + \
          'Description' + dlm + \
          'Location\n')
for theLesson in sorted(schedule):
	text = theLesson.group
	text = text + dlm + \
               theLesson.datetime.strftime("%d.%m.%Y") + dlm + \
               theLesson.timestart + dlm + \
               theLesson.datetime.strftime("%d.%m.%Y") + dlm + \
               theLesson.timeend + dlm + \
               theLesson.subject + dlm + \
               theLesson.room
	print text
	csv.write(text.encode("utf-8") + "\n")
csv.close()
