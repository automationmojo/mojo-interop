from typing import List

from mojo.interop.protocols.dns.dnsconst import DnsRecordClass, DnsRecordType

from mojo.interop.protocols.dns.dnsquestion import DnsQuestion

from mojo.interop.protocols.dns.dnsserver import DnsServer

def dns_query_name(name: str, rtype: DnsRecordType, rclass: DnsRecordClass):

    question = DnsQuestion(name, rtype, rclass)

    query_str = question.as_dns_string()

    return query_str

def dns_query_services(service_types: List[str], rtype: DnsRecordType=DnsRecordType.PTR, rclass: DnsRecordClass=DnsRecordClass.IN):
    
    service = DnsServer()
    
    service.start()

    service.wait()

    return
