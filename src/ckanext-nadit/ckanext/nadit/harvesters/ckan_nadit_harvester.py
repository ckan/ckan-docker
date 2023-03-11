from ckanext.harvest.harvesters.ckanharvester import CKANHarvester

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

    def modify_package_dict(self, package_dict, harvest_object):
        log.debug("---modify_package_dict---")
        log.debug("package_dict")
        log.debug(package_dict)

        # Show some love
        package_dict['remote_harvest'] = True

        # Tweak the name
        log.debug("--modify name--")
        package_dict['title'] = package_dict['title']['de']
        package_dict['display_name'] = package_dict['display_name']['de']
        package_dict['maintainer_email'] = 'info@datalets.ch'

        # Add tags
        log.debug("--modify tags--")
        package_dict['tags'].append({'name': 'nadit'})

        return package_dict
