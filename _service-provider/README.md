_service-provider
=================

_Clone any service providers with their Docker files here if you want to build their container._

<br>

## datapusher

For example, if you want to build the datapusher service yourself:

Clone datapusher:

	git clone https://github.com/clementmouchet/datapusher.git


Tell the fig file to build it:

	datapusher:
  		build: _service-provider/datapusher
  		hostname: datapusher
 		domainname: localdomain
  		ports:
    		- "8800:8800"

<br>

If you do not want to build it, you can pull the image from the Docker registry. In this case, simply edit the fig file and specify the image instead of the build directory.


	datapusher:
  		image: clementmouchet/datapusher
  		hostname: datapusher
 		domainname: localdomain
  		ports:
    		- "8800:8800"
