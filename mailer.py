import cPickle as pickle
import os
import random
from parse_styles import GStyleGuide, GStyleGuideParser


# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# Send the message via our own SMTP server, but don't include the
# envelope header.
server = smtplib.SMTP('localhost', 1025)

def mail_item(mail_id, item, item_num):
	# render the item with styles
	# Create a text/plain message
	msg = MIMEText(item.body)
	me = 'gstyleguidemailer@siddharthswaminathan.in'
	# you == the recipient's email address
	msg['Subject'] = '[GStyleGuideMailer] Snipped #%d' % (item_num+1)
	msg['From'] = me
	msg['To'] = mail_id
	server.sendmail(me, [mail_id], msg.as_string())



STYLES_FILENAME = 'data/parsed_styles.p'
MAIL_CACHE = 'data/mail_cache.p'
MAILING_LIST = 'mailing_list.txt'

# if parsed file exists, load them. If not, invoke the parser.
parsed_styles = None
if os.path.isfile(STYLES_FILENAME):
	parsed_styles = pickle.load(open(STYLES_FILENAME,'rb'))
else:
	parser = GStyleGuideParser('style-page.html')
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

# create a list of emails to send the mails to
mail_cache = {m:[] for m in mailing_list}
if os.path.exists(MAIL_CACHE):
	mail_cache_saved = pickle.load(open(MAIL_CACHE, 'rb'))
	mail_cache.update(mail_cache_saved)

# print mail_cache

master_set = set(range(NUM_STYLES))

for (mail_id, mailed_items) in mail_cache.iteritems():
	print mail_id, mailed_items
	allowed_set = master_set - set(mailed_items)
	selected_item = random.sample(allowed_set, 1)[0]
	mail_item(mail_id, parsed_styles[selected_item], len(mailed_items))
	mail_cache[mail_id].append(selected_item)

# save mail_cache
pickle.dump(mail_cache, open(MAIL_CACHE, 'w'))


server.quit()

