from typing import Optional

re_code_lang = "```([Dd]afny)?(.*?)```"
filter_code = make_filter_code(re_code_lang)

def step(instructions: str, code: Optional[str] = None, verify_output: Optional[str] = None, steps: int = 0, max_steps: int = 3) -> Optional[str]:
    prompt = f"""
Generate Dafny code for the following instructions:
{instructions}
"""

    if code and verify_output:
        prompt += f"""
A previously unsuccessful code code is:
```
{code}
```
The output of the verification was:
{verify_output}
"""
    
    prompt += """Enter the entire code for the instructions in a ```dafny```-guarded block of code. Do not include any other text."""
    text = generate(prompt)
    code = filter_code(text)
    success, feedback = verify(code)
    if success:
        print(f"Success! {feedback}")
        return code
    else:
        print(f"Failed! {feedback}")
        if steps < max_steps:
            return step(instructions, code, verify_output, steps + 1, max_steps)
        else:
            return None

if __name__ == "__main__":
    instructions = """
    A factorial function, and a lemma proving it is always positive.
    """
    code = step(instructions)
    print(code)
