import string

suspicious_tempmail_nameservers = [
  ".dnsowl.com", # temp-mail.org
]

trusted_mx_servers = [
  "alt1.aspmx.l.google.com",
  "alt2.aspmx.l.google.com",
  "alt3.aspmx.l.google.com",
  "alt4.aspmx.l.google.com",
  "aspmx.l.google.com",
  "aspmx2.googlemail.com",
  "aspmx3.googlemail.com",
  "aspmx4.googlemail.com",
  "aspmx5.googlemail.com",
  ".mail.protection.outlook.com",
  ".olc.protection.outlook.com",
]

# https://www.usercheck.com/providers
tempmail_mx_servers = [
  "mx2.den.yt",
  "mx1.icdn.be",
  "generator.email",
  "tempm.com",
  "emailfake.com",
  "email-fake.com",
  "mail.ggez.team",
  "mx.cse445.com",
  "mx1.simplelogin.co",
  "mx2.simplelogin.co",
  "smtp.yopmail.com",
  "gpa.lu",
  "mail.anonaddy.me",
  "mail2.anonaddy.me",
  "inbound-smtp.skiff.com",
  "in.mail.tm",
  "mx.discard.email",
  "mx.moakt.com",
  "mx.temp-mail.io",
  "mx2.temp-mail.io",
  "prd-smtp.10minutemail.com",
  "loti3.papierkorb.me",
  "us2.mx1.mailhostbox.com",
  "us2.mx2.mailhostbox.com",
  "us2.mx3.mailhostbox.com",
  "mail.mailinator.com",
  "mail2.mailinator.com",
  "mailnesia.com",
  "mx.1secmail.com"
]

public_email_providers = [
  "gmail.com",
  "yahoo.com",
  "outlook.com",
  "hotmail.com",
  "hotmail.es",
  "aol.com",
  "icloud.com",
  "mail.ru",
  "mail.com",
  "zoho.com",
  "protonmail.com",
  "gmx.com",
  "yandex.com",
  "fastmail.com",
  "hey.com",
  "tutanota.com",
  "rediffmail.com",
  "me.com",
  "mac.com",
  "live.com",
  "msn.com",
  "comcast.net",
  "verizon.net",
  "att.net",
  "bellsouth.net",
  "charter.net",
  "cox.net",
  "earthlink.net",
  "juno.com",
  "mindspring.com",
  "netzero.net",
  "rocketmail.com",
  "ymail.com",
]

typos_gmail = [
  "com.gmail",
  "g.mail",
  "gmail.com.email",
  "gmai.com",
  "gmail.om",
  "gmail.co",
  "gmail.con",
  "gmail.coom",
  "gomail.com",
  "gmail.cm",
  "gmsil.com",
  "gmill.com",
  "gmill.con",
  "gamil.ccom",
  "gmail.com.ar", # !
  "gmail.com.br", # !
  "gamil.com.br",
  "gmailcom.br",
  "gamial.com",
  "gmilcom.com",
  "gmael.com",
  "gimal.com",
  "gmil.com",
  "gemal.com",
  "gemil.com",
  "geml.com",
  "gmaile.com",
  "gqmil.com",
  "gmei.com",
  "gmeli.com",
  "gmaim.com",
  "gamail.com",
  "gtmail.com",
  "gmamail.com",
  "gmaol.com",
  "gmail.coml",
  "gmail.cl",
  "imail.com",
  "gimail.com",
  "amil.com",
  "agmail.com",
  "gamul.com",
  "gmaip.com",
  "gmain.com",
  "gamil.com",
  "fmail.com",
  "jmail.com",
  "jimail.com",
  "igmail.com",
  "imalg.com",
  "imalg.con",
  "sgmail.com",
  "hmail.com",
  "gmaii.com",
  "gilam.com",
  "mgail.com",
  "gilm.com",
  "gemeio.com",
  "gami.com",
  "gmqil.com",
  "gamol.com",
  "gmiaal.com",
  "gemai.com",
  "gamli.com",
  "gmail.co.com",
  "gmail.com.pe",
  "gmail.l.com",
  "gmilcom.com",
  "ymail.com", # WARNING! THIS IS YAHOO REAL, but it's a common typo
]

typos_hotmail = [
  "rotmail.com",
  "votmail.com",
  "jotmail.com",
  "gotmail.com",
  "hotmaim.com",
  "hotmaip.com",
  "hotmaul.com",
  "hotemail.com",
  "ghotmail.com",
  "homail.com",
  "hotml.com",
  "hotmail.c.com",
  "otmai.com",
  "hotmail.con",
  "hotmail.cm",
  "xn--hotmai-1wa.com",
]

typos_icloud = [
  "icloud.con",
  "icloud.cm",
  "jcloud.com",
  "iclouf.com",
  "iclud.com",
  "iclou.com",
  "icoud.com",
  "icluod.com",
  "iclound.com",
  "i.cloud.com",
]

typos_yahoo = [
  "uahoo.com",

]

domain_typos = {
  "gmail.com": typos_gmail,
  "hotmail.com": typos_hotmail,
  "icloud.com": typos_icloud,
}

def generate_typos(word):
  typos = [f"{word}{word}"]
  for i, char in enumerate(word):
    for replacement in string.ascii_lowercase:
      if char != replacement:
        typos.append(word[:i] + replacement + word[i+1:])
  return typos

tld_typos = {
  "com": generate_typos("com"),
  "net": generate_typos("net"),
  "org": generate_typos("org"),
}