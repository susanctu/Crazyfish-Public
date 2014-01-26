class SourceRetrievalError(Exception):
    """
    This is written as a custom exception class only
    for clarity of error messages. Indicates that 
    some issue has been encountered in attempting to retrieve
    data from some source specified on the command line
    or from some source in the default list of sources to pull from.
    """
    pass
