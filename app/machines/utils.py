import re

from sophize_datamodel import (Argument, Language, ProofResponse,
                               MetaLanguage, Proposition, TruthValue)

DONT_KNOW_RESPONSE = ProofResponse.from_dict(
    {'truthValue': TruthValue.UNKNOWN})
TRUE_STUB_RESPONSE = ProofResponse.from_dict({'truthValue': TruthValue.TRUE})
FALSE_STUB_RESPONSE = ProofResponse.from_dict(
    {'truthValue': TruthValue.FALSE})
ID4_SCHEMA = re.compile(r'^\w+\.(\d+)\.(\d+).(\d+).(\d+)$')


def get_arg_id(conclusionAndPremises=[]):
    return '-'.join(conclusionAndPremises)


def get_arg_id_premise_machine(conclusion: str, premise_machine: str):
    return 'PM' + conclusion + '-' + premise_machine


def prop_id_to_res_id(prop_id: str):
    return prop_id[:-2] if prop_id.endswith(':N') else prop_id


def string_to_int(s: str):
    try:
        return int(s)
    except ValueError:
        return None


def string_to_argument(arg_id: str) -> Argument:
    ephemeral_id = arg_id.replace('#', '').replace('/', '')
    if arg_id.startswith('PM'):
        conclusion_end = arg_id.find('-')
        conclusion = arg_id[2:conclusion_end]
        premise_machine = arg_id[conclusion_end+1:]
        return Argument.from_dict({
            'metaLanguage': MetaLanguage.INFORMAL,
            'language': Language.INFORMAL,
            'conclusion': '#P~' + conclusion,
            'premiseMachine': premise_machine,
            'ephemeralPtr': '#A~' + ephemeral_id
        })
    else:
        props = arg_id.split('-')
        return Argument.from_dict({
            'metaLanguage': MetaLanguage.INFORMAL,
            'language': Language.INFORMAL,
            'conclusion': '#P~' + props[0],
            'premises': ['#P~'+s for s in props[1:]],
            'ephemeralPtr': '#A~' + ephemeral_id
        })


def get_id_r_e_o1po2(r: int, o1: int, o2: int, result_first: bool) -> str:  # o1 + o2 = r
    if r == o1+o2 and o2 == 1 and result_first:
        return 'defn.{}'.format(r)
    return 'sum.{}.{}.{}.{}'.format(1 if result_first else 0, r, o1, o2)


def get_id_ap1_e_bpcp1_t1(a: int, b: int, c: int) -> str:   # 9 + 1 = 7 + (2 + 1)
    return 'temp.1.{}.{}.{}'.format(a, b, c)


def get_id_ap1_e_bpcp1_t2(a: int, b: int, c: int) -> str:  # (9 + 1) = (7 + 2) + 1
    return 'temp.2.{}.{}.{}'.format(a, b, c)


def string_to_proposition(prop_id: str) -> Proposition:
    statement = ''
    if prop_id.startswith('sum'):
        matcher = ID4_SCHEMA.match(prop_id)
        result_first = True if string_to_int(matcher.group(1)) == 1 else False
        r = string_to_int(matcher.group(2))
        o1 = string_to_int(matcher.group(3))
        o2 = string_to_int(matcher.group(4))
        if result_first:
            statement = '{} = {} + {}'.format(r, o1, o2)
        else:
            statement = '{} + {} = {}'.format(o1, o2, r)

    elif prop_id.startswith('defn.'):
        defined_num = int(prop_id[5:])
        statement = '{} = {} + 1'.format(defined_num, defined_num - 1)
    elif prop_id.startswith('temp'):
        matcher = ID4_SCHEMA.match(prop_id)
        temp_type = string_to_int(matcher.group(1))
        a = string_to_int(matcher.group(2))
        b = string_to_int(matcher.group(3))
        c = string_to_int(matcher.group(4))
        if temp_type == 1:
            statement = '{} + 1 = {} + ({} + 1)'.format(a, b, c)
        else:
            statement = '({}) + 1 = ({} + {}) + 1'.format(a, b, c)

    return Proposition.from_dict({
        'maetaLanguage': MetaLanguage.INFORMAL,
        'language': Language.INFORMAL,
        'statement': statement,
        'ephemeralPtr': '#P~' + prop_id
    })
