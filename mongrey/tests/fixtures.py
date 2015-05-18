# -*- coding: utf-8 -*-

import datetime
from pprint import pprint as pp
import uuid
import random
import arrow
from faker import Factory

from mongrey import constants, utils

def fixtures(models):
    
    faker = Factory.create('en')
    last = arrow.utcnow().floor('day')
    first = last.replace(days=-2)
        
    local_domains = [faker.domain_name() for i in range(10)]
    local_senders = ["%s@%s" % (faker.user_name(), domain) for domain in local_domains]
    local_mx = ["mx@%s" % domain for domain in local_domains]
    local_ip = [faker.ipv4() for i in range(10)] + [faker.ipv6() for i in range(10)]
    
    remote_domains = [faker.domain_name() for i in range(100)]
    remote_senders = ["%s@%s" % (faker.user_name(), domain) for domain in remote_domains]
    remote_mx = ["mx@%s" % domain for domain in local_domains]
    remote_ip = [faker.ipv4() for i in range(10)] + [faker.ipv6() for i in range(10)]
    
    #print "du : ", first, " Au : ", last
    
    policies = ['default', 'partner', 'china']
    
    doc_created = 0
    doc_error = 0
    
    for date_debut, date_fin in arrow.Arrow.span_range('hour', first, last):

        """        
        domain_sender = random.choice(local_domains + remote_domains)
        if domain_sender in local_domains:
            sender = random.choice(local_senders)
            recipient = random.choice(remote_senders)
            client_name = random.choice(local_mx)
            client_address = random.choice(local_ip)            
        else:
            sender = random.choice(remote_senders)
            recipient = random.choice(local_senders)
            client_name = random.choice(remote_mx)
            client_address = random.choice(remote_ip)
        """            

        sender = random.choice(remote_senders)
        recipient = random.choice(local_senders)
        client_name = random.choice(remote_mx)
        client_address = random.choice(remote_ip)            
            
        protocol = {
            'instance': uuid.uuid4(),
            'client_address': client_address,
            'client_name': client_name,
            'sender': sender,
            'recipient': recipient,
        }
    
        greylist_key = random.choice(dict(constants.GREY_KEY).keys())
        key = utils.build_key(protocol, greylist_key=greylist_key)
    
        kwargs = {}
        kwargs['protocol'] = protocol
        kwargs['key'] = key
        kwargs['timestamp'] = date_debut.datetime
        kwargs['policy'] = random.choice(policies)
        kwargs['delay'] = float(random.randint(1, 3600))
        kwargs['rejects'] = random.randint(1, 100)
        kwargs['accepts'] = random.randint(10, 300)
        kwargs['expire_time'] = date_debut.datetime + datetime.timedelta(seconds=random.randint(3600, (35 * 86400)))
        """
        last_state = fields.DateTimeField()
        """
        
        msg = "client_address=%(client_address)s client_name=%(client_name)s sender=%(sender)s recipient=%(recipient)s" % kwargs['protocol']
        #print date_debut, msg
        #print date_debut, greylist_key, key, kwargs['policy'], kwargs['delay'], kwargs['expire_time']
        try:
            models.GreylistEntry(**kwargs).save()
            doc_created += 1
        except Exception, err:
            print str(err)
            doc_error += 1
        
    return {
        'first': first,
        'last': last,
        'doc_created': doc_created,
        'doc_error': doc_error,
    }

def main():
    #from mongrey.storage.mongo import models
    fixtures(None)

if __name__ == "__main__":
    main()