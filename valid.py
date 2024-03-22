import validators


def verify(url):
    isvalid = validators.url(url)
    if isvalid and ("http://" in url) or ("https://" in url):
        return True
    else:
        return False