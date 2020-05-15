"""For handling machine requests for 'Number schema' machine (#sophize/M.l9L)."""
import copy
import re

from sophize_datamodel import Language, MachineRequest

from .utils import (DONT_KNOW_RESPONSE, FALSE_STUB_RESPONSE,
                    TRUE_STUB_RESPONSE, get_arg_id, get_id_r_e_o1po2,
                    string_to_argument, string_to_int, string_to_proposition)

NUMBER_SCHEMA = re.compile(r'^\s*(\d+)\s*=\s*(\d+)\s*\+\s*1\s*$')


def get_response(req: MachineRequest):
    """Respond to machine request for this machine."""
    proposition = req.proposition
    if proposition.language is not Language.INFORMAL:
        return DONT_KNOW_RESPONSE
    [defining_num, previous_num] = _get_statement_structure(
        proposition.statement, req.try_completing_proposition)

    if defining_num is None or previous_num is None or previous_num <= 0:
        return DONT_KNOW_RESPONSE
        
    response = TRUE_STUB_RESPONSE if defining_num == previous_num + \
        1 else FALSE_STUB_RESPONSE
    if not req.fetch_updated_proposition and not req.fetch_proof:
        return response

    response = copy.deepcopy(response)
    conclusion_id = get_id_r_e_o1po2(defining_num, previous_num, 1, True)
    response.resolved_proposition = string_to_proposition(conclusion_id)
    if not req.fetch_proof:
        return response

    if defining_num == previous_num + 1:
        argument = string_to_argument(get_arg_id([conclusion_id]))
        argument.argument_text = 'Definition of the number {}'.format(
            defining_num)
        response.proof_arguments = [argument]
    else:
        response.proof_arguments = [
            string_to_argument(get_arg_id([conclusion_id+":N"]))]
    return response


def _get_statement_structure(statement: str, try_completing_proposition: bool):
    matcher = NUMBER_SCHEMA.match(statement)
    if matcher is not None:
        return [string_to_int(matcher.group(1)), string_to_int(matcher.group(2))]
    if not try_completing_proposition:
        return [None, None]
    defining_num = string_to_int(statement)
    return [defining_num, defining_num - 1 if defining_num is not None else None]
