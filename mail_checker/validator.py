import logging
import re

from .tld import tlds

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Validator:
  def __init__(self, email: str):
    self.email = email
    self.score = 8
    self.reasons = list()

  @property
  def dict(self):
    result = {
      'email': self.email,
      'valid': self.score >= 5,
      'score': self.score,
      'reasons': self.reasons,
    }
    # if self.reasons:
    #  result['reasons'] = self.reasons
    return result

  def is_valid_email(email):
    # Simple regex for email validation
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email) is not None

  @property
  def domain(self) -> str:
    return self.email.split('@')[-1] or ""

  @property
  def username(self) -> str:
    return self.email.split('@')[0] or ""

  def penalty(self, score: int, reason: str) -> bool:
    self.score -= score
    self.reasons.append(reason)
    return False

  def step_has_at_symbol(self):
    result = '@' in self.email
    if not result:
      self.penalty(10, 'No @ symbol found in email')

  def step_has_only_one_at_symbol(self):
    result = self.email.count('@') == 1
    if not result:
      self.penalty(10, 'Multiple @ symbols found in email')
    return result

  def step_has_valid_domain(self):
    """ By default, we expect the domain to have at least 1 TLD. """
    domain = self.domain
    result = '.' in domain and len(domain.split('.')) > 1
    if not result:
      self.penalty(10, 'No TLD found in email domain')

    parts = domain.split('.', 1)
    result = result and len(parts[-1]) >= 2
    if not result:
      self.penalty(10, 'TLD is too short')
    if len(parts[0]) < 2:
      self.penalty(2, 'Domain name is too short')

    if result and len(domain) < 4 or len(domain) > 63:
      self.penalty(10, 'Invalid domain length')
    if result and domain.startswith("-") or domain.split('.')[0].endswith("-"):
      self.penalty(5, 'Invalid domain character')

    return result
  
  def step_is_tld_allowed(self):
    """ This supports domain.co.uk but not sub.domain.co.uk """
    tld_supported = 2
    result = len(self.domain.split('.')) - 1 > tld_supported
    if result:
      self.penalty(1, f'More than {tld_supported} subdomain found in email domain')

  def step_is_tld_valid(self):
    """ Check if the TLD is valid. """
    tld = self.domain.split('.')[-1].lower()
    result = tld in tlds
    if not result:
      self.penalty(10, f'Invalid TLD found in email domain: {tld}')
    return result

  def step_has_valid_username(self):
    """ Check if the username part of the email is valid. """
    regex = r'^[A-Za-z0-9._%+-]+$'
    result = re.match(regex, self.username) is not None
    if not result:
      self.penalty(10, 'Invalid characters in email username')
    if len(self.username) <= 1:
      self.penalty(1, 'Username too short')
    return result
  
  def step_is_not_robot_or_waste_bin(self):
    unwanted_usernames = [
      'no-reply', 'noreply', 'donotreply', 'do-not-reply',
      'help', 'postmaster', 'webmaster', 'hostmaster', 'abuse',
      'spam', 'junk', 'trash', 'robot', 'bot'
    ]
    result = self.username not in unwanted_usernames
    if not result:
      self.penalty(2, 'Email username is a robot name')
    return result

  def step_username_is_not_alias_box(self):
    """ You can create multiple emails with email+alias@gmail.com """
    result = '+' not in self.username
    if not result:
      self.penalty(1, 'Email username has an alias')
    return result

  def step_is_not_empty(self):
    result = bool(self.email.strip())
    if not result:
      self.penalty(10, 'Email is empty')
    return result

  def run(self):
    steps = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('step_')]
    for step in steps:
      logger.debug(f'Running {step.lstrip("step_").replace("_", " ")}')
      getattr(self, step)()
      if self.score < 0:
        return False
    return True