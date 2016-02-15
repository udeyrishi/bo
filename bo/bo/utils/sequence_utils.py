def remove_duplicates(seq):
    """
    Returns a new list keeping only the unique elements in the original sequence. Preserves the ordering.
    http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order

    :param seq: The sequence to be processed
    :return: A list containing only the unique elements in the same order as they appeared in the original sequence.

    >>> remove_duplicates(['hello', 'world', 'hello'])
    ['hello', 'world']

    >>> remove_duplicates(['hello', 'world'])
    ['hello', 'world']
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def break_string_sequence_to_words(seq):
    """
    Breaks a sequence containing multi-word strings into a set containing individual words.

    :param seq: The sequence containing multi-word strings
    :return: A set containing all the individual words

    >>> break_string_sequence_to_words(['hello world', 'foo bar', 'hello', 'red']) \
        == set({'hello', 'world', 'foo', 'bar', 'red'})
    True
    """
    return {word for string in seq for word in string.split()}


def conditional_count(seq, condition_func):
    return sum(1 for i in seq if condition_func(i))
