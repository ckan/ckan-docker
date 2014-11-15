_service-provider
=================

_Clone any service providers with their Docker files here if you want to build their container._

## datapusher

For example, if you want to build the datapusher service yourself:

Clone datapusher in `_datapusher`:

	git clone https://github.com/ckan/datapusher.git


Tell the fig file to build it:

	datapusher:
			build: _service-provider/_datapusher
			hostname: datapusher
		domainname: localdomain
			ports:
				- "8800:8800"

