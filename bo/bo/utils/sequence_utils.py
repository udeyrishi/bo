def remove_duplicates(seq):
    """
    Returns a new list keeping only the unique elements in the original sequence. Preserves the ordering.
    http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order

    :param seq: The sequence to be processed
    :return: A list containing only the unique elements in the same order as they appeared in the original sequence.
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
