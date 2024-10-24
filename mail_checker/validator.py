import logging
import re
import dns.resolver

from .tld import tlds
from .const import suspicious_tempmail_nameservers, trusted_mx_servers, tempmail_mx_servers, public_email_providers
from .const import domain_typos, tld_typos
from .const import debug_mode

logging.basicConfig(level=logging.DEBUG if debug_mode else logging.INFO)

class Validator:
  def __init__(self, email: str):
    self.email = email
    self.score = 8
    self.reasons = list()
    self.disposable = False # temp email
    self.public_domain = False # eg. gmail.com
    self.dns_exists = True
    self.suggested_domain = None
    self.logger = logging.getLogger(__name__)

  @property
  def dict(self):
    result = {
      'email': self.email,
      'valid': self.score >= 5,
      'score': self.score,
      'reasons': self.reasons,
      'disposable': self.disposable,
      'public_domain': self.public_domain,
    }
    if self.suggested_domain:
      result['did_you_mean'] = self.suggested_domain
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

  def step_0100_has_at_symbol(self):
    result = '@' in self.email
    if not result:
      self.penalty(10, 'No @ symbol found in email')

  def step_0101_has_only_one_at_symbol(self):
    result = self.email.count('@') == 1
    if not result:
      self.penalty(10, 'Multiple @ symbols found in email')
    return result

  def step_0102_has_valid_domain(self):
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

    if domain in public_email_providers:
      self.public_domain = True
      self.score += 1

    return result

  def step_0300_is_tld_allowed(self):
    """ This supports domain.co.uk but not sub.domain.co.uk """
    tld_supported = 2
    result = len(self.domain.split('.')) - 1 > tld_supported
    if result:
      self.penalty(1, f'More than {tld_supported} subdomain found in email domain')

  def step_0301_is_tld_valid(self):
    """ Check if the TLD is valid. """
    tld = self.domain.split('.')[-1].lower()
    result = tld in tlds
    if not result:
      self.penalty(7, f'Invalid TLD found in email domain: {tld}')
      if tld.startswith('co') and len(tld) == 3:
        self.suggested_domain = f"{self.domain.split('.')[0]}.com"
      self.dns_exists = False
    return result

  def step_0350_has_domain_typosquatting(self):
    """ Misplaced letters that generate a different domain than the expected. """

    check = self.domain
    parts = check.split('.', 1)
    domain_tld = parts[-1]
    tld_fixed = False
    is_invalid = False

    # remove digits from the beginning or ending of domain
    if check[0].isdigit():
      check = check.lstrip('0123456789')
      tld_fixed = True

    if check[-1].isdigit():
      check = check.rstrip('0123456789')
      tld_fixed = True

    # if earlier we check TLD is invalid, we already have a low score.
    # probably we will have a typo of COM.
    if self.score < 2:
      for tld, typos in tld_typos.items():
        if domain_tld in typos:
          # fix TLD
          check = ".".join([parts[0], tld])
          tld_fixed = True
          break

    for domain, typos in domain_typos.items():
      # Skip if match
      if check == domain:
        if tld_fixed:
          self.logger.debug(f"Match wrong TLD: {self.domain} - {domain}")
          is_invalid = True
        else:
          return True

      # xgmail.com
      elif check.endswith(domain) and (len(check) - len(domain)) <= 2:
        self.logger.debug(f"Match with prefix in domain name: {self.domain} - {domain}")
        is_invalid = True
      elif check.startswith(domain.split('.')[0]) and domain.endswith(f".{domain_tld}") and (len(check) - len(domain)) <= 2:
        self.logger.debug(f"Match with suffix in domain name: {self.domain} - {domain}")
        is_invalid = True
      # NOTE: Be careful with .com.pe and other ccTLDs!
      elif check.startswith(domain) and (len(check) - len(domain)) > 0:
        self.logger.debug(f"Match with suffix in full TLD: {self.domain} - {domain}")
        is_invalid = True
      elif check in typos:
        self.logger.debug(f"Typo found in: {check} - {domain}")
        is_invalid = True

      if is_invalid:
        self.penalty(11, f'Typosquatting detected: {domain}')
        self.suggested_domain = domain
        return False

  def step_0400_has_valid_username(self):
    """ Check if the username part of the email is valid. """
    regex = r'^[A-Za-z0-9._%+-]+$'
    result = re.match(regex, self.username) is not None
    if not result:
      self.penalty(10, 'Invalid characters in email username')
    if len(self.username) <= 1:
      self.penalty(1, 'Username too short')
    return result

  def step_0401_is_not_robot_or_waste_bin(self):
    unwanted_usernames = [
      'no-reply', 'noreply', 'donotreply', 'do-not-reply',
      'help', 'postmaster', 'webmaster', 'hostmaster', 'abuse',
      'spam', 'junk', 'trash', 'robot', 'bot'
    ]
    result = self.username not in unwanted_usernames
    if not result:
      self.penalty(2, 'Email username is a robot name')
    return result

  def step_0402_username_is_not_alias_box(self):
    """ You can create multiple emails with email+alias@gmail.com """
    result = '+' not in self.username
    if not result:
      self.penalty(1, 'Email username has an alias')
    return result

  def step_0000_is_not_empty(self):
    result = bool(self.email.strip())
    if not result:
      self.penalty(10, 'Email is empty')
    return result

  def step_1000_domain_resolve_soa(self):
    if self.public_domain or not self.dns_exists:
      return
    try:
      resolve = dns.resolver.resolve(self.domain, 'SOA')
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
      self.penalty(10, 'Domain does not exist')
      self.dns_exists = False
    except (dns.resolver.LifetimeTimeout):
      self.penalty(8, 'Timeout while checking nameservers')

  def step_1001_domain_resolve_suspicious_tempmail_nameservers(self):
    """ This can be used to check if the domain is using a suspicious tempmail nameserver. """
    if self.public_domain or not self.dns_exists:
      return
    try:
      resolve = dns.resolver.resolve(self.domain, 'SOA')
      entry = resolve.response.answer[0]

      for ns in suspicious_tempmail_nameservers:
        if ns in str(entry):
          self.penalty(7, f'Nameserver found, suspicious tempmail: {ns}')
          self.disposable = True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
      self.penalty(10, 'Domain does not exist')
      self.dns_exists = False
    except (dns.resolver.LifetimeTimeout):
      self.penalty(8, 'Timeout while checking nameservers')

  def step_1100_domain_resolve_mx(self):
    if self.public_domain or not self.dns_exists:
      return
    try:
      resolve = dns.resolver.resolve(self.domain, 'MX')
      for rdata in resolve:
        if len(str(rdata.exchange)) < 3:
          self.penalty(7, 'Invalid MX record found')
          break
    except dns.resolver.NoAnswer:
      self.penalty(10, 'Cannot send email, no MX record found for domain')
    except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
      self.penalty(10, 'Domain does not exist')
      self.dns_exists = False
    except (dns.resolver.LifetimeTimeout):
      self.penalty(8, 'Timeout while checking nameservers')
    return True

  def step_1101_domain_check_mx_tempmail(self):
    """ Check if MX belongs to known tempmail providers. """
    if self.public_domain or not self.dns_exists:
      return
    try:
      resolve = dns.resolver.resolve(self.domain, 'MX')
      for rdata in resolve:
        for tempmail_mx in tempmail_mx_servers:
          if tempmail_mx in str(rdata.exchange):
            self.penalty(7, f'Tempmail MX found: {tempmail_mx}')
            self.disposable = True
            return False
        for trusted_mx in trusted_mx_servers:
          if trusted_mx in str(rdata.exchange):
            self.logger.debug(f"Mail in trusted MX: {trusted_mx}")
            self.score += 2
            # just one bump increase
            return True
    except dns.resolver.NoAnswer:
      self.penalty(10, 'Cannot send email, no MX record found for domain')
    except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
      self.penalty(10, 'Domain does not exist')
      self.dns_exists = False
    except (dns.resolver.LifetimeTimeout):
      self.penalty(8, 'Timeout while checking nameservers')

  def run(self):
    steps = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('step_')]
    for step in steps:
      self.logger.debug(f'Running {step.lstrip("step_").replace("_", " ")}')
      getattr(self, step)()
      if self.score < 0:
        return False
    return True