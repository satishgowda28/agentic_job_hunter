from .hirist import HiristParser
from .linkedin import LinkedInParser

_parsers = [HiristParser(), LinkedInParser()]

PARSER_REGISTRY = {parser.sender_email: parser for parser in _parsers}


def get_parser(sender_email: str):
    """Returns the correct parser for the email, or None if unsupported."""
    return PARSER_REGISTRY.get(sender_email)
