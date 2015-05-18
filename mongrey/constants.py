# -*- coding: utf-8 -*-

_ = lambda s:s

ERRORS_URL_BASE = "http://mongrey.readthedocs.org/en/latest/errors.html"

SESSION_LANG_KEY = "current_lang"
SESSION_TIMEZONE_KEY = "current_tz"

GREY_KEY_HIGH = "high"
GREY_KEY_MED = "med"
GREY_KEY_LOW = "low"
GREY_KEY_VERY_LOW = "vlow"
GREY_KEY_SPECIAL = "special"

GREY_KEY = (
    (GREY_KEY_VERY_LOW, _(u"IP Address")),
    (GREY_KEY_LOW, _(u"IP Address + Domain Recipient")),
    (GREY_KEY_MED, _(u"IP Address + Email Recipient")),
    (GREY_KEY_HIGH, _(u"IP Address + Email Sender + Email Recipient")),
    (GREY_KEY_SPECIAL, _(u"Email Sender + Email Recipient")),
)

FIELD_CLIENT_ADDRESS = ('client_address', _(u"IP Address"))
FIELD_CLIENT_NAME = ('client_name', _(u"Hostname"))
FIELD_SENDER = ('sender', _(u"Email Sender"))
FIELD_RECIPIENT = ('recipient', _(u"Email Recipient"))
FIELD_COUNTRY = ('country', _(u"Country Code"))
FIELD_HELO_NAME = ('helo_name', _(u"Helo Name"))

ALL_FIELDS = (
    FIELD_CLIENT_ADDRESS,             
    FIELD_CLIENT_NAME,
    FIELD_SENDER,
    FIELD_RECIPIENT,
    FIELD_COUNTRY,
    FIELD_HELO_NAME              
) 

WL_FIELDS = (
    FIELD_COUNTRY,
    FIELD_CLIENT_ADDRESS,             
    FIELD_CLIENT_NAME,
    FIELD_SENDER,
    FIELD_RECIPIENT,
    FIELD_HELO_NAME
)

BL_FIELDS = (
    FIELD_COUNTRY,
    FIELD_CLIENT_ADDRESS,
    FIELD_CLIENT_NAME,
    FIELD_SENDER,
    FIELD_RECIPIENT,
    FIELD_HELO_NAME
)

POLICY_FIELDS = (
    FIELD_COUNTRY,
    FIELD_CLIENT_ADDRESS,
    FIELD_CLIENT_NAME,
    FIELD_SENDER,
    FIELD_RECIPIENT,
    FIELD_HELO_NAME
)

ACCEPT_PROTOCOL_STATES = ['rcpt']

ACCEPT_ACTIONS = ["DUNNO", "421", "521", "REJECT", "WARN", "INFO"]

#request=smtpd_access_policy
POSTFIX_PROTOCOL = {

    "valid_fields": [
        "request",                      #Postfix version 2.1 and later
        "protocol_state",
        "protocol_name",
        "helo_name",
        "queue_id",
        "sender",
        "recipient",                    #available in the "RCPT TO" stage and "DATA" and "END-OF-MESSAGE" stages if Postfix accepted only one recipient
        "recipient_count",              #non-zero only in the "DATA" and "END-OF-MESSAGE" stages
        "client_address",
        "client_name",
        "reverse_client_name",
        "instance",
        "sasl_method",                  #Postfix version 2.2 and later
        "sasl_username",
        "sasl_sender",
        "size",
        "ccert_subject",
        "ccert_issuer",
        "ccert_fingerprint",
        "encryption_protocol",          #Postfix version 2.3 and later
        "encryption_cipher",
        "encryption_keysize",
        "etrn_domain",
        "stress",                       #Postfix version 2.5 and later                            
        "ccert_pubkey_fingerprint",     #Postfix version 2.9 and later
        "client_port"                   #Postfix version 3.0 and later
    ],
    
    "valid_protocol_state" : [
            'CONNECT', 
            'EHLO', 
            'HELO', 
            'MAIL', 
            'RCPT', 
            'DATA', 
            'END-OF-MESSAGE', 
            'VRFY', 
            'ETRN'
    ],
    
    "valid_protocol_name" : ['SMTP', 'ESMTP']
}

NOT_FOUND = -1
SENDER_FOUND = 1
RECIPIENT_FOUND = 2

API_KEY = "api_key"