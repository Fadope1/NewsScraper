x = " nice"

match x:
    case "not nice":
        print("not nice")
    case "really nice":
        print("really nice")
    case _:
        print("default")