import secrets


def generate_vanity(min_length, max_length):
    length = secrets.choice(range(min_length, max_length))
    choices = "abcdefghijklmnopqrstuvwxyz1234567890"
    vanity = ""

    for i in range(0, length):
        vanity += choices[secrets.choice(range(0, len(choices)))]
    return vanity


def generate_vanity_fixed(length):
    choices = "abcdefghijklmnopqrstuvwxyz1234567890"
    vanity = ""

    for i in range(0, length):
        vanity += choices[secrets.choice(range(0, len(choices)))]
    return vanity


def generate_unique_vanity(min_length, max_length, model):
    vanity = generate_vanity(min_length, max_length)

    if model.objects.filter(vanity=vanity).exists():
        return generate_unique_vanity(min_length, max_length, model)
    return vanity


def generate_unique_vanity_fixed(length, model):
    vanity = generate_vanity_fixed(length)

    if model.objects.filter(vanity=vanity).exists():
        return generate_unique_vanity_fixed(length, model)
    return vanity
