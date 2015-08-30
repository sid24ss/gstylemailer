from bs4 import BeautifulSoup
import cPickle as pickle


class GStyleGuide(object):
  def append(self, s):
    self.body += '\n' + s

  def __init__(self):
    self.body = ''

class GStyleGuideParser(object):
  def __init__(self, filename):
    self._filename = filename
    self.styles = list()
    self.get_text()

  def get_text(self):
    style_file = open(self._filename, 'rb')
    self._full_text = style_file.read()
    style_file.close()

  def parse_file(self):
    self._soup = BeautifulSoup(self._full_text, 'html.parser')
    # get the first h2
    break_style = True
    styleguide = GStyleGuide()
    h2_flag = False
    nextNode = self._soup.h2
    num_styles = 0
    while nextNode.name != 'hr':
      nextNode
      if nextNode.name == 'h2':
        break_style = True
        h2_flag = True
      # if not nextNode.name:
      #   continue
      if nextNode.name == 'h3' and not h2_flag:
        # now following a h3. break into a new style
        break_style = True
      if nextNode.name == 'h3' and h2_flag:
        # do not break into new style.
        h2_flag = False
      # everything else just gets appended.
      if break_style:
        # add old one to list
        self.styles.append(styleguide)
        # start accumulating a new one
        styleguide = GStyleGuide()
        break_style = False
        num_styles += 1
        print 'accumulating style number : %d' % num_styles
      styleguide.append(str(nextNode))
      nextNode = nextNode.nextSibling

    # append the last one
    self.styles.append(styleguide)
    # clean up
    self.styles = [s for s in self.styles if s.body]

  def get_style_list(self):
    return self.styles

  def save_as_pickle(self):
    pickle.dump(self.styles, open('data/parsed_styles.p', 'w'))

# parser = GStyleGuideParser('style-page.html')
# parser.parse_file()
# styles = parser.get_style_list()
# parser.save_as_pickle()
