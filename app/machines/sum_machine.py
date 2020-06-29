"""For handling requests for machine computing sum of natural numbers (#sophize/M.VQp).

The following example shows the proofs steps returned by the machine
    4 + 7 = 11           (SUM_COMMUTATIVITY)
    7 + 4 = 11           (EQUALITY_COMMUTATIVITY)
       11 = 7 + 4        (defn11, defn4)
 (10 + 1) = (7 + 3) +1   (SUM_ASSOCIATIVITY)
 (10) + 1 = (7 + 3) + 1  (ADDITION_PROPERTY_OF_EQUALITY)
       10 = 7 + 3        (defn10, defn3)
    9 + 1 = 7 + (2 + 1)  (SUM_ASSOCIATIVITY)
    (9+1) = (7 + 2) + 1  (ADDITION_PROPERTY_OF_EQUALITY)
        9 = 7 + 2        (defn9, defn2)
    8 + 1 = 7 + (1 + 1)  (SUM_ASSOCIATIVITY)
  (8) + 1 = (7 + 1) + 1  (defn8, ADDITION_PROPERTY_OF_EQUALITY)
"""
import copy
import re
from dataclasses import dataclass
from typing import List

from sophize_datamodel import Argument, Language, ProofRequest, Proposition

from machines_managed import NUMBER_MACHINE

from .utils import (DONT_KNOW_RESPONSE, FALSE_STUB_RESPONSE,
                    TRUE_STUB_RESPONSE, get_arg_id, get_arg_id_premise_machine,
                    get_id_ap1_e_bpcp1_t1, get_id_ap1_e_bpcp1_t2,
                    get_id_r_e_o1po2, prop_id_to_res_id, string_to_argument,
                    string_to_int, string_to_proposition)

SUM_SCHEMA = re.compile(r'^\s*(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)\s*$')
SUM_SCHEMA_RESULT_FIRST = re.compile(r'^\s*(\d+)\s*=\s*(\d+)\s*\+\s*(\d+)\s*$')
SUM_SCHEMA_INCOMPLETE = re.compile(r'^\s*(\d+)\s*\+\s*(\d+)\s*$')

SUM_COMMUTATIVITY = "#sophize/P_sum_commutative"
SUM_ASSOCIATIVITY = "#sophize/P_sum_associative"
EQUALITY_COMMUTATIVITY = "#sophize/P_eq_commutative"
ADDITION_PROPERTY_OF_EQUALITY = "#sophize/P_eq_addition"


@dataclass
class Proof:
    """Contains the set of 'propositions' and 'arguments' ids required for proof of 'conclusion'"""
    conclusion: str
    propositions: set
    arguments: set

    def get_propositions(self) -> List[Proposition]:
        """Return propositions from the proposition ids. Non-ephemeral refs are skipped."""
        return list(map(string_to_proposition,
                        filter(lambda x: not x.startswith('#'), self.propositions)))

    def get_arguments(self) -> List[Argument]:
        """Return arguments from the argument ids."""
        return list(map(string_to_argument, self.arguments))

    def add_top_level_argument(self, conclusion: str, premises: List[str]):
        """Add another argment to this proof. 
        This argument would use the existing proof info and prove a new conclusion."""
        prop_ids = [conclusion, *premises]
        self.conclusion = conclusion
        self.arguments.add(get_arg_id(prop_ids))

        res_ids = list(map(prop_id_to_res_id, prop_ids))
        if conclusion.endswith(':N'):
            self.propositions.update(res_ids)
        else:
            self.propositions.update(res_ids)


def _combine_proofs(proofs: List[Proof]) -> Proof:
    combined_propositions = set()
    combined_arguments = set()
    for proof in proofs:
        combined_propositions = combined_propositions.union(proof.propositions)
        combined_arguments = combined_arguments.union(proof.arguments)
    return Proof(None, combined_propositions, combined_arguments)


