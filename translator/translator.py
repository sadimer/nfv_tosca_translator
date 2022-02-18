import yaml
import logging
import sys
import translator.utils as utils

from toscaparser.tosca_template import ToscaTemplate
from translator.template import ToscaNormativeTemplate

VNF_DEF_PATH = '/definitions/VNF_types/'
NFV_DEF_PATH = '/definitions/NFV_definintion_1_0.yaml'
TOSCA_DEF_PATH = '/definitions/TOSCA_definition_1_0.yaml'
MAP_PATH = '/definitions/TOSCA_NFV_mapping.yaml'
PROJECT_NAME = 'nfv_tosca_translator'

def translate(template_file, validate_only):
    with open(template_file, "r") as f:
        try:
            tpl = yaml.load(f, Loader=yaml.SafeLoader)
        except yaml.scanner.ScannerError as e:
            logging.error("Error parsing TOSCA template: %s %s" % (e.problem, e.context_mark))
            sys.exit(1)
    tosca_def = utils.get_project_root_path() + TOSCA_DEF_PATH
    nfv_def = utils.get_project_root_path() + NFV_DEF_PATH
    if 'imports' in tpl:
        if isinstance(tpl['imports'], list):
            tpl['imports'].append(tosca_def)
            tpl['imports'].append(nfv_def)
        else:
            logging.error("Error parsing imports in TOSCA template")
            sys.exit(1)
    else:
        tpl['imports'] = []
        tpl['imports'].append(tosca_def)
        tpl['imports'].append(nfv_def)

    try:
        tosca_parser_tpl = ToscaTemplate(yaml_dict_tpl=tpl)
    except:
        logging.exception("Got exception from OpenStack tosca-parser")
        sys.exit(1)

    if validate_only:
        logging.info("Template successfully passed validation")
        tpl = {"template successfully passed validation": template_file}
        return tpl

    map_file = utils.get_project_root_path() + MAP_PATH
    with open(map_file, "r") as f:
        try:
            mapping = yaml.load(f, Loader=yaml.SafeLoader)
        except yaml.scanner.ScannerError as e:
            logging.error("Error parsing NFV mapping: %s %s" % (e.problem, e.context_mark))
            sys.exit(1)

    try:
        tosca_normative_tpl = ToscaNormativeTemplate(tosca_parser_tpl=tosca_parser_tpl, yaml_dict_mapping = mapping)
    except:
        logging.exception("Got exception on translating NFV to TOSCA")
        sys.exit(1)
    return tosca_normative_tpl.get_result_template()