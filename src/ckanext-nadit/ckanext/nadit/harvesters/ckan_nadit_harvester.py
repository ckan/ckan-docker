from ckanext.harvest.harvesters.ckanharvester import CKANHarvester

from .util import get_single_lang

import logging

log = logging.getLogger(__name__)

MULTI_FIELDS = [
    'display_name', 'title', 'description'
]
MULTI_FIELDS_RESOURCE = [
    'name', 'title', 'display_name', 'description'
]
MULTI_FIELDS_ORG = [
    'display_name', 'title', 'description'
]


class NaditCKANHarvester(CKANHarvester):
    def info(self):
        return {
            'name': 'nadit_ckan',
            'title': 'NADIT plugin for CKAN',
            'description': 'Harvests remote CKAN instances for use with tourismdata.ch',
            'form_config_interface': 'Text'
        }

    def modify_package_dict(self, package_dict: dict, harvest_object):
        """
        Customizes the output of harvesting

        :param package_dict: A dictionary containing processed object
        :param harvest_object: Raw data from harvester
        :return: Modified package_dict
        """
        log.debug("---modify package: [%s]---" % package_dict['id'])

        # Indicate that we have modified this dataset
        package_dict['remote_harvest'] = True

        # Convert to single strings based on language priority
        log.debug("--modify multilingual fields--")
        for fld in MULTI_FIELDS:
            if fld not in package_dict:
                continue
            package_dict[fld] = get_single_lang(package_dict[fld])

        # Additional fields
        print(harvest_object)

        log.debug("--add language")
        if 'language' in harvest_object:
            package_dict['language'] = ",".join(harvest_object['language'])
        
        log.debug("--add rights (licenses)")
        for res in harvest_object['resources']:
            package_dict['harvest_license'] = res['rights']

        log.debug("--add temporals")
        log.debug("--add spatial")
        log.debug("--add contact_points")
        

        # Rename field for CKAN standard format
        if 'description' in package_dict:
            package_dict['notes'] = package_dict.pop('description')

        log.debug("--modify multilingual organization--")
        org = package_dict['organization']
        for fld in MULTI_FIELDS_ORG:
            if fld not in org:
                continue
            org[fld] = get_single_lang(org[fld])

        log.debug("--modify multilingual resources--")
        for res in package_dict['resources']:
            for fld in MULTI_FIELDS_RESOURCE:
                if fld not in res:
                    continue
                res[fld] = get_single_lang(res[fld])

        # Remove tags, as they will be added manually
        log.debug("--clear tags--")
        package_dict['tags'] = []

        # Return modified dictionary
        return package_dict
