def clean_fen(filedir):
    with open(filedir, "r") as file:
        text = file.read()
        new_text = text.replace("20", "")
        new_text = new_text.replace("%", " ")

    with open(filedir, "w") as new_file:
        new_file.write(new_text)
