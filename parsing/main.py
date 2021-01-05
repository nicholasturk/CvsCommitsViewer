import json
import copy
import sys
import datetime
from pymongo import MongoClient

cvs_collection = MongoClient("************", 27017).cvs.checkins
cvs_arr_to_upload = []

class BreakIt(Exception): pass


def file_path_to_name(path):
   return path.split('/')[-1]

def convert2unicode(mydict):
   for key in mydict.keys():
      if type(mydict[key]) != datetime.datetime:
         mydict[key] = mydict[key].strip().rstrip().replace("\\x", "").replace("\\t", "")
   return mydict


def is_service_first(word):

   # Must be atleast 6 characters long
   if len(word) < 6: return False

   first_half = []
   second_half = []
   has_number = False

   # Split on first number appearance
   for (i, letter) in enumerate(word):
      try:
         if unicode(letter, 'utf-8').isnumeric():
            first_half = word[0:i]
            second_half = word[i:len(word)-1]
            has_number = True
            break 
      except:
         print("Oops")

   
   # If there's no number return false
   if not has_number: return False

   # First half must be between 3 and 5 characters
   if len(first_half) < 3 or len(first_half) > 5: return False

   # Second half must be atleast 5 numbers long
   if len(second_half) < 5: return False
   for letter in first_half: 
      try:
         if unicode(letter, 'utf-8').isnumeric(): return False
      except:
         print("Oops")

   try:
      int(second_half)
   except:
      return False
   
   print(word)

   return True


def is_jira_ticket(word):
   # Must be atleast 5 characters long to be considered a ticket
   if len(word) < 5: return False
   word_s = word.split('-')
   # Must look like '{string}-{int}'
   if len(word_s) != 2: return False
   if len(word_s[0]) < 3 or len(word_s[1]) < 3: return False 
   # First part must be a string
   try: 
      int(word_s[0])
      return False
   except: pass
   # Second part must be an int 
   try: 
      (int(word_s[1][:len(word_s[1])-1]))
   except: return False
   return True


def get_chunks(lines):
   chunks = []
   start = 0
   for (idx, line) in enumerate(lines):
      if line.startswith('RCS file') or idx == len(lines) - 1: 
         chunks.append((start, idx - 1, lines[start + 1].split(' ')[-1]))
         start = idx
   if(len(chunks) > 1): del chunks[0]
   return chunks


def block_to_mongo(block, file_path, ticket):
   ret = {}
   ret['file_name'] = file_path_to_name(file_path.rstrip().strip())
   ret['ticket'] = ticket.rstrip().strip()
   temp_date = ''
   for line in block:
      words = line.split(' ')
      if words[0] == 'revision':
         ret['revision'] = words[-1].rstrip().strip()
         continue
      ret['file_path'] = file_path.rstrip().strip()
      if (words[0] == ticket): ret['message'] = line.rstrip().strip()
      else:
         if words[0] == 'branches:': col_split = [line]
         else: col_split = line.split(';')
         for item in col_split:
            key_val = item.split(':', 1)
            if len(key_val) == 2:
               if key_val[0] == 'date':
                  temp_date = key_val[1]
                  date = key_val[1].strip().rstrip().split(' ')[0]
                  ret[key_val[0].strip().rstrip()] = datetime.datetime.strptime(date, "%Y/%m/%d")
               else:
                  ret[key_val[0].strip().rstrip().replace('.', '_')] = key_val[1].rstrip().strip()
   
   cvs_arr_to_upload.append(convert2unicode(copy.deepcopy(ret)))
   if 'date' in ret:
      ret['date'] = temp_date
   return ret


if __name__ == "__main__":

   file_name = '../' + sys.argv[1] + '.txt'
   if sys.argv[1] == 'PolicyCenter7.0': cvs_collection.drop()

   cvs_log_output = open(file_name).readlines()
   file_chunks = get_chunks(cvs_log_output)

   # Go through each file
   for chunk in file_chunks:
      # Get subset of file
      file_lines = cvs_log_output[chunk[0]:chunk[1]] 
      # Go through each line of file
      for (i, line) in enumerate(file_lines):
         # A checkin appeared (cvs logs with '---' to break revision blocks)
         if(line.startswith('---')):
            s = i + 1
            e = s
            # Get subset of description block to parse
            while not (file_lines[e].startswith('---') or file_lines[e].startswith('===')): 
               e += 1
               if(e == len(file_lines)): break
            # Get lines relating to the checkin
            description_block = file_lines[s:e]
            # Go through each message
            try:
               for msg in description_block:
                  # Go through each word
                  for (idx, word) in enumerate(msg.split(' ')):
                     # We found a ticket ('CSI-427' would yield true)
                     if is_jira_ticket(word) or is_service_first(word):
                        block_to_mongo(description_block, chunk[2], word)
                        raise BreakIt
            except BreakIt: pass
                     

   # Upload to MongoDB
   fails = 0
   for doc in cvs_arr_to_upload:
      try:
         cvs_collection.insert_one(doc)
      except:
         fails = fails + 1

   print(fails)

                     