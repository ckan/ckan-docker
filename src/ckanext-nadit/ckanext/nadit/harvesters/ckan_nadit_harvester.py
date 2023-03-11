from ckanext.harvest.harvesters.ckanharvester import CKANHarvester


class NaditCKANHarvester(CKANHarvester):

    @staticmethod
    def modify_package_dict(package_dict, harvest_object):
        # Set a default custom field
        package_dict['remote_harvest'] = True

        # Add tags
        package_dict['tags'].append({'name': 'nadit'})

        return package_dict