def get_response(req: ProofRequest):
    """Respond to machine request for this machine."""
    proposition = req.proposition
    if proposition.language is not Language.INFORMAL:
        return DONT_KNOW_RESPONSE
    statement = proposition.statement
    structure = _get_statement_structure(statement, req.parse_lenient)

    if structure is None:
        return DONT_KNOW_RESPONSE
    [o1, o2, r, result_first] = structure

    response = TRUE_STUB_RESPONSE if o1+o2 == r else FALSE_STUB_RESPONSE

    if not req.fetch_updated_proposition and not req.fetch_proof:
        return response
    response = copy.deepcopy(response)
    response.resolved_proposition = string_to_proposition(
        get_id_r_e_o1po2(r, o1, o2, result_first))
    if not req.fetch_proof:
        return response
    proof = _get_proof_r_e_o1po2(r, o1, o2, result_first)
    response.proof_propositions = proof.get_propositions()
    response.proof_arguments = proof.get_arguments()
    return response


def _get_statement_structure(statement: str, parse_lenient: bool):
    matcher = SUM_SCHEMA.match(statement)
    if matcher is not None:
        return [string_to_int(matcher.group(1)),
                string_to_int(matcher.group(2)),
                string_to_int(matcher.group(3)),
                False]

    matcher = SUM_SCHEMA_RESULT_FIRST.match(statement)
    if matcher is not None:
        return [string_to_int(matcher.group(2)),
                string_to_int(matcher.group(3)),
                string_to_int(matcher.group(1)),
                True]

    if not parse_lenient:
        return None

    matcher = SUM_SCHEMA_INCOMPLETE.match(statement)
    if matcher is None:
        return None
    o1 = string_to_int(matcher.group(1))
    o2 = string_to_int(matcher.group(2))
    if o1 is None or o2 is None:
        return None

    return [o1, o2, o1+o2, False]


def _get_proof_r_e_o1po2(r: int, o1: int, o2: int, result_first: bool) -> Proof:
    """r=o1+o2 or o1+o2=r"""
    conclusion = get_id_r_e_o1po2(r, o1, o2, result_first)

    if o1 + o2 != r:
        r_correct = o1 + o2
        proof = _get_proof_r_e_o1po2(r_correct, o1, o2, result_first)
        proof.add_top_level_argument(conclusion + ":N", [proof.conclusion])
        return proof

    if not result_first:
        proof = _get_proof_r_e_o1po2(r, o1, o2, True)
        premise2 = EQUALITY_COMMUTATIVITY
        proof.add_top_level_argument(conclusion, [proof.conclusion, premise2])
        return proof

    if o1 < o2:
        proof = _get_proof_r_e_o1po2(r, o2, o1, result_first)
        premise2 = SUM_COMMUTATIVITY
        proof.add_top_level_argument(conclusion, [proof.conclusion, premise2])
        return proof

    if o2 == 1:
        return Proof(conclusion, {conclusion},
                     {get_arg_id_premise_machine(conclusion, NUMBER_MACHINE)})

    proof_prev_step = _get_proof_ap1_e_bpcp1_t1(r-1, o1, o2-1)

    proof_defn_r = _get_proof_r_e_o1po2(r, r-1, 1, True)
    proof_defn_o2 = _get_proof_r_e_o1po2(o2, o2-1, 1, True)

    combine_proof = _combine_proofs(
        [proof_prev_step, proof_defn_r, proof_defn_o2])
    combine_proof.add_top_level_argument(
        conclusion, [proof_prev_step.conclusion, proof_defn_r.conclusion, proof_defn_o2.conclusion])
    return combine_proof


def _get_proof_ap1_e_bpcp1_t1(a: int, b: int, c: int) -> Proof:
    """9 + 1 = 7 + (2 + 1)"""
    conclusion = get_id_ap1_e_bpcp1_t1(a, b, c)

    proof = _get_proof_ap1_e_bpcp1_t2(a, b, c)
    premise2 = SUM_ASSOCIATIVITY
    proof.add_top_level_argument(conclusion, [proof.conclusion, premise2])
    return proof


def _get_proof_ap1_e_bpcp1_t2(a: int, b: int, c: int) -> Proof:
    """(9 + 1) = (7 + 2) + 1"""
    conclusion = get_id_ap1_e_bpcp1_t2(a, b, c)

    proof = _get_proof_r_e_o1po2(a, b, c, True)
    premise2 = ADDITION_PROPERTY_OF_EQUALITY
    proof.add_top_level_argument(conclusion, [proof.conclusion, premise2])
    return proof
