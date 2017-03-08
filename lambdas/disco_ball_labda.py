import httplib, urllib

def lambda_handler(event, context):

    # https://api.particle.io/v1/devices/20002c000247343337373739/led?access_token=342b89abb8022fdc05b8e0ed53d28bac700f2ed7
    conn = httplib.HTTPSConnection("api.particle.io")
    conn.request("POST",
                 "/v1/devices/20002c000247343337373739/led?access_token=342b89abb8022fdc05b8e0ed53d28bac700f2ed7",
                 urllib.urlencode({'arg': "off"}),
                 {"Content-type": "application/x-www-form-urlencoded",
                  "Accept": "text/plain"}
                 )

    return "Success"
