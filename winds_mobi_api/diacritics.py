# coding=utf-8

diacritics = "ŠŒŽšœžŸ¥µÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýÿ"
asciis = "SOZsozYYuAAAAAAACEEEEIIIIDNOOOOOOUUUUYsaaaaaaaceeeeiiiionoooooouuuuyy"


def normalize(str):
    new_str = ""
    for char in str:
        new_char = char
        for i, diacritic in enumerate(diacritics):
            if char == diacritic:
                new_char = asciis[i]
                break
        new_str += new_char

    return new_str


def create_regexp(str):
    reg_exp = ""
    for char in str:
        found = False
        for i, ascii in enumerate(asciis):
            if char == ascii:
                if not found:
                    reg_exp += "["
                    found = True
                reg_exp += diacritics[i]

        reg_exp += char
        if found:
            reg_exp += "]"

    return reg_exp
