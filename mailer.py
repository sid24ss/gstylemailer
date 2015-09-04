import cPickle as pickle
import os, sys
import random
from parse_styles import GStyleGuide, GStyleGuideParser

try:
	from settings import *
except:
	print 'Cannot find the settings file. Quitting.'
	sys.exit(1)

# email related imports
import smtplib
from email.mime.text import MIMEText

# Send the message via our own SMTP server.
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

def mail_item(mail_id, item, snipped_num):
	# render the item with styles
	# Create a text/plain message
	msg_body = item.body
	msg_body += '\n<link rel="stylesheet" type="text/css" href="https://google-styleguide.googlecode.com/svn/trunk/styleguide.css">'
	msg = MIMEText(msg_body, 'html')
	me = MAILER_FROM
	# you == the recipient's email address
	msg['Subject'] = '[GStyleGuideMailer] Snippet #%d' % (snipped_num)
	msg['From'] = me
	msg['To'] = mail_id
	try:
		server.sendmail(me, [mail_id], msg.as_string())
		return True
	except:
		return False


STYLES_FILENAME = 'data/parsed_styles.p'
MAIL_CACHE = 'data/mail_cache.p'

# if parsed file exists, load them. If not, invoke the parser.
parsed_styles = None
if os.path.isfile(STYLES_FILENAME):
	parsed_styles = pickle.load(open(STYLES_FILENAME,'rb'))
else:
	parser = GStyleGuideParser('resources/style-page.html')
	parser.parse_file()
	parsed_styles = parser.get_style_list()
	# save for future use.
	parser.save_as_pickle()

NUM_STYLES = len(parsed_styles)

# load list of emails to send mails to
mailing_list = None
with open(MAILING_LIST, 'rb') as mlistfile:
	mailing_list = mlistfile.readlines()
	mailing_list = [m.strip() for m in mailing_list]

# create a dict {mail_id : [items_mailed]}
mail_cache = {m:[] for m in mailing_list}

# Update from cache
if os.path.exists(MAIL_CACHE):
	mail_cache_saved = pickle.load(open(MAIL_CACHE, 'rb'))
	# filter out items that are no longer in the mailing_list
	mail_cache_saved = {k:v for (k,v) in mail_cache_saved.iteritems() if k in mail_cache}
	# update our current list with the cache
	mail_cache.update(mail_cache_saved)

# print mail_cache
master_set = set(range(NUM_STYLES))
for (mail_id, mailed_items) in mail_cache.iteritems():
	# print mail_id, mailed_items
	allowed_set = master_set - set(mailed_items)
	# if we have already mailed every item, skip
	if not allowed_set:
		continue
	selected_item = random.sample(allowed_set, 1)[0]
	while selected_item == NUM_STYLES - 1 and len(allowed_set) > 1:
		selected_item = random.sample(allowed_set, 1)[0]
	if not mailed_items:
		# first mail
		selected_item = 0
	success = mail_item(mail_id, parsed_styles[selected_item], len(mailed_items)+1)
	if success:
		mail_cache[mail_id].append(selected_item)

# save mail_cache
pickle.dump(mail_cache, open(MAIL_CACHE, 'w'))

server.quit()

