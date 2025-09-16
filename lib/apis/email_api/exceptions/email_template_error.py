class EmailTemplateError(LookupError):
    """
    Exception which is thrown whenever there is an error with setting up email templates
    e.g. when template doesn't exist or template missing required schema values
    """
