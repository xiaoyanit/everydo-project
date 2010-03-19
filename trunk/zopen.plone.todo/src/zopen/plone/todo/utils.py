import re
urlRegexp = re.compile(r'((?:ftp|https?)://(?:[a-z0-9](?:[-a-z0-9]*[a-z0-9])?\.)+(?:com|edu|biz|org|gov|int|info|mil|net|name|museum|coop|aero|[a-z][a-z])\b(?:\d+)?(?:\/[^"\'<>()\[\]{}\s\x7f-\xff]*(?:[.,?]+[^"\'<>()\[\]{}\s\x7f-\xff]+)*)?)', re.I|re.S|re.U)

def abbreviateUrl(url, max = 60,  ellipsis = "[&hellip;]"):
        if len(url) < max:
            return url
        protocolend = url.find("//")
        if protocolend == -1:
            protocol = ""
        else:
            protocol = url[0 : protocolend+2]
            url = url[protocolend+2 : ]
        list = url.split("/")
        if len(list) < 3 or len(list[0])+len(list[-1] )>max:
            url = protocol + url
            center = (max-5)/2
            return url[:center] + ellipsis + url[-center:]
        
        return protocol + list[0] +"/" +ellipsis + "/" + list[-1]

def replaceURL(match):
    url = match.groups()[0]
    # rel="nofollow" shall avoid spamming
    return '<a href="%s" rel="nofollow">%s</a>' % (url, abbreviateUrl(url))


def transformToRichTitle(title):
    return urlRegexp.subn(replaceURL, title)[0]

