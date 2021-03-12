import csv
import datetime
import ipaddress
import os
import logging

class GetASN:

    _URL            = 'https://iptoasn.com/'
    _DB_FILENAME    = 'ip2asn-v4.tsv'
    _MAX_DAYS       = 7
    _CACHE_MAX_SIZE    = 1000

    def __init__(self, path = '.'):

        self._CACHE         = {}
        self._cache_reuse   = 0
        self._add_cache     = True
        
        db_full_path = os.path.abspath(os.path.join(path, GetASN._DB_FILENAME))
        logging.debug(f"GetASN working with {db_full_path!r}.")
        db_mod_time = os.path.getmtime(db_full_path)
        if (datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(db_mod_time)).days > GetASN._MAX_DAYS:
            logging.warning(f"ASN database is more than {GetASN._MAX_DAYS} days old. You might want to download a fresh one from {GetASN._URL}.")
        
        # ['1.0.0.0', '1.0.0.255', '13335', 'US', 'CLOUDFLARENET - Cloudflare, Inc.']

        self._DATA = {}
        with open(db_full_path, encoding='utf-8') as f:
            csv_r = csv.reader(f, delimiter='\t')
            for row in csv_r:
                self._DATA[ipaddress.ip_address(row[1])] = (ipaddress.ip_address(row[0]), row[4])
    
    def lookup(self, ipv4):

        if isinstance(ipv4, str):
            ipv4 = ipaddress.ip_address(ipv4)
        
        for top in self._CACHE:
            if self._CACHE[top][0] <= ipv4 <= top:
                self._cache_reuse += 1
                return self._CACHE[top][1]
        
        for top in self._DATA:
            if ipv4 < top:
                if self._add_cache:
                    self._CACHE[top] = self._DATA[top]
                    if len(self._CACHE) == GetASN._CACHE_MAX_SIZE:
                        self._add_cache = False
                        logging.warning(f"ASN lookup cache has reached maximum size ({GetASN._CACHE_MAX_SIZE}); won't add to cache.")
                        logging.warning("Performance may slow down.")
                return self._DATA[top][1]
        
        return None


if __name__ == '__main__':
    
    logging.getLogger().setLevel(logging.DEBUG)
    get_asn = GetASN()
    print(f"1.0.0.5: {get_asn.lookup('1.0.0.5')}")
    print(f"8.8.8.8: {get_asn.lookup('8.8.8.8')}")
