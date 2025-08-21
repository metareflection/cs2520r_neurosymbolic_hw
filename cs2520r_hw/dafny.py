import re
import requests
import json

def verify(v):
    r = requests.post("https://dafny.livecode.ch/check", data = { 'v': v })
    text = json.dumps(r.json())
    if r.status_code != 200:
        raise RuntimeError("https://dafny.livecode.ch/check is down.")
    success = "Error:" not in text
    return success, text

def example():
    return verify("""
    module FactorialModule {
        function factorial(n: nat): nat
        decreases n
        {
            if n == 0 then 1 else n * factorial(n - 1)
        }

        // Proving the above statement
        lemma factorial_is_always_positive(n: nat)
            ensures factorial(n) > 0
        {
            if n > 0 {
                factorial_is_always_positive(n - 1);
                assert n * factorial(n - 1) > 0;  // as n > 0 and factorial(n-1) > 0
            }
        }
    }
    """)

if __name__ == "__main__":
    example()