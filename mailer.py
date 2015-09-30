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
	# msg_body += '\n<link rel="stylesheet" type="text/css" href="https://google-styleguide.googlecode.com/svn/trunk/styleguide.css">'
	msg_body += '<style>\n'
	css = None
	with open('resources/styleguide.css', 'rb') as f:
		css = f.read()
	msg_body += css
	msg_body += '</style>'
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
# if a command line argument was passed, send an email to only that ID (assume there was just one ID)
# This can be used to send the initial email to the person that just signed up
if len(sys.argv) > 1:
	mail_id = sys.argv[1]
	mailing_list = [mail_id]
else:
	with open(MAILING_LIST, 'rb') as mlistfile:
		mailing_list = mlistfile.readlines()
		mailing_list = [m.strip() for m in mailing_list]

# create a dict {mail_id : [items_mailed]}
mail_cache = {m:[] for m in mailing_list}

mail_cache_saved = dict()
# Update from cache
if os.path.exists(MAIL_CACHE):
	mail_cache_saved = pickle.load(open(MAIL_CACHE, 'rb'))
	# get items from the saved cache that are relevant to the current mailing list
	mail_cache_current = {k:v for (k,v) in mail_cache_saved.iteritems() if k in mail_cache}
	# update our current list with the cache
	mail_cache.update(mail_cache_current)

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

# update the cache
mail_cache_saved.update(mail_cache)
# save mail_cache
pickle.dump(mail_cache_saved, open(MAIL_CACHE, 'w'))

server.quit()

