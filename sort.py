


import functools
import difflib

def main():

    def comp_reverse(n,m):
        if n < m:
            return 1
        elif m < n:
            return -1
        else:
            return 0

    text = list("asdfghjkl")
    print(f"original: {text}")

    text2 = sorted(text)
    print(f"sorted: {text2}")

    text2 = sorted(text,
                   key=functools.cmp_to_key(comp_reverse))
    print(f"reverse sorted: {text2}")

    
if __name__ == "__main__":
    main()
