

def generator_example(n):
    """
    Short description of `generator_example`.
    
    Args:
        n (TYPE): DESCRIPTION.
    """
    for i in range(n):
        yield i


def raises_example(x):
    """
    Short description of `raises_example`.
    
    Args:
        x (TYPE): DESCRIPTION.
    """

    if x < 0:
        raise ValueError("negative")
    return x * 2

