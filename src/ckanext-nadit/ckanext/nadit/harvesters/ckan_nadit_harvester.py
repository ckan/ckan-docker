from ckanext.harvest.harvesters.ckanharvester import CKANHarvester

from .util import get_single_lang

import logging
log = logging.getLogger(__name__)


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
        log.debug("---modify_package_dict---")
        log.debug("package_dict")
        log.debug(package_dict)

        # Indicate that we have modified this dataset
        package_dict['remote_harvest'] = True

        # Obtain title based on language priority
        log.debug("--modify display name and title--")
        package_dict['title'] = get_single_lang(package_dict['title'])
        package_dict['display_name'] = get_single_lang(package_dict['display_name'])

        # Add tags
        log.debug("--clear tags--")
        package_dict['tags'] = []

        # Return modified dictionary
        return package_dict
