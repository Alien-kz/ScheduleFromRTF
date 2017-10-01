#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import copy
import locale   #month, day in text mode
import os.path  #fileexists
import sys      #fileexists
from datetime import datetime, timedelta

class position:
	def __init__(self, text, start):
		self.start = start
		self.end = start
		self.text = text
		self.theletter = re.compile("\\\\\'[0-9a-f][0-9a-f]|\s")
		self.thetime = re.compile("\d\d:\d\d\s-\s\d\d:\d\d")
		self.thedate = re.compile("\d\d\.\d\d\.\d\d\d\d")
		self.theroom = re.compile("\s\d\d\d\s")
		
	def printstartend(self):
		print self.start, self.end

	def printblock(self):
		print self.text[self.start: self.end+1]
	   
	def next(self):
		self.start = self.text.find("{", self.end)
		self.end = self.text.find("}", self.start)
		start = self.start
		end = self.end
		return start != -1
	
	def gettext(self):
		delimeter = " "
		codes = []
		for letter in self.theletter.finditer(self.text, self.start, self.end):
			temp = letter.group()
			if len(temp) == 4:
				codes.append(int(temp[2:4], 16))
			elif delimeter == " " and len(codes) > 0 and codes[-1] != 32:
				codes.append(32)
		return bytearray(codes).decode("cp1251")
	
	def gettime(self):
		for time in self.thetime.finditer(self.text, self.start, self.end):
			return time.group()
		return ""
	
	def getdate(self):
		for date in self.thedate.finditer(self.text, self.start, self.end):
			return date.group()
		return ""
		 
	def getroom(self):
		for room in self.theroom.finditer(self.text, self.start, self.end):
			return room.group()[1:-1]
		return ""
	
class lessons:
	def __init__(self, subject, date, time, name, location, group):
		self.subject = subject
		self.date = date
		self.name = name
		self.location = location
		self.time = time
		self.group = group
		
	def datetime(self):
		if self.date != ' ':
			return datetime.strptime(self.date + " " + self.time[0:5], "%d.%m.%Y %H:%M")
		return datetime(2100, 01, 01)
	
	def __lt__(self, other):
		return self.datetime() < other.datetime()
	   
	def print_lesson(self):
		start_time = self.time[0:5]
		end_time = self.time[8:14]
		return self.group + ", " + self.date + ", " + start_time + ", " + self.date + ", " + end_time + ", " + self.location
    	

# date
# ?
# time
# ?
# room subject
# teacher
# ?
# ?
# time
# ?
# room subject
# teacher
# room subject
# teacher
# ?
# ?

#while (1)
#	if !date: break
#	step
#	step
#	while (1)
#		if !time: break
#		step
#		step
#		while (1)
#			if !room: break
#			subj
#			step
#			teacher
#			step
#	    step
#	    step
def get_from_file(file_name, answer):
	f = open(file_name)
	fulltext = ""
	for line in f:
		fulltext = fulltext + line
	pos = position(fulltext, 30000)
	lesson = lessons("", "", "", "", "", file_name[:-4])
	firstdate = datetime(2100, 01, 01)	
	while True:
#		pos.printstartend() #- uncomment to debug
#		pos.printblock() #- uncomment to debug

		date = ""
		while pos.next():
			date = pos.getdate()
			if len(date) != 0:
				break
		if len(date) == 0:
			break
		
		currentdate =  datetime.strptime(date, "%d.%m.%Y") 
		if currentdate < firstdate:
			firstdate = currentdate 
#		print " DATE : ", date
		lesson.date = date		
		pos.next()
		pos.next()
		
		while True:
			time = pos.gettime()
			if len(time) == 0:
				break
#			print " TIME : ", time
			lesson.time = time
			pos.next()
			pos.next()

			while True:	
				room = pos.getroom()	
				if len(room) == 0:
					break
#				print " ROOM : ", room
				lesson.location = room
	
				text = pos.gettext()
				if len(text) == 0:
					break
#				print " SUBJECT : ", text
				lesson.subject = text				

				pos.next()
		
				text = pos.gettext()
				if len(text) == 0:
					break
#				print " NAME : ", text
				lesson.name = text
				
				if not pos.next():
					break
				
				answer.append(copy.deepcopy(lesson))
				
			pos.next()
			if not pos.next():
				break
	return firstdate

teacher = u"Баев"
program = os.path.basename(sys.argv[0]).decode(locale.getpreferredencoding())
teacher = program[0:-3]

file_out = open('calendar.csv', 'w')
head="Subject, Start Date, Start Time, End Date, End Time, Location"
file_out.write((head + '\n').encode("utf-8"))

schedule = []

filenames = [ u"ВМ-11.rtf", u"М-21.rtf",
            u"М-11.rtf", u"ВМ-21.rtf", 
            u"Э-11.rtf", u"Э-21.rtf", u"Э-31.rtf",
            u"Ф-11.rtf", u"Ф-21.rtf", u"Ф-31.rtf",
            u"Г-11.rtf", u"Г-21.rtf", u"Г-31.rtf", ]

for filename in filenames:
	if not os.path.exists(filename):
		continue  
	firstdate = get_from_file(filename, schedule)

# output csv
print head
for les in schedule:
	if les.name[:-3] == teacher:
		text = les.print_lesson()
		file_out.write((text + '\n').encode("utf-8"))
		print text

# day and month in locale
locale.setlocale(locale.LC_ALL, '')

# output txt
sorted_schedule = []
for les in sorted(schedule):
	if les.name[:-3] == teacher:
		sorted_schedule.append(les)


print '\nmake ' + teacher + '.txt'
f = open(teacher + '.txt', 'w')
for i in range(7):
	stringDate = firstdate.strftime("%d %b (%A)")
	print stringDate
	f.write(stringDate + "\n")
	for theLesson in sorted_schedule:
		if firstdate.date() == theLesson.datetime().date():
			text = theLesson.time[0:5] + '-' + \
					theLesson.time[8:14] + "\t" + \
					theLesson.group + "\t" + \
					theLesson.location + "\t" + \
					theLesson.subject
			f.write(text.encode(locale.getpreferredencoding()) + "\n")
			print text
	print
	f.write('\n')
	firstdate = firstdate + timedelta(days=1)
f.close()
