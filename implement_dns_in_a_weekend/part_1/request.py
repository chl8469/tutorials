import enum
from dataclasses import dataclass
import dataclasses
import random
import struct


@dataclass
class DNSHeader:
    id: int
    flags: int
    num_questions: int = 0
    num_answers: int = 0
    num_authorities: int = 0
    num_additionals: int = 0


class DNSType(enum.IntEnum):
    A: int = 1  # a host address
    NS: int = 2  # an authoritative name server
    MD: int = 3  # a mail destination (Obsolete - use MX)
    MF: int = 4  # a mail forwarder (Obsolete - use MX)
    CNAME: int = 5  # the canonical name for an alias
    SOA: int = 6  # marks the start of a zone of authority
    MB: int = 7  # a mailbox domain name (EXPERIMENTAL)
    MG: int = 8  # a mail group member (EXPERIMENTAL)
    MR: int = 9  # a mail rename domain name (EXPERIMENTAL)
    NULL: int = 10  # a null RR (EXPERIMENTAL)
    WKS: int = 11  # a well known service description
    PTR: int = 12  # a domain name pointer
    HINFO: int = 13  # host information
    MINFO: int = 14  # mailbox or mail list information
    MX: int = 15  # mail exchange
    TXT: int = 16  # text strings


@dataclass
class DNSQuestion:
    name: bytes
    type_: int
    class_: int


def header_to_bytes(header):
    fields = dataclasses.astuple(header)
    # there are 6 `H`s because there are 6 fields
    return struct.pack("!HHHHHH", *fields)


def question_to_bytes(question):
    return question.name + struct.pack("!HH", question.type_, question.class_)


def encode_dns_name(domain_name):
    encoded = b""
    for part in domain_name.encode("ascii").split(b"."):
        encoded += bytes([len(part)]) + part
    return encoded + b"\x00"


def build_query(domain_name, record_type):
    name = encode_dns_name(domain_name)
    id_ = random.randint(0, 65535)
    recursion_desired = 1 << 8
    header = DNSHeader(id=id_, num_questions=1, flags=recursion_desired)
    question = DNSQuestion(name=name, type_=record_type, class_=DNSType.A)
    return header_to_bytes(header) + question_to_bytes(question)
