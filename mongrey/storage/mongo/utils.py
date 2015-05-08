# -*- coding: utf-8 -*-


def create_mongo_connection(conn_settings):
    
    from pymongo import uri_parser
    import mongoengine

    conn = dict([(k.lower(), v) for k, v in conn_settings.items() if v])

    if 'replicaset' in conn:
        conn['replicaSet'] = conn.pop('replicaset')

    # Handle uri style connections
    if "://" in conn.get('host', ''):
        uri_dict = uri_parser.parse_uri(conn_settings['host'])
        conn['db'] = uri_dict['database']

    return mongoengine.connect(conn.pop('db', 'test'), **conn)
